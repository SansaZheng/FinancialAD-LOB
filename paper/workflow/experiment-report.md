# Verified direct-scoring experiments / 已核验直接评分实验

Thirty primary fold-seed runs and thirty frozen secondary evaluations completed through CQ, covering300selected-method evaluations each. Nine additional source dates across five stocks yielded45full-day partitions and3,439,144replayed rows. See [full results](../012-results.md), [data card](../../docs/dataset-012.md), [reproduction steps](../../docs/reproduce-012.md), and the source-linked [results ledger](results.csv). The previous stage011 negative results remain in archive/011-experiment-report.md and paper/011-results.md.

本轮不是仅提交任务：完整训练、冻结模型测试、逐项独立复算和归档已经完成。指标为逐股票日平均的AP，不是原论文的同数据AUC-PR复现。

| Method | Held-out dates AP | Held-out dates + stocks AP |
|---|---:|---:|
| Ordinary HGB |0.5513|0.5275|
| Enhanced HGB |0.8605|0.8521|
| Enhanced HGB + hard weights |0.8611|0.8583|
| Registered enhanced MLP + hard weights |0.7613|0.7157|

The feature-assisted boosting gain is positive in all15seed-averaged stock-days per regime. The extra hard-weighting AP gain is0.0006/0.0062 and both exploratory intervals include zero. Neural superiority is rejected by the matched enhanced-HGB countercheck. Combined HGB has identical scores across five training seeds because it uses all below-cap samples with effectively deterministic fitting; repeated seeds are not independent market observations.

增强特征的收益稳定出现在15个测试股票日上，但难负例加权增益不稳定。神经候选在每个股票日都落后于增强HGB。只有三个独立测试日期，不能用30次运行夸大样本量。

On predeclared lifetime-matched benign controls, enhanced HGB with hard weights reaches AP0.9014/0.8929 and benign FPR9.64%/8.14%; ordinary HGB AP is0.5478/0.5251. The neural candidate reaches only0.7466/0.6976 and benign FPR24.04%/22.40%. Compare these against the common-ID reference in the full report, not the unfiltered primary table. The intervention makes enhanced HGB's task easier and MLP's task harder; it is not a universal stress-test victory.

首次CPU重载检查失败，没有采用失败结果。原训练版本和CUDA环境下重试后，300项重载评分最大差异1.11e-16、阈值翻转0；全部挑战指标独立复算通过。失败日志、重试代码、模型、预测、权重和调参记录均保存。固定环境下可复现不等于跨环境数值可移植。

The evidence supports an observable feature bundle for supervised policy-label detection in this WSE cohort. It does not isolate individual Gram/timing components, prove real manipulation intent, isolate direct supervision from the previous cascade on a common cohort, or reproduce the private original-paper setup. Fifteen source dates are now covered across stages;20dates,10datasets and recent published-baseline targets remain unmet. No paid compute or unrelated job changes were used.

中文结论：本轮已真正跑完并验证“超过普通梯度提升”的结果，最强路线是特征增强加树模型；神经方法和难负例机制的独立创新证据仍不足，距离原论文可比超越和CCF A级证据还有差距。
