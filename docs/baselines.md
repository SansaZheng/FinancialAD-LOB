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
| TCN | Runnable causal supervised adapter; engineering-qualified | Same input, labels, batches and parameter ceiling |
| Transformer | Runnable causal supervised adapter; engineering-qualified | Generic control, not the Lin–Yang cascade |
| Price-aligned liquidity candidate | Runnable observation-aware wrapper and trainer | Scientific alignment ablations pending |

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

See [observation-aware comparisons](improvement-009.md) for sequence budgets and
actual parameter counts. Original-paper cascade and detector regimes remain pending.

中文结论：四个表格控制基线及三个序列模型入口已实现；工程验证不是金融性能结果，原论文完整管线和跨域实验仍需补齐。
