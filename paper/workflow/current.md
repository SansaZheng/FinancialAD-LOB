# Active stage 009 — 2026-11-25
Executor: Codex. Configuration revision 5. CCF A quality aspiration; venue undecided.
Task: prompts/009-observation-aware-baselines.md.

Implemented: observation-aware ten-channel encoding, missing-channel gates,
causal TCN/Transformer/candidate controls, shared six-trial supervised runner,
training-only normalization and label/batch/parameter provenance.
31 local CPU tests pass. Actual WSE audit: 152 valid pairs, 1,520 level tokens,
3,040 unknown event-channel values. No manipulation AP claimed.

CQ canonical GitHub source now works through the official free Kaggle backend:
- j-1125-32c77e environment: done, outputs verified and fetched.
- j-1125-951eab dependent tests + real feature audit: done, verified and fetched.
- j-1125-e0f1ad additional three-stock public prefix/replay audit: submitted;
  latest lifecycle state will be verified before final reporting.
All pin 7023f84a036c; full SHA in cq/009-kaggle-*.json. Zero GPU/paid budget.
Local/remote identities and masks match exactly; feature max difference
8.881784197001252e-16. Source code hashes match. No other jobs changed.

Next: finish and archive expansion job; update source coverage; qualify full-day
sessions and synthetic/real labels before any scientific detector comparison.

中文结论：CQ 接入已通过免费 Kaggle 路径恢复，方法代码与公平控制已实现；正在扩充真实数据覆盖，尚无正式检测性能提升结论。
