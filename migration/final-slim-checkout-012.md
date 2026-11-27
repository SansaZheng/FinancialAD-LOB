# Final stage012 Mac cleanup

Verified GitHub main3212ef85202e3aa9fce55d1a3fea0ceb11634bd5, all existing file blob hashes, clean state, no local-only branches/stashes, all old remote refs, and byte equality of344retained files before atomic replacement. Omitted1279already archived current CQ input/output files. Removed the exact owned backup only after post-install SHA256 checks. Python environment and other projects/jobs untouched. Net reclaimed585953280allocated bytes; old604049408, new18096128. The prior migration reclaimed707,383,296bytes separately. These are separate snapshots, not an audited whole-disk net change.

Full data, checkpoints, predictions and logs remain on GitHub/CQ. Code, reports, CSV ledgers, figures, configs, audit receipts and data attribution remain local. Restore a job only as needed with `git sparse-checkout add results/cq-012/JOB_ID`; do not globally disable sparse checkout on a nearly full disk. All1378stage012CQarchive paths are inventoried in stage012-result-manifest.json.

中文结论：主实验和对照数据、模型的本机副本及旧Git对象已在远端核验后清理；代码、报告和可恢复的完整归档保留。
