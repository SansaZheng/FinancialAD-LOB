"""Real-prefix feature semantics audit; no labels, fitting, or performance scores."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from lobbench.liquidity import FEATURE_NAMES, encode_snapshot


def book(snapshot, shift=0., multiplier=1.):
    return {"time": snapshot["time_ns"], **{side: {(float(p)+shift)*multiplier: v for p, v in snapshot[side]}
                                             for side in ("ask", "bid")}}


def audit(folders, output):
    output.mkdir(parents=True, exist_ok=False)
    summary = {"evidence_class": "real_unlabeled_feature_audit", "feature_names": FEATURE_NAMES,
               "price_distance_unit": "1 PLN diagnostic scale, not a verified exchange tick size",
               "inputs": [], "partitions": [], "performance_metrics": None}
    features = []
    for folder in folders:
        manifest = json.loads((folder/"replay-audit.json").read_text())
        for item in manifest["partitions"]:
            path = folder/f"{item['stock']}-{item['date']}-snapshots.json"
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            if sha != item["snapshots_sha256"]:
                raise ValueError("Replay source hash mismatch")
            summary["inputs"].append({"path": str(path), "sha256": sha})
            snapshots = json.loads(path.read_text())
            valid = skipped_cross = skipped_time = 0
            max_shift = max_unit = 0.
            for previous, current in zip(snapshots, snapshots[1:]):
                if previous["crossed_or_locked"] or current["crossed_or_locked"]:
                    skipped_cross += 1
                    continue
                if current["time_ns"] <= previous["time_ns"]:
                    skipped_time += 1
                    continue
                x = np.asarray(encode_snapshot(book(previous), book(current), [], 1.))
                shifted = np.asarray(encode_snapshot(book(previous, shift=100), book(current, shift=100), [], 1.))
                units = np.asarray(encode_snapshot(book(previous, multiplier=100), book(current, multiplier=100), [], 100.))
                if not np.isfinite(x).all() or np.any(x[:, 8:10]):
                    raise ValueError("Unknown event channels must stay unobserved")
                max_shift = max(max_shift, float(np.max(np.abs(x-shifted))))
                max_unit = max(max_unit, float(np.max(np.abs(x-units))))
                np.testing.assert_allclose(x, shifted, atol=1e-10, rtol=0)
                np.testing.assert_allclose(x, units, atol=1e-10, rtol=0)
                valid += 1
                features.append({"stock": item["stock"], "date": item["date"],
                                 "start_ns": previous["time_ns"], "end_ns": current["time_ns"],
                                 "label": None, "tokens": x.tolist()})
            summary["partitions"].append({"stock": item["stock"], "date": item["date"],
                "valid_adjacent_pairs": valid, "excluded_crossed_endpoint_pairs": skipped_cross,
                "excluded_equal_or_backward_time_pairs": skipped_time,
                "translation_max_abs_error": max_shift, "currency_unit_max_abs_error": max_unit})
    summary["valid_pairs"] = len(features)
    summary["tokens"] = sum(len(r["tokens"]) for r in features)
    summary["unknown_event_channel_values"] = 2*summary["tokens"]
    summary["verified_zero_event_channel_values"] = 0
    dest = output/"features.jsonl"
    dest.write_text("".join(json.dumps(r)+"\n" for r in features))
    summary["features_sha256"] = hashlib.sha256(dest.read_bytes()).hexdigest()
    (output/"audit.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("inputs", "partitions")}, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--folders", type=Path, nargs="+", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    audit(args.folders, args.output)
