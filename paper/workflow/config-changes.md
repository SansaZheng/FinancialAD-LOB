# Configuration revision 5

2026-11-23, explicit user instruction: target CCF A, add fair baselines and
cross-date/cross-stock evaluation, innovate method, use CQ, archive research at
SansaZheng/FinancialAD-LOB and clear redundant Mac data.

Changed research route to `lob-generalization-v1`; specific venue remains null.
Canonical remote repository is the specified GitHub destination. New small
staging checkout is outside iCloud to avoid stalled reads and bulk hydration.
Previous revision 4 remains in the legacy directory unchanged; its bytes could
not be read this session, so no fabricated revision-4 snapshot is included here.
Paid-cloud budget remains unset. Only authorized `/date` and `/data` server
storage is allowed, subject to capacity and backing-filesystem checks.

Cleanup now explicitly requires an independently verified remote copy. This
preserves the user's data while honoring the request to remove redundant local
payloads. Actual legacy allocated bytes were zero, so no old-data space saving
was claimed.

中文结论：已按用户要求更新目标和归档位置；保留旧配置与旧数据，实际实验仍受 CQ 接入和数据条件约束。

## Revision6,2026-11-25
Route lob-generalization-v1 → lob-passive-lifecycle-v2. A concrete audit found474/2222 old injections with passive-volume truncation inside the visible book and46 with marketable inserted orders. Preserve old diagnostics; cancel only unstarted old-data stock/combined jobs; use fresh dates2017-01-16/17/18. Venue/topic unchanged. User already authorized continuing methodological improvements and CQ experiments.
