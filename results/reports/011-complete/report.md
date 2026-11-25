# Frozen WSE semi-synthetic experiment results

Suite status: complete; 60/60 fold-seed runs.

| Regime | Method | Mean fold AP | Seed SD | Test FPR | Benign FPR |
|---|---|---:|---:|---:|---:|
| combined | cascade_if | 0.0614 | 0.0018 | 0.0111 | 0.0016 |
| combined | cascade_ocsvm | 0.0738 | 0.0084 | 0.0146 | 0.0220 |
| combined | dynamics_ocsvm | 0.3484 | 0.0000 | 0.0100 | 0.1121 |
| combined | l1_cascade_ocsvm | 0.2073 | 0.0092 | 0.0109 | 0.0787 |
| combined | price_cascade_ocsvm | 0.3732 | 0.0106 | 0.0102 | 0.1220 |
| combined | price_no_lob | 0.3754 | 0.0103 | 0.0106 | 0.1266 |
| combined | price_no_scl | 0.4170 | 0.0119 | 0.0107 | 0.1534 |
| combined | rank_cascade_ocsvm | 0.2814 | 0.0086 | 0.0120 | 0.0988 |
| combined | raw_ocsvm | 0.0959 | 0.0000 | 0.0257 | 0.0760 |
| combined | supervised_hgb | 0.4429 | 0.0000 | 0.0149 | 0.2683 |
| combined | supervised_logistic | 0.4468 | 0.0000 | 0.0101 | 0.1775 |
| date | cascade_if | 0.0561 | 0.0012 | 0.0093 | 0.0019 |
| date | cascade_ocsvm | 0.0640 | 0.0015 | 0.0097 | 0.0077 |
| date | dynamics_ocsvm | 0.3277 | 0.0006 | 0.0086 | 0.0984 |
| date | l1_cascade_ocsvm | 0.2065 | 0.0051 | 0.0100 | 0.0901 |
| date | price_cascade_ocsvm | 0.4369 | 0.0087 | 0.0104 | 0.1617 |
| date | price_no_lob | 0.4415 | 0.0065 | 0.0097 | 0.1534 |
| date | price_no_scl | 0.4717 | 0.0058 | 0.0105 | 0.1725 |
| date | rank_cascade_ocsvm | 0.3327 | 0.0086 | 0.0112 | 0.1329 |
| date | raw_ocsvm | 0.0663 | 0.0011 | 0.0087 | 0.0160 |
| date | supervised_hgb | 0.5161 | 0.0000 | 0.0082 | 0.1534 |
| date | supervised_logistic | 0.4291 | 0.0000 | 0.0111 | 0.2045 |
| stock | cascade_if | 0.0465 | 0.0007 | 0.0115 | 0.0055 |
| stock | cascade_ocsvm | 0.0616 | 0.0032 | 0.0112 | 0.0060 |
| stock | dynamics_ocsvm | 0.3171 | 0.0006 | 0.0119 | 0.1239 |
| stock | l1_cascade_ocsvm | 0.2110 | 0.0051 | 0.0096 | 0.0763 |
| stock | price_cascade_ocsvm | 0.4847 | 0.0026 | 0.0102 | 0.1649 |
| stock | price_no_lob | 0.4832 | 0.0026 | 0.0106 | 0.1675 |
| stock | price_no_scl | 0.4951 | 0.0039 | 0.0100 | 0.1693 |
| stock | rank_cascade_ocsvm | 0.3693 | 0.0032 | 0.0095 | 0.1174 |
| stock | raw_ocsvm | 0.0689 | 0.0012 | 0.0354 | 0.0665 |
| stock | supervised_hgb | 0.5035 | 0.0000 | 0.0101 | 0.1893 |
| stock | supervised_logistic | 0.4850 | 0.0000 | 0.0100 | 0.1887 |
| style | cascade_if | 0.0294 | 0.0018 | 0.0091 | 0.0032 |
| style | cascade_ocsvm | 0.0419 | 0.0018 | 0.0092 | 0.0045 |
| style | dynamics_ocsvm | 0.2095 | 0.0004 | 0.0086 | 0.0984 |
| style | l1_cascade_ocsvm | 0.1240 | 0.0048 | 0.0109 | 0.1010 |
| style | price_cascade_ocsvm | 0.2886 | 0.0053 | 0.0102 | 0.1559 |
| style | price_no_lob | 0.2862 | 0.0054 | 0.0099 | 0.1495 |
| style | price_no_scl | 0.2993 | 0.0135 | 0.0100 | 0.1655 |
| style | rank_cascade_ocsvm | 0.1998 | 0.0076 | 0.0111 | 0.1240 |
| style | raw_ocsvm | 0.0311 | 0.0003 | 0.0087 | 0.0160 |
| style | supervised_hgb | 0.3423 | 0.0000 | 0.0111 | 0.2077 |
| style | supervised_logistic | 0.2808 | 0.0000 | 0.0114 | 0.2077 |

Paired stock-day intervals, exact split/seed records and prediction hashes are in report.json. These intervals are exploratory with very few independent dates.

中文结论：以上仅为固定 WSE 半合成协议上的结果。是否改进须结合配对差值、消融和正常大额流动性对照判断；任何数值超过 0.675 都不能直接证明超过原论文。
