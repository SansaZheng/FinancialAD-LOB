# Verified stage011 results / 已核验结果

All 60 registered fold-seed runs and 660 selected evaluations completed through CQ. Independent checks passed for exact splits and labels, six validation trials, validation-only thresholds, ten training epochs per neural stage, protocol/data hashes, and every saved AP/AUROC/PR-AUC/FPR/recall. This establishes artifact consistency, not real manipulation intent.

完整矩阵已跑通并复算通过。逐档价格对齐优于当前论文结构适配版、L1 和同档位差分，但完整候选方法在四种划分上均落后于梯度提升；对比损失消融也没有支持该组件的必要性。

| Method | Date AP | Stock AP | Date + stock AP | Unseen-style AP |
|---|---:|---:|---:|---:|
| Paper-structure cascade adaptation | 0.0640 | 0.0616 | 0.0738 | 0.0419 |
| Raw OC-SVM | 0.0663 | 0.0689 | 0.0959 | 0.0311 |
| Dynamics OC-SVM | 0.3277 | 0.3171 | 0.3484 | 0.2095 |
| L1-flow cascade | 0.2065 | 0.2110 | 0.2073 | 0.1240 |
| Price-aligned multilevel cascade | 0.4369 | 0.4847 | 0.3732 | 0.2886 |
| Rank-aligned ablation | 0.3327 | 0.3693 | 0.2814 | 0.1998 |
| Without contrastive loss | 0.4717 | 0.4951 | 0.4170 | 0.2993 |
| Without raw-book representation | 0.4415 | 0.4832 | 0.3754 | 0.2862 |
| Supervised logistic | 0.4291 | 0.4850 | 0.4468 | 0.2808 |
| Supervised histogram boosting | 0.5161 | 0.5035 | 0.4429 | 0.3423 |

AP is average precision, not trapezoidal PR area. Stock and combined results average the five held-out-stock folds, then seeds. Seed standard deviations and all eleven methods are in `results/reports/011-complete/report.json`. They do not measure independent market uncertainty.

The price-aligned candidate minus L1 macro stock-day AP deltas are +0.2102 (date), +0.2694 (stock), +0.1659 (combined), and +0.1474 (style). Against histogram boosting the corresponding deltas are −0.0899, −0.0243, −0.0697, and −0.0285. These differ from the pooled/fold AP table because AP is nonlinear and these contrasts average individual stock-day APs. Paired exploratory bootstrap intervals average seeds first and resample dates and stocks. One held-out date, or three dates for stock tests, is too little for strong population-level claims; intervals have no multiplicity correction.

The candidate date AP rises from 0.4369 to 0.4717 when the contrastive term is removed; combined AP rises from 0.3732 to 0.4170. Dropping the raw-book representation changes date AP only to 0.4415 and combined AP to 0.3754. The evidence supports retaining price-aligned depth information, but does not justify the present contrastive objective or an expensive raw-book autoencoder as necessary innovations.

At the validation-calibrated nominal 1% overall-negative FPR threshold, date benign-control FPR is 16.17% for the candidate and 15.34% for histogram boosting. Rare benign liquidity bursts remain a substantial failure mode; good background discrimination alone is insufficient. These are control-subgroup FPRs, not the overall test FPR.

Data: 15 untouched stock-days, 1,224,907 full daily messages, 1,189,279 session snapshots; 18,282 windows with 928 synthetic positive policies and 896 benign controls. Independent replay matched 1,500 snapshots after processing all daily rows. The generator retained 1,728 visible synthetic level-steps missing from the base book, censored 35 marketability cases, and retained seven random benign-pattern collisions. Raw source license is CC BY 4.0. Labels describe generated risk patterns, not trader intent; there is no endogenous market response or matching engine.

Compute: j-1125-161f04 (date/style), j-1125-5788a5 (stock), j-1125-58fc68 (combined). All pin execution commit c34097d44f10ab42db7cd35b6d787ce4b055b8b8; retained code/input blobs equal canonical cfadd02a59ac44501dc53c044e1168994ed03b4a. Each provider notebook supplies two T4 GPUs with one child per card. Measured peak worker RSS 3,167,780 KiB; peak allocated CUDA memory 213,105,664 bytes; nominal fusion target 200,000 parameters, actual 199,289–200,799 after training-only constant-feature removal. CQ reported allocations of 0.90/2.94/1.63 hours respectively, which include provider/collection overhead and differ from summed worker training time. No paid rental.

[Source paper](https://arxiv.org/abs/2508.17086) reports 0.675 on different data and settings. We implemented its described cascade structure and one-class detectors using a compact preserved JFDS Transformer adaptation, but lack exact 2015 LOBSTER data/labels and eight trade/cancel indicators. This is not an exact paper reproduction. Comparing any WSE AP directly with 0.675 would be invalid. CCF A quality is still an aspiration.

Next discriminating experiments, not results: (1) keep the price-aligned depth features and test a direct supervised scoring head against the same strong controls, separating objective effects from representation effects; (2) use training-only hard-negative sampling shared across methods, reporting benign-subgroup FPR at fixed recall; (3) add elapsed-time and observed-coverage controls, fresh dates and independent generator seeds, plus amplitude/lifetime shifts and leave-one-generator-out tests. Freeze each next protocol before inspecting its new test set. Obtaining lawful adjudicated or realistic agent-simulator manipulation data is needed before any real-intent claim.

GitHub sync status is tracked in `paper/workflow/current.md`. Local IPv4 failure blocked the latest bulk push; the connected GitHub integration can read this repository but rejected Git blob creation with HTTP403. Unpushed results remain committed locally and preserved on CQ. No unverified result copy has been deleted.

中文结论：完整 660 项实验已完成并独立核验；逐档价格对齐确有增益，但当前级联候选方法未胜过强监督基线，对比学习组件反而拖累结果。尚不能宣称超过原论文或达到 CCF A 水平。下一轮应围绕监督目标、良性难负例和更多独立日期补证；GitHub 新结果同步仍待网络恢复。
