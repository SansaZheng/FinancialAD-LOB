# Baseline matrix

All statuses are implementation statuses, not measured scientific performance.

| Method | Status | Fairness requirement |
|---|---|---|
| Logistic regression | Runnable tabular control | Same labeled IDs and features |
| Linear SVM | Runnable tabular control | Same six validation trials |
| Random forest | Runnable tabular control | Same feature view; report CPU budget |
| Histogram gradient boosting | Runnable tabular control | Same label subset and validation |
| Volume / cancellation rule | Pending event-aligned calibration | Threshold fitted on validation |
| OC-SVM / Isolation Forest | Pending integration | Separate clean-normal regime |
| JFDS original representation | Legacy adapter, unreadable iCloud source | Recover exact official code, avoid claiming reproduction |
| Lin–Yang cascade | Original protocol/data unavailable | Equal-label supervised comparator needed |
| TCN | Pending full training adapter | Same input channels and parameter control |
| Transformer | Pending full training adapter | Same input channels, training steps and labels |
| Price-aligned liquidity candidate | Prototype + optimizer check | Same-input and no-alignment ablations |

Recent literature search checked 2026 works on November 23. Two relevant search
candidates exist but are not adopted as executable baselines yet:

* [Financial Lane Detection](https://www.provinciajournal.com/index.php/telematique/article/view/2669)
  (2026-11-03): segmentation of synthetic anomalies; output-unit compatibility,
  code and experiment reliability require inspection.
* [Real-Time Market Surveillance Framework](https://www.preprints.org/manuscript/202611.1171)
  (posted 2026-11-11): semi-synthetic order-book benchmark; preprint status and
  cross-asset task mismatch must be disclosed.

Neither date nor a similar title establishes a useful strong baseline. The two
2026-method planning target remains unmet until compatibility is verified.

中文结论：四个监督学习控制基线已具备运行入口；原论文及神经网络强基线仍需补齐，不能将清单数量视作实验完成数量。
