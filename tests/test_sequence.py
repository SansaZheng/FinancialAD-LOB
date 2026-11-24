import argparse
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import torch
from lobbench.liquidity import encode_snapshot, FEATURE_NAMES
from lobbench.sequence_models import budget_model, observation_gate, parameter_count
from lobbench.sequence_run import SequenceNormalizer, execute

torch.set_num_threads(1)


def fixture(seed=1):
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(2, 8, 10, 10, generator=g)
    x[..., 7:10] = torch.randint(2, x[..., 7:10].shape, generator=g).float()
    return x


class SequenceChecks(unittest.TestCase):
    def test_unknown_events_differ_from_observed_empty_events(self):
        a = dict(time=0, ask={102: 10}, bid={100: 10})
        b = dict(time=1, ask={102: 8}, bid={100: 10})
        unknown = encode_snapshot(a, b, [], 1)
        known = encode_snapshot(a, b, [], 1, {"cancel": True, "execute": True})
        self.assertEqual(unknown[0][:8], known[0][:8])
        self.assertEqual(unknown[0][8:], [0., 0.])
        self.assertEqual(known[0][8:], [1., 1.])
        with self.assertRaisesRegex(ValueError, "Deletion"):
            encode_snapshot(a, b, [dict(time=1, side="ask", price=102, volume=2, type="D")], 1)

    def test_missing_channel_fill_cannot_change_any_model(self):
        x = fixture(); x[..., 7:10] = 0
        changed = x.clone(); changed[..., 3:7] += 1000
        for method in ("liquidity", "tcn", "transformer"):
            torch.manual_seed(0)
            model = budget_model(method, 32000).eval()
            with torch.no_grad():
                torch.testing.assert_close(model(x), model(changed))

    def test_all_models_are_causal_and_within_matched_parameter_range(self):
        x = fixture(); changed = x.clone(); changed[:, 5:, :, :7] += 100
        counts = []
        for method in ("liquidity", "tcn", "transformer"):
            torch.manual_seed(0)
            model = budget_model(method, 32000).eval(); counts.append(parameter_count(model))
            with torch.no_grad():
                torch.testing.assert_close(model(x)[:, :5], model(changed)[:, :5], atol=1e-5, rtol=1e-5)
        self.assertLessEqual(max(counts), 32000)
        self.assertGreaterEqual(min(counts)/max(counts), .9)

    def test_normalizer_ignores_missing_values_and_preserves_masks(self):
        x = fixture(); x[..., 8:10] = 0
        a = SequenceNormalizer().fit(x)
        changed = x.clone(); changed[..., 5:7] += 1000
        b = SequenceNormalizer().fit(changed)
        torch.testing.assert_close(a.mean, b.mean)
        torch.testing.assert_close(a.scale, b.scale)
        torch.testing.assert_close(a.transform(x), b.transform(changed))
        torch.testing.assert_close(a.transform(x)[..., 7:10], x[..., 7:10])

    def test_same_labels_batches_splits_and_steps_across_sequence_methods(self):
        records = []
        for stock in ("ENGINEERING_A", "ENGINEERING_B"):
            for day in (1, 2, 3):
                for i in range(8):
                    label = i % 2
                    x = fixture(seed=day*10+i)[0, :4].tolist()
                    records.append(dict(id=f"{stock}/{day}/{i}", stock=stock, date=f"2026-01-0{day}",
                        source_id="sequence-engineering", start=2*i, end=2*i+1, label=label,
                        event_id=f"{stock}/{day}/{i}" if label else None, features=[0.]*10, sequence=x))
        raw = ("\n".join(json.dumps(r) for r in records)+"\n").encode()
        manifest = dict(sha256=hashlib.sha256(raw).hexdigest(), evidence_class="synthetic_engineering",
            feature_names=FEATURE_NAMES, sequence_shape=[4, 10, 10], features_use_future=False,
            generator_metadata_in_features=False, preprocessing="raw_or_window_causal")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/"input").write_bytes(raw); (root/"manifest").write_text(json.dumps(manifest))
            (root/"split").write_text(json.dumps(dict(mode="combined", train_end="2026-01-01",
                validation_end="2026-01-02", test_stocks=["ENGINEERING_B"])))
            results = []
            for method in ("liquidity", "tcn", "transformer"):
                args = argparse.Namespace(input=str(root/"input"), manifest=str(root/"manifest"),
                    split=str(root/"split"), method=method, output=str(root/method), seed=0,
                    positive_budget=2, negative_budget=4, max_fpr=.1, allow_engineering=True,
                    commit="engineering-only", steps=2, batch_size=4, parameter_budget=32000, threads=1)
                results.append(execute(args))
            for key in ("label_subset_hash", "split_hash", "batch_schedule_hash", "normalization_fit_ids_hash"):
                self.assertEqual(len({r[key] for r in results}), 1, key)
            self.assertEqual({r["total_optimizer_steps"] for r in results}, {12})
            self.assertEqual({r["trial_count"] for r in results}, {6})
