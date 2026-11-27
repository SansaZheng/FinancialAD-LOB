# Current claim-to-evidence map

Stage011 negative results remain in paper/011-results.md and workflow/archive; never pooled with stage012.

| Claim | Artifact | Status and bound |
|---|---|---|
| Nine new dates and45full stock-days independently replayed | results/cq-012/j-1127-1d410b/benchmark; results/engineering/direct-012/dataset-verification.json | Supported:3,439,144rows/4,500snapshots; selected partitions, not full annualarchive |
| All registered direct comparisons executed | results/engineering/direct-012/complete-verification.json |30/30runs,300/300evaluations; artifact consistency |
| Feature-assisted boosting improves ordinary HGB | results/reports/012-complete/report.json; group-diagnosis.json | AP+.3097/+.3308,15/15stock-days; semi-synthetic cohort only |
| Neural candidate beats the enhanced strong baseline | Same report | Unsupported: AP−.0998/−.1426 |
| Hard-negative weighting consistently improves AP | Same report/contrasts | Unsupported: enhancedHGB increments.0006/.0062 with intervals crossing0; other families mixed/negative |
| Cross-level Gram terms are individually necessary | Feature bundle ablation | Pending component ablations; timing/mass moments bundled |
| Direct supervision causes improvement over old cascade | Differentstage011/012cohorts | Unsupported until matched-cohort objective comparison |
| Frozen-model lifetime intervention is evaluated | results/cq-012/j-1128-0866b5/challenge-scores; challenge-score-verification.json |30/30runs,300/300paired evaluations, no refitting; easier for enhancedHGB, harder forMLP |
| Reload is portable across numerical environments | frozen-first-attempt.log; local-reload-diagnosis.json | Unsupported; firstCPUfailure preserved; matchedCUDApasses, max1.11e-16/0flips |
| Challenge is an independent dataset or uniformly harder | configs/012-robustness.json and challenge report | Unsupported; same source IDs, model-dependent difficulty |
| Real manipulation intent or original0.675is surpassed | No comparable adjudicated/privateoriginaldata | Unsupported |
| CCF A evidence targets complete | workflow/config.json and literature.md | Not achieved: one market, three testdates,15source datesoverall, no reproduced2026methods |

中文结论：支持增强特征配合梯度提升的局部提升，不支持神经优越性、跨平台完全可复现、真实操纵识别或CCF A达标声明。
