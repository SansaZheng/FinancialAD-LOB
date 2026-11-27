# Direct scores and hard benign controls

Status: experiments in progress; this document does not contain a completed performance claim.

The previous complete experiment did not establish superiority over strong tabular baselines. Stage011's candidate macro stock-day AP was0.4369 on held-out dates and0.3732 on held-out dates plus stocks, compared with HGB0.5161 and0.4429. Its negative results remain archived. Stage012 tests a new, frozen hypothesis on nine additional source dates rather than relabeling the earlier outcomes.

We acquired45stock-day partitions for five WSE stocks on Jan19,20,23,24,25,26,27,30,31,2017. Every one of3,439,144source messages was independently replayed and4,500reference snapshots were checked. The resulting passive-overlay benchmark contains51,118windows, including2,539positive policy labels and2,459benign controls. Training uses the first three dates, validation the next three, and testing the final three. Combined splits additionally exclude the test and validation stocks from training. Source provenance, license attribution, hashes, injection ledgers and censorship records are retained.

The fixed primary comparison comprises30fold-seed runs and300selected method evaluations: one chronological fold and five combined stock/date folds, each with five seeds and ten methods. The methods include logistic regression, histogram gradient boosting and direct supervised MLPs, with matched hard-negative weighting and observable interaction-feature ablations. All use the same train-only sample cap and six validation-only hyperparameter trials. The primary neural candidate is interaction_mlp_hard; hgb is its primary reference, and interaction_hgb_hard is a mandatory stronger countercheck. A feature-assisted boosting gain must not be presented as evidence that a neural model is necessary.

Hard-negative weights are computed from group-disjoint out-of-fold training scores. The highest-scoring10%of training negatives receive fivefold relative weight before class totals are renormalized. Neither generator-kind metadata nor validation/test outcomes enters mining. The saved OOF group assignments and weights are independently checked. Post-fit benign enrichment is a diagnostic rather than a mining input.

The secondary challenge was fixed before any new detector score was observed. It changes only test benign-wave withdrawal coordination, using independently selected forward/reverse offsets at each level. The construction matches positive-wave per-level lifetime marginals in the generator distribution before censoring; it does not guarantee equal empirical marginals after censoring. The completed challenge contains15,852windows,384modified controls and55retained positive-pattern collisions. One newly marketable control was excluded; all15,468other inputs are exactly unchanged. Frozen selected models and existing validation thresholds will be evaluated on common IDs, without retraining or recalibration.

All scientific fitting runs through CQ on its free Kaggle backend. CUDA qualification passed, and all63engineering tests passed. The formal date/seed0 pilot j-1127-02f40d is running; its measurements will determine resource reservations for the remaining fixed runs. These engineering and data checks are not detector-performance evidence.

Primary outcomes will report macro stock-day AP, pooled fold AP, seed variability, validation-calibrated recall, and benign/background false-positive rates. Paired date/stock bootstrap intervals are exploratory: only three independent test dates are available and multiplicity is not controlled. The challenge comparison must use the common-ID primary score as its reference. CPU reload parity and unchanged-row threshold flips will be reported explicitly.

The labels remain semi-synthetic behavioral policy labels, not verified human intent. WSE snapshot reconstruction lacks authoritative order identities and the original paper's private labeling conditions. These experiments therefore cannot establish direct superiority to the original reported AUC-PR0.675, real regulatory detection performance, or CCF A acceptance readiness. Five stocks from one market and three test dates also limit generalization claims.

中文说明：本轮将直接监督评分、可观测的多档协调特征和仅由训练集产生的难负例权重放到同一公平协议中比较。新增九个日期已经取得并验证，正式试跑正在CQ运行。更难良性对照会使用原模型与原阈值，检查方法是否仅依赖简单的模拟特征。

中文结论：目前完成的是独立日期数据、标签与难对照构造，以及运行与核验准备；是否超过梯度提升仍待完整结果。即使本轮AP提高，也只能支持这一半合成协议下的有限结论。
