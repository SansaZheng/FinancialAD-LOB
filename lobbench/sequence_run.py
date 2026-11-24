"""Supervised sequence controls with fixed budgets and validation-only selection.

Non-engineering runs require CQ. No automatic conversion of unlabeled WSE data
into negatives; no generic Transformer is labeled as original-paper reproduction.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import time

import numpy as np
import torch
from torch.nn import functional as F

from .liquidity import FEATURE_NAMES
from .metrics import average_precision, summarize, threshold_at_fpr
from .protocol import digest, select_labels, split_records
from .sequence_models import budget_model, observation_gate, parameter_count


class SequenceNormalizer:
    """Training-only channel moments; absent values never contribute to moments."""
    def fit(self, x):
        x = observation_gate(x)
        self.mean = torch.zeros(10, dtype=x.dtype)
        self.scale = torch.ones(10, dtype=x.dtype)
        for channel in range(7):
            valid = torch.ones_like(x[..., channel], dtype=torch.bool)
            if channel in (3, 4):
                valid = x[..., 7].bool()
            elif channel in (5, 6):
                valid = x[..., channel+3].bool()
            values = x[..., channel][valid]
            if len(values):
                self.mean[channel] = values.mean()
                self.scale[channel] = values.std(unbiased=False).clamp_min(1e-6)
        return self

    def transform(self, x):
        y = (observation_gate(x) - self.mean) / self.scale
        return observation_gate(y)  # mean=0, scale=1 for all binary masks


def probabilities(model, x, batch_size):
    model.eval()
    scores = []
    with torch.no_grad():
        for start in range(0, len(x), batch_size):
            scores.extend(model(x[start:start+batch_size].to(next(model.parameters()).device))[:, -1].sigmoid().cpu().tolist())
    return scores


def execute(args):
    device = getattr(args, "device", "cpu")
    if device not in ("cpu", "cuda") or (device == "cuda" and not torch.cuda.is_available()):
        raise ValueError("Requested device is unavailable")
    if device == "cuda":
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    if args.steps < 1 or args.batch_size < 1 or args.parameter_budget < 1 or args.threads < 1:
        raise ValueError("Training budgets must be positive")
    if not 0 < args.max_fpr < 1:
        raise ValueError("FPR target must be between zero and one")
    raw = Path(args.input).read_bytes()
    manifest = json.loads(Path(args.manifest).read_text())
    if hashlib.sha256(raw).hexdigest() != manifest["sha256"]:
        raise ValueError("Input hash mismatch")
    evidence = manifest["evidence_class"]
    if evidence not in ("synthetic_engineering", "semi_synthetic", "real_labeled"):
        raise ValueError("Unlabeled inputs cannot be trained as confirmed normal/anomalous")
    if evidence == "synthetic_engineering":
        if not args.allow_engineering:
            raise ValueError("Engineering fixtures require explicit opt-in")
        if not os.environ.get("CQ_OUTPUT_DIR") and (args.steps > 20 or len(raw) > 10*1024**2):
            raise ValueError("Only bounded engineering smoke runs are allowed locally")
    elif not os.environ.get("CQ_OUTPUT_DIR"):
        raise ValueError("Scientific sequence training requires CQ")
    if (manifest.get("features_use_future") is not False or
        manifest.get("generator_metadata_in_features") is not False or
        manifest.get("preprocessing") != "raw_or_window_causal"):
        raise ValueError("Audited causal preprocessing declarations required")
    if manifest.get("feature_names") != FEATURE_NAMES:
        raise ValueError("Observation-aware v2 schema required")
    shape = manifest["sequence_shape"]
    if len(shape) != 3 or shape[-1] != 10 or any(type(n) is not int or n < 1 for n in shape):
        raise ValueError("Invalid sequence shape")
    records = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    for r in records:
        sequence = np.asarray(r["sequence"], dtype=np.float32)
        if sequence.shape != tuple(shape) or not np.isfinite(sequence).all():
            raise ValueError("Malformed sequence")
        observation_gate(torch.from_numpy(sequence))
    split = json.loads(Path(args.split).read_text())
    parts = split_records(records, split)
    train, label_hash = select_labels(parts["train"], args.positive_budget, args.negative_budget, args.seed)
    val, test = parts["validation"], parts["test"]
    for rows in (val, test):
        if {r["label"] for r in rows} != {0, 1}:
            raise ValueError("Both validation and test require both classes")
    tensors = {name: torch.tensor([r["sequence"] for r in rows], dtype=torch.float32)
               for name, rows in (("train", train), ("validation", val), ("test", test))}
    normalizer = SequenceNormalizer().fit(tensors["train"])
    tensors = {k: normalizer.transform(x) for k, x in tensors.items()}
    y = torch.tensor([r["label"] for r in train], dtype=torch.float32)
    val_y = [r["label"] for r in val]
    out = Path(args.output or os.environ.get("CQ_OUTPUT_DIR", ""))
    if str(out) == "." or (out.exists() and any(out.iterdir())):
        raise ValueError("A new or empty output directory is required")
    out.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    # Fixed schedule shared across methods/trials; no early stopping or test tuning.
    generator = torch.Generator().manual_seed(args.seed)
    batches = torch.randint(len(train), (args.steps, args.batch_size), generator=generator)
    trials, best = [], None
    for learning_rate in (1e-4, 3e-4, 1e-3):
        for decay in (0., 1e-3):
            torch.manual_seed(args.seed)
            model = budget_model(args.method, args.parameter_budget, levels=shape[1]).to(device)
            optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=decay)
            pos_weight = torch.tensor(args.negative_budget / args.positive_budget, device=device)
            start = time.monotonic()
            model.train()
            for batch in batches:
                optimizer.zero_grad(set_to_none=True)
                loss = F.binary_cross_entropy_with_logits(model(tensors["train"][batch].to(device))[:, -1],
                                                           y[batch].to(device), pos_weight=pos_weight)
                if not torch.isfinite(loss):
                    raise RuntimeError("Nonfinite training loss")
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
                optimizer.step()
            val_scores = probabilities(model, tensors["validation"], args.batch_size)
            ap = average_precision(val_y, val_scores)
            params = {"learning_rate": learning_rate, "weight_decay": decay}
            trials.append({**params, "validation_ap": ap, "steps": args.steps,
                           "seconds": time.monotonic()-start, "last_loss": float(loss.detach())})
            if best is None or ap > best["ap"]:
                best = {"ap": ap, "model": model, "params": params, "validation_scores": val_scores}
            (out/"progress.txt").write_text(f"{len(trials)}/7 validation trials\n")
            (out/"trials.json").write_text(json.dumps(trials, indent=2)+"\n")
    model = best["model"]
    threshold = threshold_at_fpr(val_y, best["validation_scores"], args.max_fpr)
    scores = probabilities(model, tensors["test"], args.batch_size)
    split_hash = digest({k: [r["id"] for r in rows] for k, rows in parts.items()})
    result = {"method": args.method, "evidence_class": evidence, "code_commit": args.commit, "device": device,
              "input_sha256": manifest["sha256"], "seed": args.seed, "split": split,
              "split_hash": split_hash, "label_subset_hash": label_hash,
              "batch_schedule_hash": digest(batches.tolist()), "positive_budget": args.positive_budget,
              "negative_budget": args.negative_budget, "trial_count": len(trials), "steps_per_trial": args.steps,
              "total_optimizer_steps": len(trials)*args.steps, "batch_size": args.batch_size,
              "parameter_budget": args.parameter_budget, "parameters": parameter_count(model), "width": model.width,
              "feature_names": FEATURE_NAMES, "sequence_shape": shape, "validation_ap": best["ap"],
              "selected_params": best["params"], "threshold_source": "validation_negatives_only",
              "test": summarize(test, scores, threshold), "normalization_fit_ids_hash": label_hash,
              "versions": {"python": platform.python_version(), "numpy": np.__version__, "torch": torch.__version__},
              "scope": "Generic supervised controls; not Lin-Yang cascaded contrastive reproduction; no paper-score comparability."}
    (out/"split-ids.json").write_text(json.dumps({k: [r["id"] for r in v] for k, v in parts.items()}, indent=2)+"\n")
    (out/"label-ids.json").write_text(json.dumps([r["id"] for r in train])+"\n")
    (out/"normalizer.json").write_text(json.dumps({"mean": normalizer.mean.tolist(), "scale": normalizer.scale.tolist()}, indent=2)+"\n")
    (out/"predictions.jsonl").write_text("".join(json.dumps({"id": r["id"], "label": r["label"], "score": s})+"\n" for r, s in zip(test, scores)))
    torch.save({"state_dict": model.state_dict(), "method": args.method, "width": model.width,
                "levels": shape[1], "channels": shape[2]}, out/"model.pt")
    (out/"result.json").write_text(json.dumps(result, indent=2)+"\n")
    (out/"progress.txt").write_text("7/7 complete\n")
    return result


def main():
    p = argparse.ArgumentParser()
    for key in ("input", "manifest", "split", "commit"):
        p.add_argument("--"+key, required=True)
    p.add_argument("--method", required=True, choices=["liquidity", "tcn", "transformer"])
    p.add_argument("--output")
    p.add_argument("--steps", type=int, default=1000)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--parameter-budget", type=int, default=32000)
    p.add_argument("--threads", type=int, default=1)
    p.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--positive-budget", type=int, default=32)
    p.add_argument("--negative-budget", type=int, default=256)
    p.add_argument("--max-fpr", type=float, default=.01)
    p.add_argument("--allow-engineering", action="store_true")
    print(json.dumps(execute(p.parse_args())))


if __name__ == "__main__":
    main()
