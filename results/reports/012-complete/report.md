# Direct supervised scores on fresh dates

Status: complete, 30/30 fold-seed runs.

| Regime | Method | Macro stock-day AP | Pooled fold AP | Benign FPR | Background FPR | Recall |
|---|---|---:|---:|---:|---:|---:|
| combined | logistic | 0.5173 | 0.5010 | 0.1750 | 0.0002 | 0.1809 |
| combined | logistic_hard | 0.4520 | 0.4397 | 0.1816 | 0.0006 | 0.1740 |
| combined | hgb | 0.5275 | 0.5136 | 0.1802 | 0.0000 | 0.1944 |
| combined | hgb_hard | 0.5139 | 0.4966 | 0.1707 | 0.0000 | 0.1851 |
| combined | mlp | 0.4946 | 0.4788 | 0.1956 | 0.0006 | 0.2431 |
| combined | mlp_hard | 0.4555 | 0.4409 | 0.1830 | 0.0004 | 0.2301 |
| combined | interaction_hgb | 0.8521 | 0.8524 | 0.1506 | 0.0000 | 0.6368 |
| combined | interaction_hgb_hard | 0.8583 | 0.8602 | 0.1435 | 0.0000 | 0.6347 |
| combined | interaction_mlp | 0.7074 | 0.7026 | 0.1666 | 0.0002 | 0.5109 |
| combined | interaction_mlp_hard | 0.7157 | 0.7111 | 0.1677 | 0.0001 | 0.5292 |
| date | logistic | 0.5224 | 0.4959 | 0.1945 | 0.0006 | 0.1962 |
| date | logistic_hard | 0.4884 | 0.4625 | 0.1873 | 0.0006 | 0.2010 |
| date | hgb | 0.5513 | 0.5330 | 0.2042 | 0.0000 | 0.2369 |
| date | hgb_hard | 0.5224 | 0.5078 | 0.2083 | 0.0000 | 0.2216 |
| date | mlp | 0.5236 | 0.4961 | 0.1823 | 0.0006 | 0.2304 |
| date | mlp_hard | 0.5007 | 0.4715 | 0.1800 | 0.0006 | 0.2256 |
| date | interaction_hgb | 0.8605 | 0.8595 | 0.1867 | 0.0000 | 0.6587 |
| date | interaction_hgb_hard | 0.8611 | 0.8594 | 0.1802 | 0.0000 | 0.6449 |
| date | interaction_mlp | 0.7642 | 0.7568 | 0.1875 | 0.0001 | 0.5839 |
| date | interaction_mlp_hard | 0.7613 | 0.7504 | 0.1948 | 0.0003 | 0.5817 |

中文结论：以上为固定新日期半合成协议的结果；须同时比较原始与增强强基线、难负例误报和配对差值，不能直接等同于真实操纵检测或超过原论文。
