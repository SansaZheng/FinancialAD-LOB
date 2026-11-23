# CQ execution status

Canonical work label: `FinancialAD-LOB`. Its registry acceptance is not yet
verified because the repository-owner check failed first.

`preflight.json` pins pushed commit
`f0910311eb1771209369705fdba9976e94ff0515`. The attempted submission uses 1 CPU,
1 GB RAM, no GPU, 0.1 hours, one attempt, lab-only placement, and no rental.
Its storage guard requires authorized `/date` or `/data` backing storage and at
least 60 GiB free. `home.from=c224` is selected because the CQ workflow documents
that server's local `/date` disk; actual placement and storage still require the
preflight check. No runtime has qualified this assumption.

Actual server response on 2026-11-23:

```
HTTP 400 code.git: only repositories of SuuTTT can be cloned on the lab servers
(push yours there; got SansaZheng)
```

No job ID was returned. Evidence is saved in
`results/engineering/cq-submission.json`. This is a server policy rejection,
not a GPU-capacity failure. Do not patch the allowlist, mislabel the project,
inject code into another project's job, or fall back to manual SSH execution.

The administrator must allow `SansaZheng/FinancialAD-LOB` or provide an authorized
mirror. Preserve the canonical archive in the user-specified repository. If an
authorized mirror is used, record source and mirror commit equivalence.

After access is resolved:

1. Query `cq jobs --work FinancialAD-LOB` and verify duplicates/partial submissions.
2. Submit `cq/preflight.json` with the approved pinned source.
3. Read the resulting preflight report; resolve storage/input issues before builds.
4. Prepare a project-only conda env build dependent on preflight. Declare disk,
   memory and time; do not use another user's runtime as a writable environment.
5. CPU tests, GPU smoke and real-data qualification follow the environment build.
6. Frozen protocol batches depend on smoke and data qualification. CPU/VRAM
   reservations must use measured peaks; no bulk blind submission.

The remaining specs are deliberately not queued with invented input hashes,
dependencies, measurements or data paths. No paid Colab/Vast budget is authorized.

中文结论：CQ 已实际尝试提交，但被仓库所有者限制拒绝；必须解决接入限制后才能启动实验，不能声称任务已运行。
