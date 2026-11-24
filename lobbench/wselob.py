"""Conservative WSE order replay for ingestion qualification, not intent labels.

Field semantics: Marszalek (2023), WSELOB-2017 v1, order_data.ipynb,
DOI 10.17632/3g4mhdp899.1, CC BY 4.0. Independent implementation.
Only explicit limit orders enter displayed limit-depth snapshots. Missing order
references fail closed. Deletions remain 'D', never relabeled cancellations.
"""
from collections import defaultdict
from decimal import Decimal


class WSEBook:
    def __init__(self):
        self.orders = {}
        self.initialized = False
        self.symbol = None
        self.last_time = None

    def apply(self, row):
        time = int(row["time"])
        symbol = int(row["symbol_idx"])
        if self.symbol is not None and symbol != self.symbol:
            raise ValueError("Mixed instruments in one book")
        if self.last_time is not None and time < self.last_time:
            raise ValueError("Noncausal message ordering")
        self.symbol, self.last_time = symbol, time
        action = row["action_type"]
        if action == "F":
            self.orders.clear()
            self.initialized = True
            return
        if not self.initialized:
            raise ValueError("A reset and full retransmission prefix are required")
        key = (symbol, int(row["order_date"]), int(row["order_id"]))
        if action == "D":
            if key not in self.orders:
                raise ValueError("Unknown deleted order")
            del self.orders[key]
            return
        if action not in ("A", "M", "Y"):
            raise ValueError("Unsupported action")
        if action == "M" and key not in self.orders:
            raise ValueError("Unknown modified order")
        if action == "A" and key in self.orders:
            raise ValueError("Duplicate new order")
        order = dict(self.orders.get(key, {}))
        for field in ("side", "price", "price_level", "volume", "order_type"):
            value = row[field] if field == "order_type" else int(row[field])
            if str(value) != "-1":
                order[field] = value
        if set(order) != {"side", "price", "price_level", "volume", "order_type"}:
            raise ValueError("Incomplete new order")
        if order["side"] not in (1, 2, 5) or order["volume"] < 0:
            raise ValueError("Invalid order side/volume")
        self.orders[key] = order

    def snapshot(self, depth=5):
        bids, asks = defaultdict(int), defaultdict(int)
        excluded = 0
        for order in self.orders.values():
            if order["order_type"] != "2" or order["price"] <= 0 or order["volume"] == 0:
                excluded += 1
                continue
            price = Decimal(order["price"]).scaleb(-order["price_level"])
            side = bids if order["side"] == 1 else asks
            side[price] += order["volume"]
        bid = sorted(bids, reverse=True)[:depth]
        ask = sorted(asks)[:depth]
        return {"time_ns": self.last_time, "symbol_idx": self.symbol,
                "bid": [[str(p), bids[p]] for p in bid], "ask": [[str(p), asks[p]] for p in ask],
                "crossed_or_locked": bool(bid and ask and bid[0] >= ask[0]),
                "complete_depth": len(bid) == depth and len(ask) == depth,
                "excluded_nonlimit_or_empty_orders": excluded}
