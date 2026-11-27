# Direct supervised scores on fresh dates

Status: partial, 1/30 fold-seed runs.

| Regime | Method | Macro stock-day AP | Pooled fold AP | Benign FPR | Background FPR | Recall |
|---|---|---:|---:|---:|---:|---:|
| date | logistic | 0.5217 | 0.4974 | 0.2003 | 0.0006 | 0.1945 |
| date | logistic_hard | 0.4889 | 0.4649 | 0.1769 | 0.0005 | 0.1870 |
| date | hgb | 0.5364 | 0.5270 | 0.1964 | 0.0000 | 0.2334 |
| date | hgb_hard | 0.5215 | 0.5060 | 0.1860 | 0.0000 | 0.2058 |
| date | mlp | 0.5214 | 0.4951 | 0.1782 | 0.0008 | 0.2246 |
| date | mlp_hard | 0.4850 | 0.4559 | 0.1873 | 0.0007 | 0.1995 |
| date | interaction_hgb | 0.8624 | 0.8616 | 0.1821 | 0.0000 | 0.6625 |
| date | interaction_hgb_hard | 0.8696 | 0.8656 | 0.1664 | 0.0000 | 0.6399 |
| date | interaction_mlp | 0.7516 | 0.7429 | 0.1860 | 0.0001 | 0.5609 |
| date | interaction_mlp_hard | 0.7441 | 0.7361 | 0.1873 | 0.0003 | 0.5496 |

中文结论：以上为固定新日期半合成协议的结果；须同时比较原始与增强强基线、难负例误报和配对差值，不能直接等同于真实操纵检测或超过原论文。
