# Progress report / 进展报告 — 2026-11-24

CQ access was prioritized and retried after checking the queue and GitHub rights.
It still rejects SansaZheng-owned source repositories with HTTP 400; no job ID
was issued. The proposed SuuTTT execution fork is absent. The connector does
not expose fork creation, and browser inspection did not provide a usable
SuuTTT login. Exact allowlisting or an owner-created fork is the pending action.
The canonical archive remains SansaZheng/FinancialAD-LOB.

**已执行的数据工作：** WSELOB-2017 主站明确提供 CC BY 4.0 许可。五只股票的
订单/成交文件元数据已核对；KGHM 和 PEKAO 在 2017-01-10、11、12 的六个
真实分区各读取 4,096 条消息，共 24,576 条。独立回放生成 192 个五档快照，
全部具备五档深度，28 个交叉或锁定盘口被标记。样本包含重传和开盘前状态，
不能直接作为连续交易时段评测集，更不包含真实操纵意图标签。

Saved artifacts include raw permitted CSV prefixes, reconstructed JSON snapshots,
per-file hashes, source/license metadata, data-ingestion and replay audits, a
bounded range reader, event replay adapter, CQ-only full acquisition command,
and exact steps. The first combined read's HTTP range failure is preserved;
PEKAO then completed in a separate bounded run. The full 2017 files were not
copied to the Mac. No full-source SHA256 verification is claimed yet.

Quant-Arena's pinned release manifest and license were extracted from its large
archive using ranges. It lists 289 stocks and up to 484 days, but its 15-second
quotes do not replace event-level spoofing data. Redistribution provenance remains
pending and no market-data rows from it have been validated.

26 bounded CPU engineering tests pass. Two full-download guard checks reject
non-CQ execution and paths outside /date or /data. These are implementation/data
checks, not scientific evidence of AP improvement. Formal CQ environment, full
acquisition, session filters, labeling controls, neural baselines, cross-domain
performance and methodology ablations remain incomplete.

中文结论：本轮已完成真实多日多股票数据的小样本读取、回放和工程验证，所有新证据将随代码存档；CQ 接入仍需管理员放行或创建执行镜像，不能宣称已复现或超越原论文，也不能宣称已达到 CCF A 录用水平。
