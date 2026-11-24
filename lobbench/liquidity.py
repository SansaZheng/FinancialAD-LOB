"""Price-aligned causal liquidity features, with explicit visibility censoring.

Snapshot changes alone cannot distinguish execution from cancellation. Event
fields must be sourced from actual messages, never manufactured from labels.
"""
import math

FEATURE_NAMES = ["side", "mid_distance_ticks", "log_volume", "aligned_added",
                 "aligned_removed", "cancel_volume", "execute_volume", "price_observed_both",
                 "cancel_observed", "execute_observed"]


def price_aligned_changes(previous, current):
    """Books are price->volume mappings for ONE side, bounded observed depth.

    Unseen/new prices are censored, not treated as adds or cancels. This avoids
    calling level migration a cancellation when the best quote changes.
    """
    if any(v < 0 or not math.isfinite(v) for v in list(previous.values()) + list(current.values())):
        raise ValueError("Volumes must be finite and nonnegative")
    return {p: {"added": max(v - previous[p], 0) if p in previous else 0,
                "removed": max(previous[p] - v, 0) if p in previous else 0,
                "observed_both": p in previous} for p, v in current.items()}


def encode_snapshot(previous, current, messages, tick_size, event_coverage=None):
    """Return ten channels listed in FEATURE_NAMES, with explicit event coverage.

    messages describe only the interval ending at current['time']. Message
    timestamps after that endpoint cause an error. Price distances use current
    mid / actual tick size. Coverage is a per-type boolean assertion for the
    entire interval, not inferred from having one message or an empty list.
    Missing channels are zero-filled AND flagged unobserved, never known-zero.
    """
    if tick_size <= 0 or current["time"] <= previous["time"]:
        raise ValueError("Invalid time or tick size")
    coverage = {"cancel": False, "execute": False}
    if event_coverage is not None:
        if set(event_coverage) != set(coverage) or any(type(v) is not bool for v in event_coverage.values()):
            raise ValueError("Explicit boolean coverage needed for cancel and execute")
        coverage.update(event_coverage)
    if not all(book[side] for book in (previous, current) for side in ("ask", "bid")):
        raise ValueError("Both book sides are required")
    if any(min(book["ask"]) <= max(book["bid"]) for book in (previous, current)):
        raise ValueError("Crossed/locked book excluded by protocol")
    totals = {}
    for m in messages:
        if not previous["time"] < m["time"] <= current["time"]:
            raise ValueError("Message outside causal interval")
        if m["side"] not in ("ask", "bid") or m["volume"] < 0:
            raise ValueError("Invalid message")
        if m["type"] not in coverage:
            raise ValueError("Deletion is not a verified cancellation/execution")
        if not coverage[m["type"]]:
            raise ValueError("Cannot use incomplete/unobserved event channel")
        key = (m["side"], m["price"], m["type"])
        totals[key] = totals.get(key, 0) + m["volume"]
    mid = (min(current["ask"]) + max(current["bid"])) / 2
    out = []
    for side, sign in (("ask", 1), ("bid", -1)):
        changes = price_aligned_changes(previous[side], current[side])
        scale = max(sum(previous[side].values()) / max(len(previous[side]), 1), 1)
        for price in sorted(current[side], reverse=(side == "bid")):
            c = changes[price]
            out.append([sign, sign * (price - mid) / tick_size, math.log1p(current[side][price]),
                        c["added"] / scale, c["removed"] / scale,
                        totals.get((side, price, "cancel"), 0) / scale,
                        totals.get((side, price, "execute"), 0) / scale,
                        float(c["observed_both"]), float(coverage["cancel"]), float(coverage["execute"])])
    return out
