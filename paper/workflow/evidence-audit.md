# Evidence audit — stage012

Verified completion:30primary fold-seeds/300selected evaluations,30frozen secondary fold-seeds/300paired evaluations. Exact split IDs, label/source hashes, train-only normalization, group-disjoint OOF mining, shared train cap, six validation-only trials, unchanged thresholds and every saved metric are independently checked. Primary and secondary receipts: results/engineering/direct-012/{complete-verification,challenge-score-verification}.json. Exported methods.csv and challenge-methods.csv each contain300unique rows; cumulative ledger preserves5,280prior-cohort rows and adds3,300primary plus2,400secondary metric rows.

Data: nine new dates/five stocks/45daily partitions/3,439,144rows,4,500reference snapshots.51,118primary windows;15,852secondary windows. Three held-out dates,15teststock-days; one market and one generator seed per condition. Licensing/provenance/censoring/collisions are explicit in docs/dataset-012.md. Three source job audits and all retained files are archived. No whole-annual-archive hash claim.

Supported: enhanced HGB+hard AP.8611/.8583 versus ordinaryHGB.5513/.5275 on held-out dates/combinedfolds. Positive differences in15/15seed-averaged stock-days. Unsupported: neural superiority (candidate.7613/.7157), consistent hard-weight benefit (increments.0006/.0062, exploratory intervals cross zero), specific cross-level Gram necessity (feature bundle also includes per-level moments), and objective-only improvement over stage011 (different cohorts). Shared hard miners use enhanced features even for base scorers; the scorer ablation does not remove them from every pipeline component.

Secondary: enhancedHGBhard AP.9014/.8929, benignFPR9.64%/8.14%; neuralcandidate AP.7466/.6976, benignFPR24.04%/22.40%. The challenge is easier for enhanced boosting, harder for MLP. No broad robustness or independently harder-dataset claim. Common-ID references and all10methods are retained, no refitting or post-test selection.

Portability: firstCPUreloadattempt j-1128-1a111a failed; no metrics accepted. Saved local diagnosis reproduces enhanced-HGB discrepancies and exact cause remains unresolved. MatchingCUDAretry j-1128-0866b5 passes300scorecomparisons (max1.11e-16;0thresholdflips). This qualification does not establish cross-CPU portability. Training sources unchanged. Three focused reload/marginal/tamper tests pass after diagnostic changes; earlier63test suite and five audit regressions are preserved without claiming an unnecessary full rerun.

Resources: totalprimaryworker27,404.0s,maximumRSS3,219,624KiB,maximumallocatedCUDAtensors78,524,928bytes; secondary76.25s/RSS1,912,544KiB. No trainingwarnings. These measurements exclude GPUcontext and cannot be equated with provider walltime. All jobs use free CQKaggle; no cloud spending.

Limits: semi-synthetic policy labels, no real intent/orderidentity/endogenousresponse, no exact originalprivateLOBSTERsetup, onlythree testdates, seed repetitions not market replication, exploratory non-multiplicity-corrected intervals, tenvariants fromthreeclassifierfamilies rather than tenindependentrecentpublishedmethods. No original0.675orCCFAreadinessclaim. See literature.md for checked recent work, none claimed reproduced.

中文结论：本轮证据足以支持同协议特征增强收益，并明确否定当前神经模型优越性；失败记录、跨环境限制和未完成的研究目标均保留。
