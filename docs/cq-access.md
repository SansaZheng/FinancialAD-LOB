# CQ access resolution — observed 2026-11-24

Canonical repository: **SansaZheng/FinancialAD-LOB**. The GitHub connector now
reports push permission for its SuuTTT identity, and the local GitHub SSH identity
is SansaZheng. These are GitHub permissions, not CQ's source-owner policy.

After inspecting the queue, the existing project preflight was retried once.
CQ returned HTTP 400: `code.git: only repositories of SuuTTT can be cloned on
the lab servers (push yours there; got SansaZheng)`. No job ID was issued.
Evidence: `results/engineering/cq-submission-20261124.json`.
No other project's cancelled jobs were restarted, no shared policy changed,
and no paid capacity was requested.

Two supported remedies:

1. A CQ administrator allows **only SansaZheng/FinancialAD-LOB** in the applicable
   repository policy; leave unrelated scheduler settings intact.
2. The SuuTTT account owner creates an execution fork at
   [SuuTTT/FinancialAD-LOB](https://github.com/SansaZheng/FinancialAD-LOB/fork).
   Verify its source, commit identity and permissions before CQ submission.
   Continue archiving all canonical code/results in SansaZheng/FinancialAD-LOB.

The proposed mirror returned 404 during this run. `SuuTTT/FinancialAD-target`
is a different crypto project and is **not** an execution mirror. The installed
GitHub connector exposes no repository/fork creation action. Available browser
inspection did not yield a usable SuuTTT signed-in session. A concrete request
to the account owner/admin is pending; this is a missing account capability,
not a request to repeat authorization already given by the user.

After access is changed: query current project jobs to avoid duplication, pin
the pushed full commit SHA in the preflight spec, validate work-registry acceptance,
then run storage preflight. Only after successful preflight, qualify the Python
environment and run acquisition/replay as CQ jobs. Large inputs must resolve to
authorized `/date` or `/data` backing, not Mac storage or another user's home.
CPU environment -> smoke -> batch dependency order still applies. No cloud
spending until an explicit budget is supplied.

中文结论：仓库写权限已具备，但 CQ 的所有者白名单仍未放行；需要管理员精确放行或 SuuTTT 创建执行镜像，才能启动正式作业。
