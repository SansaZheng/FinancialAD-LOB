# Reproduce or inspect stage011

Canonical repository: SansaZheng/FinancialAD-LOB. The exact executed source is
`c34097d44f10ab42db7cd35b6d787ce4b055b8b8` on `codex/runtime-011`.
It preserves code/config/vendor/input blobs from canonical
`cfadd02a59ac44501dc53c044e1168994ed03b4a`, trimming only unrelated old result
files in the execution tree. See `cq/runtime-tree-011.json`. Canonical main
retains the historical archive; no scientific code was changed by packaging.

Before submitting, inspect `cq jobs --work FinancialAD-LOB` to avoid duplicate
runs. This matrix already completed. To inspect it, fetch the existing jobs:

```bash
cq fetch j-1125-41384c --to results/cq-011
cq fetch j-1125-161f04 --to results/cq-011
python3 cq/fetch-011-results.py
python3 -m scripts.verify_cascade_results \
  --root results/cq-011 \
  --dataset results/cq-011/j-1125-41384c/benchmark/benchmark.npz \
  --protocol configs/011-preregistered.json \
  --output results/engineering/cascade-011/complete-metric-verification.json
python3 -m scripts.summarize_cascade \
  --root results/cq-011 --protocol configs/011-preregistered.json \
  --output results/reports/011-complete
python3 -m scripts.plot_cascade_results \
  --report results/reports/011-complete/report.json \
  --output paper/figures/011-complete
```

The saved fetch script retrieves the stock and combined batches in bounded
fold-seed folders with three concurrent transfers and up to three attempts.
This avoids the interrupted aggregate transfer observed in this session.
It uses the installed CQ CLI at `/Users/zyy/.local/bin/cq`; adjust that executable
path on another machine. Do not infer scientific verification from fetch alone;
the independent checker must report complete_suite=true, 60 runs and660
selected evaluations. All individual artifacts have SHA256 entries in
`migration/stage011-result-manifest.json`.

The original submission specifications, rather than reconstructed commands,
are `cq/011-full-sessions.json`, `cq/011-benchmark.json`,
`cq/011-cuda-qualification.json`, `cq/011-date-style.json`,
`cq/011-stock.json`, and `cq/011-combined.json`. They pin their own exact code
revisions and complete-job dependencies. Scientific work requires CQ; local
execution is restricted to small engineering fixtures or artifact verification.
The official free Kaggle backend was used with allow_rent=false and max_usd=0.
No private server policy, paid account or other user's environment was changed.

Recorded scientific runtime: Python3.13.16, NumPy2.1.3, scikit-learn1.6.1,
PyTorch2.11.0+cu130, two TeslaT4 GPUs per notebook, one process per GPU.
All model artifacts record their own runtime versions; these take precedence
over the older local engineering requirements.txt. Thread count is1 per child,
CUDA deterministic algorithms are enabled, and CUBLAS_WORKSPACE_CONFIG is
`:4096:8`. Allocation is4 CPUs/10GB RAM; observed maximum worker RSS is
3,167,780KiB. 

Full raw days use bounded HTTP ranges and independent replay; their hash and
license manifests are stored under j-1125-8c5bef/full-sessions. Some verified
Mac working copies are intentionally removed with Git skip-worktree flags.
To restore an individual archived file:

```bash
git update-index --no-skip-worktree -- EXACT_PATH
git restore -- EXACT_PATH
```

See migration/mac-working-copy-cleanup-011-archived.json for exact paths.
The Git objects and GitHub archives remain; do not clear those flags globally
or hydrate the historical iCloud directory. Current unpublished results must
remain until a successful remote push is confirmed. The sync blocker is tracked
in paper/workflow/current.md; an existing local commit is not proof of upload.

中文结论：数据、固定配置、执行提交、作业编号、逐项预测、权重和复算步骤均可追溯；这能复现本轮 WSE 半合成实验，但不能替代原论文同数据复现。
