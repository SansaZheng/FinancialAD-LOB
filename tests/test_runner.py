import argparse
import hashlib
import json
import random
import tempfile
import unittest
from pathlib import Path
from lobbench.run import execute


class RunnerChecks(unittest.TestCase):
    def test_same_label_and_split_hash_for_four_controls(self):
        rng = random.Random(123)
        rows = []
        for stock in ("SYN_A", "SYN_B"):
            for day in (1, 2, 3):
                for i in range(24):
                    label = int(i % 4 == 0)
                    rows.append(dict(id=f"{stock}/{day}/{i}", stock=stock, date=f"2026-01-0{day}",
                        source_id="engineering-v1", start=i*2, end=i*2+1, label=label,
                        event_id=f"{stock}/{day}/{i}" if label else None,
                        features=[rng.random() + label * .3, rng.random()]))
        raw = ("\n".join(json.dumps(r) for r in rows) + "\n").encode()
        manifest = dict(sha256=hashlib.sha256(raw).hexdigest(), evidence_class="synthetic_engineering",
                        feature_names=["fixture_x", "fixture_y"], features_use_future=False,
                        generator_metadata_in_features=False, preprocessing="raw_or_window_causal")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p/"rows.jsonl").write_bytes(raw)
            (p/"manifest.json").write_text(json.dumps(manifest))
            (p/"split.json").write_text(json.dumps(dict(mode="combined", train_end="2026-01-01",
                validation_end="2026-01-02", test_stocks=["SYN_B"])))
            results = []
            for method in ("logistic", "linear_svm", "random_forest", "hist_gradient_boosting"):
                args = argparse.Namespace(input=str(p/"rows.jsonl"), manifest=str(p/"manifest.json"),
                    split=str(p/"split.json"), method=method, output=str(p/method), seed=0,
                    positive_budget=4, negative_budget=12, max_fpr=.1, allow_engineering=True,
                    commit="engineering-test-not-paper-evidence")
                execute(args)
                result = json.loads((p/method/"result.json").read_text())
                self.assertEqual(result["trial_count"], 6)
                self.assertEqual(result["evidence_class"], "synthetic_engineering")
                results.append(result)
            self.assertEqual(len({r["label_subset_hash"] for r in results}), 1)
            self.assertEqual(len({r["split_hash"] for r in results}), 1)


if __name__ == "__main__": unittest.main()
