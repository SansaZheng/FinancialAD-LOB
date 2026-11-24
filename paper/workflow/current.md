# Current execution — 2026-11-24

008-cq-access-public-data | Codex | independent data work completed; CQ blocked
Configuration revision 5. Target: CCF A quality aspiration, venue undecided.
Canonical: https://github.com/SansaZheng/FinancialAD-LOB

CQ: today's retry again rejected the SansaZheng owner (HTTP 400); no job ID.
GitHub write access is present, but CQ's owner policy is separate. Supported
remedies and the concrete pending owner/admin action are in docs/cq-access.md.
No unrelated jobs, shared environments, policy settings or paid capacity changed.

Data: WSELOB v1 primary release explicitly CC BY 4.0; five stocks' order/trade
metadata matched to the primary API. Actual acquisition and deterministic replay
completed for KGHM and PEKAO on 2017-01-10/11/12: 24,576 event messages, 192
five-level snapshots, 28 crossed/locked snapshots flagged. Full source hashes
are not yet verified. Prefixes include retransmission/preopen states; no intent
labels or manipulation detection performance is inferred. Quant-Arena metadata
is archived as a secondary provenance-pending candidate, with no market rows read.

Code: bounded HTTP reader, WSE event parser/replay, acquisition/probe/audit scripts,
source manifest, CC attribution and steps. 26 engineering tests pass; full fetch
storage guards also rejected non-CQ and non-/date-or-/data invocation as intended.
No complete neural training pipeline or matched scientific benchmark has run.

Archiving: commit 594a829bef1856aa4f8ea66f13110fe3be3d1773 was pushed, independently
cloned and all 95 tracked files (3,117,531 bytes) matched SHA256. Receipt:
migration/github-verification-20261124.json. The verification clone was removed. Legacy 189 iCloud placeholders
are preserved; no claim of migration or old-data space reclaimed.

Next: account owner creates SuuTTT/FinancialAD-LOB execution fork or CQ admin
allows canonical repo; then check duplicates, pin pushed SHA, CQ storage preflight,
environment qualification, full WSE checksum acquisition, session/label audits,
and the registered date/stock fair-control and innovation/ablation experiments.

中文结论：真实公开多日多股票样本已读取并回放，数据接入不再停留在文献准备；CQ 仓库白名单仍是正式训练的外部阻塞，尚无超越原论文的证据。
