# Current claim-to-evidence map

Historical engineering claims remain in Git history. Completed detector-performance claims below use the stage011 cohort. Stage012 adds independently verified source/benchmark evidence; its full-matrix and challenge performance are pending, with21primary fold-seeds already checked.

| Claim | Evidence | Status and limit |
|---|---|---|
| Full daily partitions, five stocks across three fresh dates | results/cq-011/j-1125-8c5bef/full-sessions/audit.json; j-1125-41384c/benchmark/full-day-validation.json | Verified selected artifacts and independent replay; not whole annual archive |
| All fixed comparisons executed | results/engineering/cascade-011/complete-metric-verification.json | 60 fold-seeds, 660 method evaluations; semi-synthetic |
| Depth-resolved aligned candidate improves over L1 and rank control | results/reports/011-complete/report.json | Positive mean AP and exploratory paired deltas in four regimes; few dates |
| Current contrastive objective improves performance | Same report, price_no_scl ablation | Unsupported; no-SCL has higher mean AP in every regime |
| Raw-book autoencoder is necessary | Same report, price_no_lob ablation | Unsupported; small mixed changes |
| Candidate beats strong supervised controls | Same report, supervised_hgb/logistic comparisons | Unsupported; HGB has higher mean AP in every regime |
| Real manipulation intent detected | No adjudicated labels | Unsupported; generated policy labels only |
| Original 0.675 reproduced or exceeded | Different market, input availability and protocol | Unsupported; direct numerical comparison invalid |
| CCF A-level evidence complete | Only three fresh dates and one generator seed; no realistic response | Not achieved |
| New full result archive synchronized | paper/workflow/current.md | Verified: canonical main094b7dd pushed and independently checked; subsequent stage012 data/code archives pushed through124e361 |

| Nine additional dates,45stock-days acquired and independently replayed | results/engineering/direct-012/dataset-verification.json; results/cq-012/j-1127-1d410b/benchmark | Verified3,439,144rows and4,500reference snapshots; not real labels |
| New direct/hard-negative candidate beats boosting | cq/012-pilot-submission.txt; configs/012-preregistered.json | Partial evidence: enhanced HGB improves AP in completed runs; the registered neural candidate still loses to feature-matched HGB.21/30runs checked; no final broad superiority claim. |
| Per-level lifetime challenge retains unchanged non-wave inputs | results/engineering/direct-012/challenge-data-verification.json | Verified15,468unchanged windows,384modified controls,1censored; theoretical marginal match before censoring |
| Robustness to more difficult benign controls | configs/012-robustness.json | Pending frozen-model evaluation; collisions deliberately retained |

中文结论：已支持逐档价格对齐的局部贡献，但不支持当前完整模型优越性、真实意图识别、原论文超越或 CCF A 达标声明。
