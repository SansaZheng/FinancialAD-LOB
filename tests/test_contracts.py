import math
import unittest
from lobbench.protocol import split_records, audit_splits, select_labels
from lobbench.metrics import average_precision, threshold_at_fpr, paired_block_bootstrap
from lobbench.liquidity import price_aligned_changes, encode_snapshot


def record(i, stock="A", date="2026-01-01", start=0, end=1, label=0, event=None):
    return dict(id=str(i), stock=stock, date=date, source_id=stock+date,
                start=start, end=end, label=label, event_id=event, features=[1, 2])


class Contracts(unittest.TestCase):
    def test_combined_split_excludes_unseen_stock_history(self):
        rows = [record(f"{s}{d}", s, f"2026-01-0{d}") for s in ("A", "B") for d in (1, 2, 3)]
        p = split_records(rows, dict(mode="combined", train_end="2026-01-01", validation_end="2026-01-02", test_stocks=["B"]))
        self.assertEqual([r["id"] for r in p["train"]], ["A1"])
        self.assertEqual([r["id"] for r in p["test"]], ["B3"])
        self.assertEqual(len(p["unused"]), 3)

    def test_empty_cross_date_test_fails(self):
        with self.assertRaisesRegex(ValueError, "Empty"):
            split_records([record(1)], dict(mode="date", train_end="2026-01-01", validation_end="2026-01-02"))

    def test_overlapping_windows_rejected(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            audit_splits(dict(train=[record(1, start=0, end=10)], validation=[record(2, start=8, end=15)], test=[record(3, date="2026-01-02")]))

    def test_nested_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            audit_splits(dict(train=[record(1, end=100), record(2, start=1, end=2)], validation=[record(3, start=50, end=51)], test=[record(4, date="2026-01-02")]))

    def test_event_leakage_rejected(self):
        with self.assertRaisesRegex(ValueError, "Event"):
            audit_splits(dict(train=[record(1, label=1, event="e")], validation=[record(2, start=20, end=30, label=1, event="e")], test=[record(3, date="2026-01-02")]))

    def test_labels_stable_under_input_order(self):
        rows = [record(i, label=i % 2, event=str(i)) for i in range(20)]
        a, ha = select_labels(rows, 3, 5, 1)
        b, hb = select_labels(rows[::-1], 3, 5, 1)
        self.assertEqual(ha, hb)
        self.assertEqual(len(a), 8)
        self.assertEqual(sum(r["label"] for r in b), 3)

    def test_ap_ties_are_not_order_dependent(self):
        self.assertAlmostEqual(average_precision([1, 0, 1, 0], [1, 1, 0, 0]), .5)
        self.assertEqual(average_precision([0, 0], [1, 2]), None)

    def test_fpr_ties_are_conservative(self):
        t = threshold_at_fpr([0, 0, 0, 0, 1], [2, 2, 1, 0, 3], .25)
        self.assertGreater(t, 2)

    def test_block_bootstrap_requires_multiple_sessions(self):
        with self.assertRaisesRegex(ValueError, "multiple"):
            paired_block_bootstrap([record(1), record(2, label=1, event="e")], [0, 1], [0, 1], repeats=10)

    def test_shifted_levels_are_not_false_cancellations(self):
        x = price_aligned_changes({100: 10, 99: 20}, {101: 12, 100: 10})
        self.assertEqual(x[100]["removed"], 0)
        self.assertFalse(x[101]["observed_both"])
        self.assertEqual(x[101]["added"], 0)

    def test_future_messages_rejected(self):
        before = dict(time=0, ask={102: 10}, bid={100: 10})
        after = dict(time=1, ask={102: 10}, bid={100: 10})
        with self.assertRaisesRegex(ValueError, "causal"):
            encode_snapshot(before, after, [dict(time=2, side="bid", price=100, type="cancel", volume=2)], 1)

    def test_price_shift_invariant_features(self):
        a = dict(time=0, ask={102: 10}, bid={100: 10})
        b = dict(time=1, ask={102: 8}, bid={100: 10})
        c = dict(time=0, ask={202: 10}, bid={200: 10})
        d = dict(time=1, ask={202: 8}, bid={200: 10})
        self.assertEqual(encode_snapshot(a, b, [], 1), encode_snapshot(c, d, [], 1))


if __name__ == "__main__": unittest.main()
