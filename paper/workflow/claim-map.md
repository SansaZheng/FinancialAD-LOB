# Evidence map

| Claim | Artifact | Status / scope |
|---|---|---|
| Four controls share exact training-label and split hashes | `tests/test_runner.py`, `results/engineering/contracts/tests.log` | Verified on generated engineering fixture |
| Split code rejects event/window leakage | `tests/test_contracts.py` | Verified tested cases; not proof of an external dataset audit |
| Candidate is causal under future perturbation | `tests/test_models.py` | Verified tested tensor fixture |
| Candidate survives a finite optimizer step | `tests/test_models.py` | Engineering execution only |
| Price alignment avoids tested rank-migration artifact | `tests/test_contracts.py` | Limited constructed example |
| Initial GitHub copy matches 33 local files | `migration/github-verification.json` | Independent remote clone + SHA256 |
| Legacy data migrated | None | Not done; placeholders unreadable |
| CQ experiment running | `results/engineering/cq-submission.json` | False: submission rejected, no job ID |
| Cross-date/cross-stock scientific gains | None | Pending genuine data, controls and CQ runs |
| Original paper reproduced / exceeded | None | Unsupported |
| CCF A quality achieved | None | Aspiration only |

中文结论：已验证的都是工程与存档事实；真实实验性能、论文复现和顶会水平仍无完成证据。
