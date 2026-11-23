"""Fair supervised tabular controls with validation-only model selection.

Input: JSONL window records + provenance manifest; see docs/data-contract.md.
The candidate neural model is separately qualified, not disguised as a baseline.
"""
import argparse
import hashlib
import json
import os
import platform
import time
from pathlib import Path

from .protocol import digest, select_labels, split_records
from .metrics import average_precision, summarize, threshold_at_fpr


def candidates(name, seed):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
    from sklearn.svm import LinearSVC
    if name == "logistic":
        return [(str(c), make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=2000,
                       class_weight="balanced", random_state=seed))) for c in (.001, .01, .1, 1, 10, 100)]
    if name == "linear_svm":
        return [(str(c), make_pipeline(StandardScaler(), LinearSVC(C=c, max_iter=10000,
                       class_weight="balanced", random_state=seed, dual=False))) for c in (.001, .01, .1, 1, 10, 100)]
    if name == "random_forest":
        return [(str((depth, leaf)), RandomForestClassifier(n_estimators=200, max_depth=depth,
                  min_samples_leaf=leaf, class_weight="balanced", random_state=seed, n_jobs=1))
                for depth in (4, 8, None) for leaf in (1, 5)]
    if name == "hist_gradient_boosting":
        return [(str((leaves, lr)), HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=leaves,
                  learning_rate=lr, random_state=seed, early_stopping=False))
                for leaves in (7, 15, 31) for lr in (.03, .1)]
    raise ValueError("Unimplemented method: " + name)


def score(model, x):
    return model.predict_proba(x)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(x)


def execute(args):
    import numpy as np
    import sklearn
    import joblib
    raw = Path(args.input).read_bytes()
    manifest = json.loads(Path(args.manifest).read_text())
    if hashlib.sha256(raw).hexdigest() != manifest["sha256"]:
        raise ValueError("Input hash mismatch")
    if manifest["evidence_class"] not in ("synthetic_engineering", "semi_synthetic", "real_labeled"):
        raise ValueError("Explicit evidence class required")
    if manifest["evidence_class"] == "synthetic_engineering" and not args.allow_engineering:
        raise ValueError("Engineering fixtures cannot enter scientific tables")
    if manifest.get("features_use_future") is not False or manifest.get("generator_metadata_in_features") is not False:
        raise ValueError("Causality and metadata exclusion must be audited")
    if manifest.get("preprocessing") != "raw_or_window_causal":
        raise ValueError("Global/pre-split normalization is not accepted")
    records = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    feature_count = len(manifest["feature_names"])
    if not feature_count or len(set(manifest["feature_names"])) != feature_count:
        raise ValueError("Feature schema is missing or duplicated")
    for r in records:
        x = np.asarray(r["features"], dtype=float)
        if x.shape != (feature_count,) or not np.isfinite(x).all():
            raise ValueError("Invalid feature vector")
    spec = json.loads(Path(args.split).read_text())
    parts = split_records(records, spec)
    train, budget_hash = select_labels(parts["train"], args.positive_budget, args.negative_budget, args.seed)
    val, test = parts["validation"], parts["test"]
    if set(r["label"] for r in val) != {0, 1} or set(r["label"] for r in test) != {0, 1}:
        raise ValueError("Validation and test both need positives and negatives")
    arrays = {name: (np.asarray([r["features"] for r in rows]), [r["label"] for r in rows])
              for name, rows in (("train", train), ("validation", val), ("test", test))}
    out = Path(args.output or os.environ.get("CQ_OUTPUT_DIR", ""))
    if not str(out) or str(out) == ".":
        raise ValueError("Explicit output directory required")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "result.json").exists():
        raise ValueError("Use a new output directory; completed results are immutable")
    trials, best = [], None
    for index, (params, model) in enumerate(candidates(args.method, args.seed)):
        start = time.monotonic()
        model.fit(*arrays["train"])
        predictions = score(model, arrays["validation"][0])
        ap = average_precision(arrays["validation"][1], predictions.tolist())
        trials.append({"params": params, "validation_ap": ap, "seconds": time.monotonic() - start})
        if best is None or ap > best[0]:
            best = (ap, model, params, predictions)
        with (out / "progress.txt").open("a") as f:
            f.write(f"{index+1}/7 validation trials\n")
    _, model, params, val_scores = best
    threshold = threshold_at_fpr(arrays["validation"][1], val_scores.tolist(), args.max_fpr)
    test_scores = score(model, arrays["test"][0]).tolist()  # test read only AFTER selection
    result = {"method": args.method, "seed": args.seed, "input_sha256": manifest["sha256"],
              "evidence_class": manifest["evidence_class"], "code_commit": args.commit,
              "split": spec, "split_hash": digest({k: [r["id"] for r in v] for k, v in parts.items()}),
              "label_subset_hash": budget_hash, "positive_budget": args.positive_budget,
              "negative_budget": args.negative_budget, "selected_params": params,
              "trial_count": len(trials), "validation_ap": best[0],
              "test": summarize(test, test_scores, threshold),
              "versions": {"python": platform.python_version(), "numpy": np.__version__, "sklearn": sklearn.__version__},
              "scope": "No direct comparability with paper AUC-PR 0.675; AP definition and dataset differ."}
    (out / "trials.json").write_text(json.dumps(trials, indent=2) + "\n")
    (out / "split-ids.json").write_text(json.dumps({k: [r["id"] for r in v] for k, v in parts.items()}, indent=2) + "\n")
    (out / "label-ids.json").write_text(json.dumps([r["id"] for r in train]) + "\n")
    (out / "predictions.jsonl").write_text("".join(json.dumps({"id": r["id"], "label": r["label"], "score": s}) + "\n" for r, s in zip(test, test_scores)))
    joblib.dump(model, out / "model.joblib")
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    with (out / "progress.txt").open("a") as f: f.write("7/7 complete\n")
    print(json.dumps(result))


def main():
    p = argparse.ArgumentParser()
    for key in ("input", "manifest", "split", "method", "commit"):
        p.add_argument("--" + key, required=True)
    p.add_argument("--output")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--positive-budget", type=int, default=32)
    p.add_argument("--negative-budget", type=int, default=256)
    p.add_argument("--max-fpr", type=float, default=.01)
    p.add_argument("--allow-engineering", action="store_true")
    execute(p.parse_args())


if __name__ == "__main__":
    main()
