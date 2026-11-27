# FinancialAD-LOB

Reproducible research toward robust multilevel limit-order-book manipulation
detection. Canonical archive: https://github.com/SansaZheng/FinancialAD-LOB.

**Status:** the fresh-date 11-method, 5-seed, 4-regime semi-synthetic matrix is complete and independently checked. The candidate improves over L1/rank/paper-structure adapters but loses to histogram boosting; original
paper reproduction and CCF A-level evidence are not complete. No claim of
matching or exceeding the source paper's 0.675 AUC-PR.

## Start here

* [Stage012 direct supervision protocol](paper/012-protocol.md), [frozen configuration](configs/012-preregistered.json), [execution steps](docs/reproduce-012.md), and [live report](paper/012-results.md): nine new dates/45stock-days acquired and replayed,51,118labeled windows, training-only hard negatives and strong controls; formal detector results pending. The predeclared matched-lifetime benign challenge is also generated and verified.

* [Current fresh-date protocol](paper/011-protocol.md), [dataset card](docs/dataset-011.md), and [registered eleven-method matrix](configs/011-preregistered.json).
* [Exact execution and verification steps](docs/reproduce-011.md).
* [Complete verified results](paper/011-results.md): 60 fold-seed runs / 660 evaluations, including negative findings against strong baselines.
* [Evaluation protocol](docs/protocol.md): supervision budgets, stock/date splits,
  held-out generators, metrics and falsification criteria.
* [Candidate mechanism](docs/method.md): causal price-aligned liquidity dynamics.
* [Baseline status](docs/baselines.md) and [data contract](docs/data-contract.md).
* [Public data qualification](docs/public-data.md): prefix provenance and public-source licensing.
* [Diagnostic stage010 dataset card](docs/dataset-010.md): complete-day coverage,22,206 windows, labels and source hashes.
* [Complete-day cascade protocol](paper/010-reproduction-fidelity.md): 15 complete stock-days, explicitly semi-synthetic labels, original-described cascade and one-class controls.
* [Registered stage010 suite](configs/010-preregistered.json): 10 methods, 5 seeds, date/stock/combined/style tests; planned runs are not completed results.
* [Observation-aware improvements](docs/improvement-009.md): matched causal sequence controls.
* [CQ access resolution](docs/cq-access.md): free Kaggle environment and smoke jobs completed.
* [Current state](paper/workflow/current.md) and [execution prompt](paper/workflow/prompts/012-direct-hard-negative.md).
* [Legacy inventory](migration/legacy-inventory.json): metadata **not backup**.
* [Engineering checks](results/engineering/): no financial benchmark conclusions.

## Local bounded engineering checks

Use the dependencies in `requirements.txt`; consult recorded job versions for the actual CQ runtime.
The recorded local checks use the exact versions in
`results/engineering/local-versions.json`; CQ CPU compatibility has been qualified (Python3.13.18 / PyTorch2.11.0+cpu). Stage012 CUDA qualification records Python3.13.16 / PyTorch2.11.0+cu130 / sklearn1.6.1 in results/cq-012/j-1127-fed5f1/qualification.json. No environment should be installed into another user's interpreter.

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m unittest discover -s tests -v
```

The integration test generates tiny synthetic arrays in a temporary directory,
checks identical split/label hashes across four controls, and removes temporary
artifacts. Its scores are not research results. GPU and long CPU work use CQ.

## Run a baseline through CQ after input qualification

```bash
python -m lobbench.run \
  --input /data/PROJECT/windows.jsonl \
  --manifest /data/PROJECT/windows.manifest.json \
  --split configs/split.json \
  --method logistic --seed 0 --positive-budget 32 --negative-budget 256 \
  --commit FULL_PUSHED_SHA --output "$CQ_OUTPUT_DIR"
```

Paths above are examples, not acquired inputs. Four runnable controls are
`logistic`, `linear_svm`, `random_forest`, `hist_gradient_boosting`. Each uses six
validation-only trials, saves labeled and split IDs, predictions, a checkpoint,
dependency versions and provenance. Use a fresh output directory per run.

## Archiving and Mac storage

New code, docs, permitted selected daily partitions and provenance are committed here. Stage010 daily compressed files are individually at most4.1MB (38.6MB total), not whole annual archives. Full archive verification is not claimed; selected artifacts have SHA256 receipts.
Large permitted artifacts require GitHub Releases/LFS and checksum receipts.
Earlier verified working-copy cleanup used per-file Git skip-worktree flags. On2026-11-28 Asia/Singapore, the Mac checkout was replaced with a verified partial clone and sparse checkout: historical binary blobs remain on GitHub/CQ and are now fetched on demand. Code, documentation, audit records and current required stage012 inputs/models were checked byte-for-byte before replacement. See [migration verification](migration/slim-checkout-012.md) and its JSON receipt. Restore omitted archived folders with `git sparse-checkout add results/cq-XXX/JOB`; avoid globally hydrating the archive on a nearly full disk. Raw LOBSTER redistribution rights are not assumed. The older Mac LOB data were
iCloud placeholders at inventory time (zero allocated data blocks); deleting
them would not reclaim their apparent logical size and could remove cloud copies.
Never delete sole or unverified copies, and never clean another project.

中文结论：仓库用于保存可追溯的研究过程；当前成果是可测试的协议和候选方法，不是已完成的论文复现或性能超越。
