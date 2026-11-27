# Direct scores and hard benign controls

Status: complete and independently verified:30primary fold-seeds/300selected evaluations plus30frozen secondary fold-seeds/300paired evaluations. Primary report: results/reports/012-complete; secondary artifacts: results/cq-012/j-1128-0866b5/challenge-scores. Independent receipts: results/engineering/direct-012/complete-verification.json and challenge-score-verification.json. The failed CPU reload attempt is retained and excluded.

The previous complete experiment did not establish superiority over strong tabular baselines. Stage011's candidate mean fold-pooled AP was0.4369 on held-out dates and0.3732 on held-out dates plus stocks, compared with HGB0.5161 and0.4429. Its negative results remain archived. Stage012 tests a new, frozen hypothesis on nine additional source dates rather than relabeling the earlier outcomes.

We acquired45stock-day partitions for five WSE stocks on Jan19,20,23,24,25,26,27,30,31,2017. Every one of3,439,144source messages was independently replayed and4,500reference snapshots were checked. The resulting passive-overlay benchmark contains51,118windows, including2,539positive policy labels and2,459benign controls. Training uses the first three dates, validation the next three, and testing the final three. Combined splits additionally exclude the test and validation stocks from training. Source provenance, license attribution, hashes, injection ledgers and censorship records are retained.

The fixed primary comparison comprises30fold-seed runs and300selected method evaluations: one chronological fold and five combined stock/date folds, each with five seeds and ten methods. The methods include logistic regression, histogram gradient boosting and direct supervised MLPs, with matched hard-negative weighting and observable interaction-feature ablations. All use the same train-only sample cap and six validation-only hyperparameter trials. The primary neural candidate is interaction_mlp_hard; hgb is its primary reference, and interaction_hgb_hard is a mandatory stronger countercheck. A feature-assisted boosting gain must not be presented as evidence that a neural model is necessary.

Hard-negative weights are computed from group-disjoint out-of-fold training scores. The highest-scoring10%of training negatives receive fivefold relative weight before class totals are renormalized. Neither generator-kind metadata nor validation/test outcomes enters mining. The saved OOF group assignments and weights are independently checked. Post-fit benign enrichment is a diagnostic rather than a mining input.

The secondary challenge was fixed before any new detector score was observed. It changes only test benign-wave withdrawal coordination, using independently selected forward/reverse offsets at each level. The construction matches positive-wave per-level lifetime marginals in the generator distribution before censoring; it does not guarantee equal empirical marginals after censoring. The completed challenge contains15,852windows,384modified controls and55retained positive-pattern collisions. One newly marketable control was excluded; all15,468other inputs are exactly unchanged. Frozen selected models and existing validation thresholds were evaluated on common IDs, without retraining or recalibration.

All scientific fitting ran through CQ on its free Kaggle backend. All 30 runs used the same frozen scoring commit45950e7701a713e61cc7b8aa7a9eb7fcb94d08f4 and passed independent split, normalization, OOF mining, selection, threshold and metric checks. All 63 engineering tests passed before the later audit-only changes, followed by five focused audit regressions; no claim is made that every historical test was rerun after every reporting edit. No training warnings were recorded. Sum of worker runtimes was27,404.0s; maximum worker RSS3,219,624KiB and allocated CUDA tensor memory78,524,928bytes. These are not provider walltime or total GPU memory.

Primary outcomes report macro stock-day AP, pooled fold AP, seed variability, validation-calibrated recall, and benign/background false-positive rates. Paired date/stock bootstrap intervals are exploratory: only three independent test dates are available and multiplicity is not controlled. The challenge comparison must use the common-ID primary score as its reference. Reload parity and unchanged-row threshold flips are reported explicitly below.

The488-coordinate enhancement bundles cross-level/lagged co-occurrence with per-level mass, timing moments and breadth. The registered feature ablation tests this bundle, not the necessity of its individual components. A gain cannot yet be attributed specifically to cross-level Gram features rather than temporal moments or their combination. The matched-lifetime challenge probes one shortcut but does not replace component ablations.

