# Frozen WSE semi-synthetic experiment results

Suite status: partial; 10/60 fold-seed runs.

| Regime | Method | Mean fold AP | Seed SD | Test FPR | Benign FPR |
|---|---|---:|---:|---:|---:|
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
