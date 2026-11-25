# Current claim-to-evidence map

Historical engineering claims remain in Git history. Current scientific claims use only the fresh stage011 cohort.

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
| New full result archive synchronized | paper/workflow/current.md | Pending local IPv4 restoration; CQ and local copies preserved |

中文结论：已支持逐档价格对齐的局部贡献，但不支持当前完整模型优越性、真实意图识别、原论文超越或 CCF A 达标声明。
