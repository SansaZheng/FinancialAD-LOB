# Evidence map

| Claim | Artifact | Status / scope |
|---|---|---|
| Four controls share exact training-label and split hashes | `tests/test_runner.py`, `results/engineering/contracts/tests.log` | Verified on generated engineering fixture |
| Split code rejects event/window leakage | `tests/test_contracts.py` | Verified tested cases; not proof of an external dataset audit |
| Candidate is causal under future perturbation | `tests/test_models.py` | Verified tested tensor fixture |
| Candidate survives a finite optimizer step | `tests/test_models.py` | Engineering execution only |
| Price alignment avoids tested rank-migration artifact | `tests/test_contracts.py` | Limited constructed example |
| Initial GitHub copy matches 33 local files | `migration/github-verification.json` | Independent remote clone + SHA256 |
| WSE public event prefixes actually acquired | `results/engineering/public-data-summary-20261124.json` | 2 stocks × 3 dates, 24,576 messages; CC BY 4.0 |
| WSE five-level replay executed | `results/wselob-probe-20261124*/replay-audit.json` | 192 snapshots; 28 crossed/locked; no manipulation labels |
| Public-data reader and order parser tested | `results/engineering/qualification-20261124/tests.log` | 26 total engineering checks; no AP claim |
| Current public data/code archive matches 95 files | `migration/github-verification-20261124.json` | Independent GitHub clone at 594a829 + SHA256; 3,117,531 bytes |
| Legacy data migrated | None | Not done; placeholders unreadable |
| CQ canonical source can execute | `results/cq-009/`, `cq/009-kaggle-*.json` | Three CPU jobs completed through official free Kaggle route |
| Five-stock real-prefix replay completed | `results/engineering/stage-009-summary.json` | 15 stock-days, 61,440 messages; unlabeled prefixes only |
| Three neural controls share labels/batches/budgets | `tests/test_sequence.py`, CQ smoke tests.log | Verified on engineering fixtures; actual parameter counts reported |
| Missing values do not masquerade as observed zeros | `results/wse-feature-audit-009/`, `tests/test_sequence.py` | 10-channel explicit masks; no AP gain implied |
| Cross-date/cross-stock scientific gains | None | Real prefixes available; full inputs, labels, controls and CQ batches pending |
| Original paper reproduced / exceeded | None | Unsupported |
| CCF A quality achieved | None | Aspiration only |

中文结论：已验证的都是工程与存档事实；真实实验性能、论文复现和顶会水平仍无完成证据。
