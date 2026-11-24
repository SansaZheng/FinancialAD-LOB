import io
import unittest
from unittest.mock import patch

from lobbench.http_range import HTTPRangeFile
from lobbench.wselob import WSEBook


class Response(io.BytesIO):
    def __init__(self, body, status=206, content_range="bytes 0-3/8"):
        super().__init__(body)
        self.status = status
        self.headers = {"Content-Range": content_range}


class RangeSafety(unittest.TestCase):
    def test_ignored_range_is_rejected_before_body_read(self):
        responses = [Response(b"full-file", 200) for _ in range(3)]
        with patch("urllib.request.urlopen", side_effect=responses) as call:
            f = HTTPRangeFile("https://example.org/a", 8, 4, 4)
            with self.assertRaisesRegex(RuntimeError, "Range mismatch"):
                f.read(1)
            self.assertEqual(f.downloaded, 0)
            self.assertEqual(call.call_count, 3)
            self.assertEqual(f.range_rejections, 3)

    def test_transient_ignored_range_recovers_without_full_body(self):
        with patch("urllib.request.urlopen", side_effect=[Response(b"full", 200), Response(b"abcd")]):
            f = HTTPRangeFile("https://example.org/a", 8, 4, 4)
            self.assertEqual(f.read(4), b"abcd")
            self.assertEqual(f.downloaded, 4)
            self.assertEqual(f.range_rejections, 1)

    def test_cache_seek_and_budget(self):
        with patch("urllib.request.urlopen", return_value=Response(b"abcd")) as call:
            f = HTTPRangeFile("https://example.org/a", 8, 4, 4)
            self.assertEqual(f.read(2), b"ab")
            f.seek(-1, 1)
            self.assertEqual(f.read(3), b"bcd")
            with self.assertRaisesRegex(RuntimeError, "budget"):
                f.read(1)
            self.assertEqual(call.call_count, 1)

    def test_short_response_is_rejected(self):
        with patch("urllib.request.urlopen", return_value=Response(b"abc")):
            with self.assertRaisesRegex(RuntimeError, "Incomplete"):
                HTTPRangeFile("https://example.org/a", 8, 4, 4).read(1)


def row(action, time=1, oid=1, side=1, price=10000, volume=10, **kwargs):
    return dict(time=time, symbol_idx=10783, action_type=action, order_date=20170101,
                order_id=oid, side=side, price=price, price_level=2, volume=volume,
                order_type="2", **kwargs)


class WSEReplay(unittest.TestCase):
    def test_reset_is_required_and_unknown_reference_rejected(self):
        b = WSEBook()
        with self.assertRaisesRegex(ValueError, "reset"):
            b.apply(row("A"))
        b.apply(row("F"))
        with self.assertRaisesRegex(ValueError, "Unknown"):
            b.apply(row("D"))

    def test_price_level_aggregation_modification_deletion(self):
        b = WSEBook()
        for r in [row("F"), row("Y"), row("A", oid=2, volume=20),
                  row("A", oid=3, side=5, price=10100)]:
            b.apply(r)
        self.assertEqual(b.snapshot()["bid"], [["100.00", 30]])
        b.apply(row("M", volume=4, price=-1, side=-1))
        self.assertEqual(b.snapshot()["bid"], [["100.00", 24]])
        b.apply(row("D", oid=2))
        self.assertEqual(b.snapshot()["bid"], [["100.00", 4]])
        self.assertFalse(b.snapshot()["crossed_or_locked"])

    def test_future_reordering_and_mixed_symbol_rejected(self):
        b = WSEBook()
        b.apply(row("F", time=2))
        with self.assertRaisesRegex(ValueError, "Noncausal"):
            b.apply(row("A", time=1))
        r = row("A", time=3)
        r["symbol_idx"] = 11322
        with self.assertRaisesRegex(ValueError, "Mixed"):
            b.apply(r)

    def test_nonlimit_and_crossed_states_are_visible(self):
        b = WSEBook()
        b.apply(row("F"))
        b.apply(row("A"))
        b.apply(row("A", oid=2, side=2, price=9999))
        r = row("A", oid=3)
        r["order_type"] = "1"
        b.apply(r)
        self.assertTrue(b.snapshot()["crossed_or_locked"])
        self.assertEqual(b.snapshot()["excluded_nonlimit_or_empty_orders"], 1)
