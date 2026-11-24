# FinancialAD-LOB

Reproducible research toward robust multilevel limit-order-book manipulation
detection. Canonical archive: https://github.com/SansaZheng/FinancialAD-LOB.

**Status:** fair-evaluation infrastructure and a method prototype; original
paper reproduction and CCF A-level evidence are not complete. No claim of
matching or exceeding the source paper's 0.675 AUC-PR.

## Start here

* [Evaluation protocol](docs/protocol.md): supervision budgets, stock/date splits,
  held-out generators, metrics and falsification criteria.
* [Candidate mechanism](docs/method.md): causal price-aligned liquidity dynamics.
* [Baseline status](docs/baselines.md) and [data contract](docs/data-contract.md).
* [Public data qualification](docs/public-data.md): actual two-stock, three-date WSE event replay.
* [CQ access resolution](docs/cq-access.md): observed owner policy and supported remedies.
* [Current state](paper/workflow/current.md) and [execution prompt](paper/workflow/prompts/008-cq-access-public-data.md).
* [Legacy inventory](migration/legacy-inventory.json): metadata **not backup**.
* [Engineering checks](results/engineering/): no financial benchmark conclusions.

## Local bounded engineering checks

Use the dependencies in `requirements.txt`; Python 3.11 is the target CQ runtime.
The recorded local checks use the exact versions in
`results/engineering/local-versions.json`; remote compatibility is still to be
qualified. No environment should be installed into another user's interpreter.

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

New code, docs, small permitted outputs and provenance are committed here.
Large permitted artifacts require GitHub Releases/LFS and checksum receipts.
Raw LOBSTER redistribution rights are not assumed. The older Mac LOB data were
iCloud placeholders at inventory time (zero allocated data blocks); deleting
them would not reclaim their apparent logical size and could remove cloud copies.
Never delete sole or unverified copies, and never clean another project.

中文结论：仓库用于保存可追溯的研究过程；当前成果是可测试的协议和候选方法，不是已完成的论文复现或性能超越。
