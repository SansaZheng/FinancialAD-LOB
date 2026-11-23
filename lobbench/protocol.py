"""Split and supervision contracts. Never split overlapping windows at random."""
import datetime as dt
import hashlib
import json
import math
from collections import defaultdict


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_records(records):
    seen = set()
    for r in records:
        required = ("id", "stock", "date", "source_id", "start", "end", "label", "event_id", "features")
        if any(k not in r for k in required):
            raise ValueError("Missing record fields")
        if r["id"] in seen:
            raise ValueError("Duplicate sample ID")
        seen.add(r["id"])
        dt.date.fromisoformat(r["date"])
        if (not r["stock"] or not r["source_id"] or
                not all(isinstance(r[k], (int, float)) and math.isfinite(r[k]) for k in ("start", "end")) or
                r["start"] > r["end"]):
            raise ValueError("Invalid identity or interval")
        if r["label"] not in (0, 1):
            raise ValueError("Binary labels required")
        if r["label"] and not r["event_id"]:
            raise ValueError("Every anomaly needs an event ID")
    if not records:
        raise ValueError("No samples")


def split_records(records, spec):
    """Explicit held-out stocks and chronological sessions, selected before fitting.

    combined: seen stocks before cutoffs train/validate; unseen stocks after
    validation cutoff test. Unused records remain unused, never reassigned.
    stock: disjoint stock groups, common date range permitted.
    date: all stocks, disjoint chronological date ranges.
    """
    validate_records(records)
    mode = spec["mode"]
    if mode not in ("date", "stock", "combined"):
        raise ValueError("Unknown split mode")
    train_end, val_end = spec["train_end"], spec["validation_end"]
    dt.date.fromisoformat(train_end)
    dt.date.fromisoformat(val_end)
    if train_end >= val_end:
        raise ValueError("Train cutoff must precede validation cutoff")
    test_stocks = set(spec.get("test_stocks", []))
    val_stocks = set(spec.get("validation_stocks", []))
    if mode != "date" and not test_stocks:
        raise ValueError("Explicit held-out stock required")
    if val_stocks & test_stocks:
        raise ValueError("Validation and test stocks overlap")
    if mode == "stock" and not val_stocks:
        raise ValueError("Stock split needs disjoint validation stocks")
    parts = {k: [] for k in ("train", "validation", "test", "unused")}
    for r in records:
        date, stock = r["date"], r["stock"]
        if mode == "stock":
            part = "test" if stock in test_stocks else "validation" if stock in val_stocks else "train"
        elif mode == "date":
            part = "train" if date <= train_end else "validation" if date <= val_end else "test"
        elif stock in test_stocks:
            part = "test" if date > val_end else "unused"
        elif date <= train_end:
            part = "train"
        elif date <= val_end:
            part = "validation"
        else:
            part = "unused"
        parts[part].append(r)
    audit_splits(parts, embargo=spec.get("embargo", 0))
    return parts


def audit_splits(parts, embargo=0):
    if embargo < 0:
        raise ValueError("Negative embargo")
    ids, events = {}, {}
    intervals = defaultdict(list)
    for part in ("train", "validation", "test"):
        if not parts[part]:
            raise ValueError("Empty " + part + " split")
        for r in parts[part]:
            if r["id"] in ids:
                raise ValueError("Sample leakage")
            ids[r["id"]] = part
            if r["event_id"]:
                # Event IDs must be unique within a source; episodes cannot straddle splits.
                event = (r["source_id"], r["event_id"])
                if event in events and events[event] != part:
                    raise ValueError("Event leakage")
                events[event] = part
            intervals[(r["source_id"], r["stock"], r["date"])].append((r["start"], r["end"], part))
    for group in intervals.values():
        # Keep the furthest endpoint in each partition: handles nested windows.
        last_end = {}
        for start, end, part in sorted(group):
            if any(start <= previous + embargo for other, previous in last_end.items() if other != part):
                raise ValueError("Window overlap / embargo violation")
            last_end[part] = max(end, last_end.get(part, end))


def select_labels(train, positive_budget, negative_budget, seed):
    """One common labeled subset for ALL supervised methods. Hidden labels unused."""
    if positive_budget < 1 or negative_budget < 1:
        raise ValueError("Positive and negative label budgets must be positive")
    chosen = []
    for label, budget in ((0, negative_budget), (1, positive_budget)):
        candidates = [r for r in train if r["label"] == label]
        if len(candidates) < budget:
            raise ValueError("Insufficient labeled samples for declared budget")
        candidates.sort(key=lambda r: digest([seed, r["id"]]))
        chosen.extend(candidates[:budget])
    chosen.sort(key=lambda r: r["id"])
    return chosen, digest([r["id"] for r in chosen])
