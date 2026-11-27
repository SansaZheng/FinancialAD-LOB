012-direct-hard-negative | Codex | running | configuration7 | 2026-11-27T16:16:51.139511+00:00

Prompt:prompts/012-direct-hard-negative.md. Frozen scoringcommit45950e7701a713e61cc7b8aa7a9eb7fcb94d08f4; dataset01213ddbaf0ffc19d31d43ce4793839031c283b3ef241abc6a21b31472cc8d2d. Nine new dates/45stock-days/3,439,144rows,4,500reference snapshots,51,118benchmark windows. Stage011 negative results remain archived.

Verified16/30fold-seeds and160/300selected evaluations: date/seed0 j-1127-02f40d; PZU j-1127-30d90c,PKOBP j-1127-d720d4,PKNORLEN j-1127-f8100c,all5seeds each. Independent receipt results/engineering/direct-012/partial-16-verification.json; interim results/reports/012-partial-16. Combined summary covers only these3stocks: HGBmacroAP.5190,interactionHGB.8518,interactionHGBhard.8550,registeredinteractionMLPhard.7299. Not a final five-stock conclusion.

Still active: PEKAO j-1127-d6ea5e andKGHM j-1127-bd6422 running; date seeds1–4 j-1127-0d03c9 queued at last check. Two workers per notebook;10GBRAM/4CPUs,freeCQKaggle only. Query live states before any retry. Local fetch watcher resumed after storage migration; no CQjob was stopped or duplicated.

Secondary challenge j-1127-d406c2 is generated and verified,15,852common-ID windows/384modified controls/55collisions/1censored. Frozen-model scoring pending completion of all primary models. Models, thresholds and code remain frozen; no test-driven tuning.

Mac partial-clone migration verified523retained files byte-for-byte and alloldremote refs before replacing the old checkout;707,383,296allocated bytes net reclaimed. Full historical data remain onGitHub/CQ; git sparse-checkout add results/cq-XXX/JOB restores on demand. Paths and Pythonenvironment unchanged. Receipts migration/slim-checkout-012.*. Prior normalizer audit portability correction and allnegative findings retained. Recent primary-literature check in paper/workflow/literature.md does not count as reproduced2026baselines.

Next:finish remaining14runs, independently check30/300, score frozen models on the secondary challenge throughCQ, independently recompute, archive complete models/predictions/reports, and finish bilingual report. No original0.675orCCFAreadiness claim.

中文结论：三个已完成跨股票测试均进入独立核验汇总，增强特征加梯度提升明显优于普通基线；难负例的额外收益较小，神经模型优越性仍未得到支持。剩余实验和更难良性对照继续执行。
