011b-frozen-matrix | Codex | experiments completed; archive sync blocked | configuration 6 | 2026-11-25T17:54:00.972168+00:00

Prompt: [011b](prompts/011b-frozen-matrix.md). Report: [complete findings](../011-results.md). Target CCF A quality, specific venue unset. Route lob-passive-lifecycle-v2.

Completed: five stocks × three fresh dates, 1,224,907 full daily messages; 18,282 windows, 928 synthetic positives, 896 benign controls. Acquisition/replay jobs j-1125-8c5bef and j-1125-41384c; CUDA qualification j-1125-f2ce0f. All 60 fold-seed runs and 660 selected evaluations completed: date/style j-1125-161f04, stock j-1125-5788a5, combined j-1125-58fc68. No remaining active jobs for this matrix. Execution commit c34097d44f10ab42db7cd35b6d787ce4b055b8b8; protocol SHA256 821a8dc6450119c672bb61d9ada704b5cb95fd89220d6ed4125b3701f8705ac1; data SHA256 edf460e5a3fc84140528f35765ac21b94b966090d8f73e0e6740a2bba5d5c082.

Independent verification passed all saved metrics, exact splits/labels, six validation trials, validation-only thresholds and ten epochs. All 50 engineering tests pass. No convergence warnings or traceback found in the 60 saved run logs. 2,052 scientific result files / 453,216,445 bytes fetched; all SHA256 values in migration/stage011-result-manifest.json. Large aggregate fetch was interrupted; bounded per-fold retries retrieved all artifacts. All three jobs are CQ done/outputs-verified, not merely submitted.

Candidate AP: date .4369, stock .4847, combined .3732, style .2886. HGB: .5161/.5035/.4429/.3423. Price alignment improves over L1/rank/current paper-structure adapters, but the complete candidate loses to HGB everywhere, and no-SCL is better in all four regimes. No exact-paper reproduction, superiority over original0.675, real-intent detection, or CCF A achievement claim.

Archive blocker: last confirmed canonical main cfadd02a59ac44501dc53c044e1168994ed03b4a includes fresh data and old diagnostics. New scientific results/report are committed locally, with all CQ copies preserved; push fails because local IPv4 reports Network is unreachable while IPv6 works. Connected GitHub get_repo/fetch_commit reads work, but create_blob returned HTTP403 Resource not accessible by integration. User has been asked to restore IPv4; no credentials, network settings or other users' work were changed. Do not claim the new results are on GitHub yet.

Cleanup: 328 already-archived raw/old-diagnostic working copies removed only after their Git blobs matched confirmed remote cfadd02; fresh raw additionally independently hashed through CQ. Reclaimed 115,408,896 allocated bytes this cleanup; Git objects and remote archives remain. New unpublished result files and original iCloud placeholders remain untouched. Earlier cleanup reclaimed 38,699,008 allocated bytes.

Next required action: restore IPv4 and push local main, verify remote head equals local, then optionally remove verified result working copies. Scientific next round must preregister new independent dates and focus on direct supervised scoring, hard-negative controls and failure diagnosis; current test outcomes must not become a hidden tuning set.

中文结论：完整实验已结束且核验通过，当前方法尚未胜过强基线；本轮尚未完成的事项是新结果 GitHub 同步，原因是本机 IPv4 故障及连接器写权限不足。
