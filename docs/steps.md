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
