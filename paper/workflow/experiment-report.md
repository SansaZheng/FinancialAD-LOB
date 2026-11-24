# Stage 009 report / 阶段 009 报告 — 2026-11-25

**CQ access is working.** The official free Kaggle CPU backend accepted and ran
canonical SansaZheng/FinancialAD-LOB code. Environment, dependent smoke and
three-stock expansion jobs all completed with verified outputs. The old lab
owner restriction was not modified. No fork/admin intervention is now required
for this CPU route, and no paid/GPU budget was used.

**本轮已实现的提升：** 明确区分不可观测事件与已观测零值，新增缺失通道屏蔽；
实现同输入的因果 TCN、Transformer 与流动性候选模型训练入口，统一标签子集、
批次、六次验证搜索和训练步数。参数分别为 31,187、31,915、30,561，最大差距约
4.2%。31 项工程测试在本机和 CQ 均通过，包含真实优化器步骤及因果性检查。

The WSE dataset qualification now covers five stocks on three dates: 61,440
messages, 480 snapshots and 387 valid adjacent feature pairs. 61 crossed/locked
snapshots are explicitly flagged; 7,740 event-channel values remain unknown.
Overlapping local/remote feature values differ by at most 8.88e-16, with exact
identity/mask equality and matching source hashes. The inputs are unlabeled
prefixes, including preopen/retransmission, not full-session performance data.

**强基线来源：** 从公开 CC BY 归档中提取并保存 JFDS 前作原始模型和训练代码，
未下载完整数据包，未运行原始脚本。该源码尚未接入公平基线，且存在 CPU 训练路径
兼容性问题。通用 Transformer 对照不等同于 Lin–Yang 的完整级联对比学习方法。

Evidence: `results/engineering/stage-009-summary.json`, `results/cq-009/`,
`results/engineering/cross-runtime-audit-009.json`, `docs/improvement-009.md`,
and `vendor/jfds_reference/PROVENANCE.md`. Exact specs and hashes are archived.
No detector AP improvement is reported; missing labels/session audit, original
cascade/detector integration and full scientific comparisons remain open.

中文结论：本轮提升已落到代码、真实样本和三个已完成的 CQ 任务；当前可继续正式实验准备与扩展，尚不能把工程通过或样本增加等同于超过论文 0.675 或达到 CCF A 录用水平。