Stage011 and stage012 use different source cohorts. Their headline AP difference cannot isolate the effect of replacing the contrastive cascade with direct supervision. Stage012 supports within-cohort comparisons among its ten registered methods; an objective-only causal claim would require running both objectives with otherwise matched inputs, supervision and budgets on a common new cohort.

The labels remain semi-synthetic behavioral policy labels, not verified human intent. WSE snapshot reconstruction lacks authoritative order identities and the original paper's private labeling conditions. These experiments therefore cannot establish direct superiority to the original reported AUC-PR0.675, real regulatory detection performance, or CCF A acceptance readiness. Five stocks from one market and three test dates also limit generalization claims.

Complete primary results, macro stock-day AP (five seeds; seed SD in parentheses):

| Method | Held-out dates | Held-out dates and stocks |
|---|---:|---:|
| logistic | 0.5224 (0.0020) | 0.5173 (0.0000) |
| logistic_hard | 0.4884 (0.0042) | 0.4520 (0.0000) |
| hgb | 0.5513 (0.0175) | 0.5275 (0.0000) |
| hgb_hard | 0.5224 (0.0079) | 0.5139 (0.0000) |
| mlp | 0.5236 (0.0075) | 0.4946 (0.0064) |
| mlp_hard | 0.5007 (0.0107) | 0.4555 (0.0081) |
| interaction_hgb | 0.8605 (0.0038) | 0.8521 (0.0000) |
| interaction_hgb_hard | 0.8611 (0.0052) | 0.8583 (0.0000) |
| interaction_mlp | 0.7642 (0.0086) | 0.7074 (0.0072) |
| interaction_mlp_hard | 0.7613 (0.0170) | 0.7157 (0.0119) |

Feature-assisted HGB with hard weights exceeds ordinary HGB by0.3097 AP on held-out dates and0.3308 on combined folds. The gain is positive in all15seed-averaged stock-days in each regime. Its benign-control FPR changes from20.42%to18.02% and18.02%to14.35%, respectively, at the unchanged validation-calibrated thresholds. A validation1%overall-negative FPR target does not imply1%FPR on the distinct benign-control subset.

The hard-weighting increment over feature-assisted HGB without hard weights is only0.0006/0.0062; exploratory paired95%intervals include zero in both regimes. The preregistered neural candidate loses0.0998/0.1426AP to feature-assisted HGB with hard weights, with negative deltas in all15stock-days. Mining captures97.49–98.96%of training benign controls, but successful mining composition does not establish improved generalization. Metadata joins for that diagnostic occur only after fitting.

Combined-fold HGB seed SD is exactly zero: all7,118–10,682eligible training samples are below the12,000cap, and deterministic boosting repeats identical scores. These are five registered executions, not five independent market samples. Chronological training samples12,000of14,902eligible windows and varies across seeds. Neural initialization still varies. The bootstrap averages seeds before resampling three dates and stocks; intervals remain exploratory, not a broad population guarantee.

A reload portability issue is explicit: ordinary HGB/logistic scores reproduce, but the first CPU challenge attempt failed unchanged-input parity. The local diagnostic also reproduces enhanced-HGB discrepancies. The exact numerical source is not established; nonzero feature variance does not rule out tree split sensitivity to small floating-point changes. No tolerance is loosened and no failed challenge result is accepted. Matching the original CUDA environment resolved all300reload comparisons, with maximum unchanged-score error1.11e-16 and zero threshold flips. This establishes reproducibility in the matched environment, not portability across arbitrary numerical libraries or CPU implementations. Models, feature formulas and thresholds stayed frozen.

The predeclared lifetime-matched secondary evaluation completed in76.25s of evaluator runtime (CQ allocation0.04h), peakRSS1,912,544KiB. It used Python3.13.16, NumPy2.1.3, PyTorch2.11.0+cu130, sklearn1.6.1. All300unchanged-input comparisons pass; no thresholds were recalibrated and no estimator was refitted. The primary reference below excludes the same one censored control, so it differs slightly from the full primary table.

