# Stage 009 complete — 2026-11-25
Executor: Codex. Configuration revision 5. CCF A quality aspiration; venue undecided.
Prompt: prompts/009-observation-aware-baselines.md.
Canonical: https://github.com/SansaZheng/FinancialAD-LOB

CQ access restored through the officially supported free Kaggle CPU backend.
Canonical source commit 7023f84a036c91703a3ca54130af6d07aea7198e executed successfully.
- j-1125-32c77e: environment qualification done; outputs verified/fetched.
- j-1125-951eab: 31 tests and real-feature audit done; outputs verified/fetched.
- j-1125-e0f1ad: three-stock expansion/replay done; outputs verified/fetched.
No open project jobs remain. No paid resources, GPU quota, unrelated jobs or
shared server environments were changed. Lab owner policy is unchanged but no
longer blocks current CPU work. No fork is needed for this route.

Implemented: ten-channel missingness-aware liquidity features; explicit event
coverage; zero-imputation gates; causal TCN/Transformer/candidate adapters;
shared six-trial supervised trainer, labeled IDs/batches/normalization budgets.
Parameter counts: 31,187 / 31,915 / 30,561. CPU-qualified locally and remotely;
CUDA option not yet qualified. 31 tests pass, including actual tiny optimizer
steps and future/missing-value perturbation invariance. These are engineering
fixtures, not scientific detector performance experiments.

Real public data: five WSE stocks x three dates = 15 stock-day prefixes,
61,440 messages, 480 five-level snapshots, 61 crossed/locked flagged; 387 valid
adjacent feature pairs and 7,740 explicitly unknown event-channel values.
Full-day/session qualification, actual tick scales and intent labels are pending.
Local/CQ overlapping features differ at most 8.88e-16; identities and masks match
exactly and source-code hashes match. Full-source-file hashes remain unverified.

JFDS predecessor source recovered via bounded ranges from its CC BY Zenodo
archive; original source files preserved with hashes. It was statically inspected,
not executed or relabeled as the complete 2025 cascaded/contrastive framework.

All execution specs, small raw permitted samples, derived artifacts, receipts,
code and steps are being synchronized to canonical GitHub. Legacy iCloud files
remain preserved; no old-data migration or disk-space-reclamation claim.

Next scientific stage: qualify full-day sessions/attribution and genuine or
explicitly semi-synthetic labels; add exact cascade/OC-SVM/IF regimes; freeze
stock/date/generator splits; run matched-budget multi-seed experiments and
ablations. No claim of exceeding 0.675 or achieving CCF A acceptance is supported.

中文结论：已解除当前 CQ 接入阻塞并完成三个远端任务，方法与公平对照可运行，真实样本扩展至五股票；检测性能提升仍待合格标签和正式留出集实验验证。
