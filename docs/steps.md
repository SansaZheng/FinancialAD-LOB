# Reproduction and execution steps

1. Read `paper/workflow/current.md`, `docs/protocol.md` and `docs/data-contract.md`.
2. Acquire permitted data on authorized server storage through CQ. Record input
   hashes, license, real stock/date identities and event labels. Do not download
   bulk files to the Mac. An old metadata inventory does not establish backup.
3. Prepare source-versioned windows inside disjoint partitions; audit causal
   features and event leakage. Freeze actual date/stock fold tables. Files in
   `configs/*.engineering-example.json` are test examples, not production splits.
4. Qualify storage and inputs using the preflight CQ job, then build a project-only
   conda runtime, run CPU/GPU smoke, and only then submit dependent experiment
   batches. Bind every batch to the pushed code SHA and input manifest hash.
5. For each fold and seed, freeze a shared label subset. Fit preprocessing on
   training samples; all supervised controls use exactly the same labels. Run
   six validation trials per current tabular control. Record compute separately.
6. Add the original-paper reference only after its data/generator/settings are
   recovered. Qualify same-input TCN and Transformer controls before claiming
   gains from the candidate. Neural training/augmentation integration is pending.
7. Score frozen tests, save predictions/checkpoints/trials and calculate paired
   stock-date uncertainty, per-domain metrics and event-level operational metrics.
8. Archive permitted outputs in GitHub. Large files use Releases/LFS with download
   and checksum receipts. For restricted data record hashes/acquisition steps
   without making raw records public. Scan for credentials before publication.
9. Fetch a remote artifact independently and compare its SHA256 to the source.
   Only verified redundant local copies may be removed. iCloud placeholders are
   not physical payloads; unlinking them can delete the cloud copy as well.
10. Update the evidence map and workflow event log. Finish reports with a Chinese
    conclusion. Distinguish engineering tests, semi-synthetic experiments, exact
    reproduction and real-world validity.

中文结论：每个实验必须从合法可核验的数据、固定代码版本和公平协议开始，结果备份核验后才进行本地清理。

## 2026-11-24: public event-data acquisition and replay

Run only bounded source probes on the Mac; full acquisition is CQ-only. Source
license/limitations: `docs/public-data.md`; attribution: `data/ATTRIBUTION.md`.
An isolated environment used Python 3.9.6, numpy 2.0.2, h5py 3.12.1. No shared
interpreter was modified. The CQ Python 3.11 environment is not yet qualified.

```bash
python3 -m venv --system-site-packages /PATH/TO/ISOLATED/data-tools-venv
/PATH/TO/ISOLATED/data-tools-venv/bin/python -m pip install --no-cache-dir --no-deps h5py==3.12.1
/PATH/TO/ISOLATED/data-tools-venv/bin/python -m scripts.probe_wselob --output results/wselob-probe-NEW --stocks KGHM PEKAO
python3 -m scripts.audit_wselob_replay results/wselob-probe-NEW
```

Default sample: 4,096 consecutive events for each of 2017-01-10/11/12; no
manipulation labels and no training. The initial combined probe failed on a
PEKAO HTTP response after successfully writing the KGHM partitions. Evidence
remains in `results/wselob-probe-20261124`. The separate successful continuation:

```bash
/PATH/TO/ISOLATED/data-tools-venv/bin/python -m scripts.probe_wselob --output results/wselob-probe-20261124-pekao --stocks PEKAO
python3 -m scripts.audit_wselob_replay results/wselob-probe-20261124
python3 -m scripts.audit_wselob_replay results/wselob-probe-20261124-pekao
CQ_OUTPUT_DIR=results/engineering/qualification-20261124 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/qualify.py
```

Never execute source notebooks or unpickle HDF attributes. The reader uses h5py
numeric compound datasets directly, validates exact HTTP Content-Range and rejects
unbounded responses. Guard behavior is tested, including cached seeks and retry
limits. Full-source checksums remain unverified until a full CQ download.

After an allowed source repository exists and CQ preflight/environment pass, the
full-data job command is (replace PROJECT with the actual authorized workspace):

```bash
python -m scripts.fetch_wselob --data-dir /data/PROJECT/wselob-v1
```

This requires CQ_OUTPUT_DIR, /date or /data backing, published size/SHA256 checks,
and free space for remaining files plus 2 GiB reserve. Existing verified sources
are reused; mismatched files and incomplete .part files are preserved for review.
The full acquisition command has **not** been executed. No raw full-data backup
or training is implied by the existence of this script.

中文结论：本次步骤可复现已完成的小样本真实数据回放；完整数据下载和正式 CQ 实验仍需先解除仓库接入限制。

## Stage 009: observation-aware controls and official CQ Kaggle route

See `docs/improvement-009.md` for feature semantics, model budgets and limitations.
The supported CQ Kaggle CPU backend accepts canonical `code.github` directly;
this does not alter the lab server's owner whitelist. The local client was updated
to 2fe77566 using `cq update`, after preserving its existing .prev backup.

Executed local validation:

```bash
CQ_OUTPUT_DIR=results/engineering/qualification-009-final OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/qualify.py
python3 -m scripts.audit_wse_features --folders results/wselob-probe-20261124 results/wselob-probe-20261124-pekao --output results/wse-feature-audit-009
```

The output folder must be fresh when rerunning the feature audit. 31 tests pass.
The feature audit reports 152 valid pairs and 3,040 unknown event-channel values.

Executed CQ chain, with pinned SHA in each spec, CPU=1, GPU=0, RAM=2 GB, $0:

```bash
cq submit cq/009-kaggle-env.json
# j-1125-32c77e: done; existing provider packages, no installs
cq submit cq/009-kaggle-smoke.json
# j-1125-951eab: depends on env; done, 31 tests and WSE feature audit passed
cq fetch j-1125-32c77e --to results/cq-009
cq fetch j-1125-951eab --to results/cq-009
cq submit cq/009-kaggle-expand.json
# j-1125-e0f1ad: depends on smoke; done; 9 added stock-day prefixes verified
cq fetch j-1125-e0f1ad --to results/cq-009
```

CPU provider versions are recorded in `results/cq-009/j-1125-32c77e/environment.json`:
Python 3.13.18, numpy 2.1.3, sklearn 1.6.1, torch 2.11.0+cpu, h5py 3.14.0.
Local and remote source SHA256 values match. Feature JSON bytes differ because
of floating-point serialization; identities/masks match exactly and numerical
max difference is 8.88e-16, below the predeclared 1e-10 tolerance.

These CQ jobs qualify code and real data semantics; they do not report scientific
manipulation AP. Each provider notebook is isolated, and no other job was changed.

中文结论：CQ 环境和测试任务已真实完成；本轮结果验证可运行性、输入语义与跨环境一致性，正式检测性能比较仍需合格标签与完整评测集。

## JFDS predecessor source recovery

The primary Zenodo API confirms CC BY 4.0 for record 11048480. Only five small
source/readme/dependency members were selectively extracted from its 192 MB ZIP
using HTTP ranges and ZIP CRC validation. No archive data or model weights were
extracted, and no original script was executed. `scripts/fetch_jfds_reference.py`
reproduces this bounded retrieval; `vendor/jfds_reference/PROVENANCE.md` and
`results/engineering/jfds-source-discovery-009.json` retain attribution and hashes.
Full archive MD5 was not verified by selective reads.

中文结论：原始前作源码已恢复并存档；完整 2025 管线复现和性能比较仍需后续实现与实验。