| Regime | Method | Matched primary AP | Challenge AP | Primary benign FPR | Challenge benign FPR |
|---|---|---:|---:|---:|---:|
| date | logistic | 0.5230 | 0.5204 | 19.43% | 20.26% |
| date | logistic_hard | 0.4890 | 0.4824 | 18.67% | 20.00% |
| date | hgb | 0.5523 | 0.5478 | 20.39% | 20.60% |
| date | hgb_hard | 0.5229 | 0.5207 | 20.83% | 21.28% |
| date | mlp | 0.5244 | 0.5121 | 18.20% | 19.32% |
| date | mlp_hard | 0.5015 | 0.4912 | 17.94% | 19.61% |
| date | interaction_hgb | 0.8607 | 0.8961 | 18.67% | 10.42% |
| date | interaction_hgb_hard | 0.8611 | 0.9014 | 18.05% | 9.64% |
| date | interaction_mlp | 0.7644 | 0.7498 | 18.78% | 23.10% |
| date | interaction_mlp_hard | 0.7614 | 0.7466 | 19.48% | 24.04% |
| combined | logistic | 0.5180 | 0.5173 | 17.54% | 17.97% |
| combined | logistic_hard | 0.4521 | 0.4535 | 18.19% | 18.78% |
| combined | hgb | 0.5292 | 0.5251 | 17.87% | 17.73% |
| combined | hgb_hard | 0.5147 | 0.5096 | 16.91% | 17.14% |
| combined | mlp | 0.4949 | 0.4842 | 19.60% | 21.12% |
| combined | mlp_hard | 0.4558 | 0.4488 | 18.33% | 20.29% |
| combined | interaction_hgb | 0.8523 | 0.8833 | 15.10% | 9.28% |
| combined | interaction_hgb_hard | 0.8586 | 0.8929 | 14.39% | 8.14% |
| combined | interaction_mlp | 0.7075 | 0.6859 | 16.69% | 21.86% |
| combined | interaction_mlp_hard | 0.7159 | 0.6976 | 16.81% | 22.40% |

The secondary controls are not uniformly harder. Enhanced HGB with hard weighting improves from matched-primary0.8611/0.8586 to0.9014/0.8929 AP, while its benign FPR falls from18.05%/14.39%to9.64%/8.14%. The registered neural candidate drops from0.7614/0.7159 to0.7466/0.6976 AP and its benign FPR rises from19.48%/16.81%to24.04%/22.40%. This is model-dependent sensitivity to one predeclared intervention, not proof of robustness to every realistic benign pattern. The challenge neither adds independent dates nor permits choosing a new primary winner after seeing results. Both primary and challenge results, including all weaker methods, remain visible.

The hypothesis is only partially supported: the feature bundle improves matched strong tabular baselines, but hard-negative weighting does not show consistent primary gains and the registered neural candidate fails the feature-matched boosting countercheck. The next discriminating work requires feature-component ablations (moments versus cross-level terms), portable numerical feature construction qualified before training, a common-cohort comparison with the previous cascade, and new independent market/date evidence. Those are proposals, not completed experiments; do not retune on the current test or challenge set.

中文说明：本轮新增九日、五股票完整数据，完成30组主实验及30组冻结模型良性对照评估，合计600项已选方法评估。增强梯度提升在主测试和寿命匹配对照上均优于普通HGB；神经候选依然落后。难负例加权的主测试增益有限，不能将特征收益误写成该组件或神经网络的贡献。第一次CPU重载核验失败已保留，匹配原训练环境后300项核验通过且阈值翻转为零；跨环境可移植性仍是限制。

中文结论：已经获得同协议下超越普通梯度提升的可复核结果，但最强的是增强树模型；寿命匹配对照并非对所有模型更难，不能据此声称超过原论文0.675或达到CCF A论文水平。
