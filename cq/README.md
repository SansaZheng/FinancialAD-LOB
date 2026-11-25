# CQ execution

Canonical work label `FinancialAD-LOB` is accepted. On 2026-11-25 the official
free Kaggle backend successfully cloned the user-authorized canonical repository
`SansaZheng/FinancialAD-LOB` and completed environment, CPU smoke and public-data
jobs. See [access evidence](../docs/cq-access.md). The older lab-only rejection
(`SuuTTT` owner allowlist) remains in force for that backend; it was not bypassed.

Use `cq jobs --work FinancialAD-LOB` before every submission. Pinned specs in this
directory use `placement.target=kaggle`, `allow_rent=false`, `max_usd=0`, and
explicit completed-job dependencies. No Vast/cloud spending cap has been agreed.
Never restart or cancel another project's jobs. The shared Kaggle notebook limit
is two, and GPU quota is shared across projects.

Completed stage009 jobs: environment `j-1125-32c77e`, CPU smoke `j-1125-951eab`,
three-stock public-prefix expansion `j-1125-e0f1ad`.
Stage010 complete-session acquisition: `j-1125-5d4369`.
Stage010 CUDA environment and eight-method engineering smoke: `j-1125-c8115a`.
Check live state; a listed job is not evidence of completion.

The provider's isolated `CQ_OUTPUT_DIR` is ephemeral scratch, not a shared lab
root filesystem. Declared job disk limits and the500MB CQ retrieval cap bound the
artifacts; whole1.3GB source archives are never downloaded to the Mac. Authorized
lab storage remains `/date` or `/data` if that backend later becomes available.
Code and inputs are uploaded by CQ as private provider datasets. Scientific runs
pin code commits and receive fixed, hash-verified public input artifacts.

```bash
cq submit cq/010-full-sessions.json
cq show JOB_ID
cq logs JOB_ID
cq fetch JOB_ID --path full-sessions/audit.json --to results/cq-010
```

After data/environment qualification, run the registered cascade suite in staged
batches with measured memory/time reservations. Save checkpoints, split IDs,
validation trials, test predictions, provenance and negative findings. Do not
classify engineering-fixture scores as scientific results.

中文结论：CQ 已通过官方免费 Kaggle 后端实际运行；实验按数据验证、环境验证、正式批次顺序推进，保留原有服务器策略和其他项目作业。
