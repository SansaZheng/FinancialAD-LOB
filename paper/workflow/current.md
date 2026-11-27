012-direct-hard-negative | Codex | running | configuration7 | 2026-11-27T15:00:30.034283+00:00

Task:prompts/012-direct-hard-negative.md. Canonical repository synchronized through7b66d5a before this update. Stage011 complete negative findings remain unchanged and archived. Nine new dates/45stock-days/3,439,144rows independently replayed;4,500snapshot checks. Primary benchmark51,118windows (2,539positives/2,459benign), SHA01213ddbaf0ffc19d31d43ce4793839031c283b3ef241abc6a21b31472cc8d2d.

Completed and independently verified:6/30fold-seeds,60/300selected evaluations. Pilot j-1127-02f40d plus combined-PZU j-1127-30d90c. Pilot:60trials. Independent split/weight/selection/prediction/metric verification passed. Actual1684.226s,3,219,624KiB peakRSS,78,422,528GPUbytes; no training warnings. Cross-platform regenerated float32 interaction statistics differ at1e-9 absolute; independently diagnosed and checker tolerance corrected only for those features, with tamper rejection tests. Core training code/config unchanged.

Single-seed macro stock-day AP: HGB.5364, interactionHGB.8624, interactionHGBhard.8696, interactionMLP.7516, registered interactionMLPhard.7441. Benign FPR HGB.1964 vs interactionHGBhard.1664. This is partial evidence, not a completed superiority claim. OOF-mined hard negatives contain48.03%benign controls versus4.87%among training negatives; metadata was joined only after fitting.

Originally remaining29fold-seeds submitted in six batches; PZU completed,24remain, all scoringcommit45950e7701a713e61cc7b8aa7a9eb7fcb94d08f4: j-1127-0d03c9, j-1127-bd6422, j-1127-d6ea5e, j-1127-f8100c, j-1127-d720d4, j-1127-30d90c. Two workers/10GBRAM/4CPUs per job; date2h, combined2.5h caps based on measured pilot; free backend only. CQ receipts cq/012-batch-submissions.json. Query live states before resubmitting anything.

PZU held-out stock/date result, five seeds: HGBmacroAP.5066, interactionHGBhard.8742, registeredinteractionMLPhard.6973. BenignFPR.1346/.1442/.1346 respectively: AP improves but benign-FPR does not improve uniformly. Audit results/engineering/direct-012/partial-06-verification.json; interim report results/reports/012-partial-06. Other stock folds are not represented yet.

Secondary challenge j-1127-d406c2 completed/verified/archived:15,852common-ID windows,384modified controls,55retained collisions,1censored; all15,468other inputs unchanged. Frozen-model challenge scores still pending primary model completion. Next: fetch/check all30runs, aggregate paired results, evaluate frozen secondary controls throughCQ, archive all artifacts and update final conclusions.

中文结论：单种子交互特征加梯度提升取得明显增益，但神经候选仍逊于同特征强基线；正在运行其余29组固定实验，完整多种子与更难良性对照结论尚未形成。
