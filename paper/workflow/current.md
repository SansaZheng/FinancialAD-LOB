012-direct-hard-negative | Codex | completed | configuration 7 | 2026-11-27T18:33:17.878805+00:00

Prompt: prompts/012-direct-hard-negative.md. Route: lob-direct-hard-negative-v3. Quality aspiration: CCF A; specific venue unset. All requested stage012 experiments, independent checks, reports and archive are complete. No project CQ jobs are queued or running as of the final query.

Data: nine additional dates, five stocks, 45 daily partitions, 3,439,144 replayed source rows, 4,500 checked reference snapshots; 51,118 primary windows. Training/validation/test each use three disjoint dates. Across stages, 15 source dates are covered; the 20-date planning target remains unmet.

Primary: 30 fold-seeds / 300 selected-method evaluations verified. Source commit45950e7701a713e61cc7b8aa7a9eb7fcb94d08f4. Macro stock-day AP, held-out dates / dates plus stocks: ordinary HGB0.5513/0.5275; enhanced HGB+hard0.8611/0.8583; registered neural candidate0.7613/0.7157. The feature bundle helps; hard weighting gains are small/mixed and neural superiority is unsupported.

Secondary: 30 frozen fold-seeds / 300 paired evaluations verified. Successful CQ job j-1128-0866b5, runtime420329687fd442278304ad43b9bc58524365a67d. Enhanced HGB+hard AP0.9014/0.8929, neural AP0.7466/0.6976. This intervention is easier for enhanced boosting, harder for MLP, not a universally harder dataset. No refitting/recalibration. All300 unchanged-score comparisons pass: max error1.11e-16, zero threshold flips. First CPU job j-1128-1a111a failed; logs and diagnosis retained. Matching CUDA resolves acceptance, but cross-environment portability remains unproven.

Artifacts: results/reports/012-complete; paper/012-results.md; paper/workflow/experiment-report.md; docs/reproduce-012.md; results/engineering/direct-012/complete-verification.json and challenge-score-verification.json. Ledger: 5,280 previous +3,300 primary +2,400 secondary metric rows. GitHub archive commit ffdd1797d7ae641c8cefcf00776cbce9804f364f contains complete results; manifest commit3212ef85202e3aa9fce55d1a3fea0ceb11634bd5 independently verified before cleanup. All1,378 stage012 CQ artifact paths are inventoried in migration/stage012-result-manifest.json. Cleanup receipts are migration/final-slim-checkout-012.*.

Mac: verified344 retained files byte-for-byte before replacing the owned checkout; reclaimed585,953,280 allocated bytes in the final cleanup. Earlier partial-clone migration reclaimed707,383,296 bytes separately. Current dataset/model working copies and old Git blobs are omitted; full archives remain on GitHub/CQ. Restore only required folders with git sparse-checkout add results/cq-012/JOB_ID. Python environment and other projects/jobs unchanged. No paid compute.

Research still missing: independent component ablations, numerically portable feature construction, a common-cohort cascade/direct-objective comparison, more independent dates/markets, relevant recent published baselines and real adjudicated labels. These are future research, not claimed completed or automatically queued. No original-paper0.675 or CCF A-readiness claim.

中文结论：本轮已完成直接监督与难负例实验、独立日期扩展、冻结模型对照、核验、GitHub归档和Mac副本清理；同协议普通梯度提升被增强特征方案超过，但神经方法优越性、难负例机制的稳定收益和CCF A级证据仍未成立。
