# Direct scores and hard benign controls

Status: all 30 primary fold-seeds / 300 selected evaluations complete and independently verified. Frozen-model matched-lifetime challenge CQ j-1128-1a111a is pending. Complete primary evidence: results/reports/012-complete; receipt results/engineering/direct-012/complete-verification.json. Primary data and every selected model are archived on GitHub main7972935.

The previous complete experiment did not establish superiority over strong tabular baselines. Stage011's candidate mean fold-pooled AP was0.4369 on held-out dates and0.3732 on held-out dates plus stocks, compared with HGB0.5161 and0.4429. Its negative results remain archived. Stage012 tests a new, frozen hypothesis on nine additional source dates rather than relabeling the earlier outcomes.

We acquired45stock-day partitions for five WSE stocks on Jan19,20,23,24,25,26,27,30,31,2017. Every one of3,439,144source messages was independently replayed and4,500reference snapshots were checked. The resulting passive-overlay benchmark contains51,118windows, including2,539positive policy labels and2,459benign controls. Training uses the first three dates, validation the next three, and testing the final three. Combined splits additionally exclude the test and validation stocks from training. Source provenance, license attribution, hashes, injection ledgers and censorship records are retained.

The fixed primary comparison comprises30fold-seed runs and300selected method evaluations: one chronological fold and five combined stock/date folds, each with five seeds and ten methods. The methods include logistic regression, histogram gradient boosting and direct supervised MLPs, with matched hard-negative weighting and observable interaction-feature ablations. All use the same train-only sample cap and six validation-only hyperparameter trials. The primary neural candidate is interaction_mlp_hard; hgb is its primary reference, and interaction_hgb_hard is a mandatory stronger countercheck. A feature-assisted boosting gain must not be presented as evidence that a neural model is necessary.

Hard-negative weights are computed from group-disjoint out-of-fold training scores. The highest-scoring10%of training negatives receive fivefold relative weight before class totals are renormalized. Neither generator-kind metadata nor validation/test outcomes enters mining. The saved OOF group assignments and weights are independently checked. Post-fit benign enrichment is a diagnostic rather than a mining input.

The secondary challenge was fixed before any new detector score was observed. It changes only test benign-wave withdrawal coordination, using independently selected forward/reverse offsets at each level. The construction matches positive-wave per-level lifetime marginals in the generator distribution before censoring; it does not guarantee equal empirical marginals after censoring. The completed challenge contains15,852windows,384modified controls and55retained positive-pattern collisions. One newly marketable control was excluded; all15,468other inputs are exactly unchanged. Frozen selected models and existing validation thresholds are being evaluated on common IDs, without retraining or recalibration.

All scientific fitting ran through CQ on its free Kaggle backend. All 30 runs used the same frozen scoring commit45950e7701a713e61cc7b8aa7a9eb7fcb94d08f4 and passed independent split, normalization, OOF mining, selection, threshold and metric checks. All 63 engineering tests passed before the later audit-only changes, followed by five focused audit regressions; no claim is made that every historical test was rerun after every reporting edit. No training warnings were recorded. Sum of worker runtimes was27,404.0s; maximum worker RSS3,219,624KiB and allocated CUDA tensor memory78,524,928bytes. These are not provider walltime or total GPU memory.

Primary outcomes report macro stock-day AP, pooled fold AP, seed variability, validation-calibrated recall, and benign/background false-positive rates. Paired date/stock bootstrap intervals are exploratory: only three independent test dates are available and multiplicity is not controlled. The challenge comparison must use the common-ID primary score as its reference. CPU reload parity and unchanged-row threshold flips will be reported explicitly.

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

中文说明：新增九个日期、五只股票的完整日数据已取得并验证，直接监督和难负例矩阵已全部完成。收益主要来自增强特征配合梯度提升；难负例加权增益有限，神经候选仍落后。下一项已登记的良性对照保持模型、参数、阈值不变，只改变对照生成方式。

中文结论：完整主实验已经超过同协议普通梯度提升，但尚未证明神经方法优于增强强基线；良性挑战结果仍待完成，不能据此声称超过原论文或达到CCF A水平。
