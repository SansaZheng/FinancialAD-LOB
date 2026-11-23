"""Threshold-independent metrics and validation-only alarm calibration."""
import math
import random
from collections import defaultdict


def _check(y, scores):
    if not y or len(y) != len(scores) or any(v not in (0, 1) for v in y):
        raise ValueError("Invalid labels/scores")
    if any(not math.isfinite(float(v)) for v in scores):
        raise ValueError("Nonfinite score")


def average_precision(y, scores):
    """Step AP with tie groups (not trapezoidal PR AUC)."""
    _check(y, scores)
    positives = sum(y)
    if not positives:
        return None
    groups = defaultdict(list)
    for label, score in zip(y, scores):
        groups[float(score)].append(label)
    tp = total = 0
    ap = 0.0
    for score in sorted(groups, reverse=True):
        labels = groups[score]
        added = sum(labels)
        tp += added
        total += len(labels)
        ap += added / positives * tp / total
    return ap


def threshold_at_fpr(y, scores, max_fpr):
    """Conservative tie-aware calibration using validation negatives only."""
    _check(y, scores)
    if not 0 <= max_fpr < 1:
        raise ValueError("FPR must be in [0, 1)")
    negatives = sorted((s for l, s in zip(y, scores) if l == 0), reverse=True)
    if not negatives:
        raise ValueError("Validation has no negatives")
    allowed = math.floor(max_fpr * len(negatives))
    return math.nextafter(float(negatives[allowed]), math.inf)


def summarize(records, scores, threshold):
    y = [r["label"] for r in records]
    _check(y, scores)
    predicted = [s >= threshold for s in scores]
    tp = sum(p and l for p, l in zip(predicted, y))
    fp = sum(p and not l for p, l in zip(predicted, y))
    positive = sum(y)
    negative = len(y) - positive
    events = defaultdict(list)
    event_intervals = {}
    intervals_complete = True
    for r, s in zip(records, scores):
        if r["label"]:
            key = (r["source_id"], r["event_id"])
            events[key].append((r["end"], s >= threshold))
            if "event_start" not in r or "event_end" not in r:
                intervals_complete = False
            else:
                interval = (r["event_start"], r["event_end"])
                if any(not math.isfinite(v) for v in interval) or interval[0] > interval[1]:
                    raise ValueError("Invalid event interval")
                if key in event_intervals and event_intervals[key] != interval:
                    raise ValueError("Inconsistent event interval")
                event_intervals[key] = interval
    # An alarm is observable only at window END; never backdate to window start.
    hit_events = sum(any(hit for _, hit in rows) for rows in events.values())
    timely_hits = sum(any(hit and event_intervals[key][0] <= t <= event_intervals[key][1]
                         for t, hit in rows) for key, rows in events.items()) if intervals_complete else None
    return {"average_precision": average_precision(y, scores), "prevalence": positive / len(y),
            "window_precision": tp / (tp + fp) if tp + fp else 0.0,
            "window_recall": tp / positive if positive else None,
            "window_fpr": fp / negative if negative else None,
            "window_covered_event_recall": hit_events / len(events) if events else None,
            "event_recall": timely_hits / len(events) if events and timely_hits is not None else None,
            "event_count": len(events), "threshold": threshold,
            "note": "Window FPR is not alarms/hour. Covered-event recall is a proxy; timely event recall requires authoritative event intervals."}


def paired_block_bootstrap(records, scores_a, scores_b, repeats=2000, seed=0):
    """Resample whole stock-date sessions; paired samples, never independent windows."""
    if len(records) != len(scores_a) or len(records) != len(scores_b):
        raise ValueError("Length mismatch")
    blocks = defaultdict(list)
    for i, r in enumerate(records):
        blocks[(r["stock"], r["date"])].append(i)
    if len(blocks) < 2:
        raise ValueError("Need multiple independent stock-date blocks")
    rng = random.Random(seed)
    keys = sorted(blocks)
    diffs = []
    for _ in range(repeats):
        idx = [i for _ in keys for i in blocks[rng.choice(keys)]]
        y = [records[i]["label"] for i in idx]
        a = average_precision(y, [scores_a[i] for i in idx])
        b = average_precision(y, [scores_b[i] for i in idx])
        if a is not None and b is not None:
            diffs.append(b - a)
    if not diffs:
        raise ValueError("No bootstrap replicate contains positives")
    diffs.sort()
    return {"low": diffs[int(.025 * (len(diffs) - 1))],
            "high": diffs[int(.975 * (len(diffs) - 1))], "valid_repeats": len(diffs),
            "blocks": len(keys), "unit": "stock-date", "difference": "b minus a"}
