"""Price-aligned causal liquidity features, with explicit visibility censoring.

Snapshot changes alone cannot distinguish execution from cancellation. Event
fields must be sourced from actual messages, never manufactured from labels.
"""
import math


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


def encode_snapshot(previous, current, messages, tick_size):
    """Return per-level [side,distance,logvolume,add,remove,cancel,execute,observed].

    messages describe only the interval ending at current['time']. Message
    timestamps after that endpoint cause an error. Price distances use current
    mid / actual tick size. Shared price encoding generalizes across price scales.
    """
    if tick_size <= 0 or current["time"] <= previous["time"]:
        raise ValueError("Invalid time or tick size")
    if min(current["ask"]) <= max(current["bid"]):
        raise ValueError("Crossed/locked book excluded by protocol")
    totals = {}
    for m in messages:
        if not previous["time"] < m["time"] <= current["time"]:
            raise ValueError("Message outside causal interval")
        if m["side"] not in ("ask", "bid") or m["volume"] < 0:
            raise ValueError("Invalid message")
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
                        float(c["observed_both"])])
    return out
