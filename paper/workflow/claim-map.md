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
| CQ experiment running | `results/engineering/cq-submission-20261124.json` | False: submission rejected, no job ID |
| Cross-date/cross-stock scientific gains | None | Real prefixes available; full inputs, labels, controls and CQ batches pending |
| Original paper reproduced / exceeded | None | Unsupported |
| CCF A quality achieved | None | Aspiration only |

中文结论：已验证的都是工程与存档事实；真实实验性能、论文复现和顶会水平仍无完成证据。
