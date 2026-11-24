# Public data qualification — 2026-11-24

**Stage 009 update, 2026-11-25:** CQ job `j-1125-e0f1ad` completed acquisition
and replay of PKNORLEN, PKOBP and PZU prefixes on the same three dates. Combined
coverage is now five stocks, 15 stock-days, 61,440 messages and 480 snapshots,
with 61 crossed/locked snapshots flagged. 387 adjacent feature pairs survive
the endpoint checks. These remain unlabeled prefixes, not full trading sessions.
New outputs are in `results/cq-009/j-1125-e0f1ad/`; the earlier two-stock evidence
below is retained unchanged as the history of the first acquisition.

## Selected primary source: WSELOB-2017

[Adam Marszałek (2023), WSELOB-2017 v1, Mendeley Data](https://data.mendeley.com/datasets/3g4mhdp899/1),
DOI **10.17632/3g4mhdp899.1**, explicitly released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The release describes 2017 order messages and trades for KGHM, PEKAO,
PKNORLEN, PKOBP and PZU. The associated paper is
[Modeling of limit order book data with ordered fuzzy numbers](https://www.sciencedirect.com/science/article/pii/S1568494624003296).
The source release and its examples, rather than a third party's results,
define the schema used here.

**Actually verified:** all ten order/trade file locators, published byte sizes
and published SHA256 values from the primary API; hashes of the three downloaded
support files; direct HDF5 access to two stocks on three dates. Published full
file hashes are not represented as locally verified full-file hashes.

The public frontend exposes folder metadata at
`https://data.mendeley.com/public-api/datasets/3g4mhdp899/folders/1`.
Files are listed at `/public-api/datasets/3g4mhdp899/files?folder_id=FOLDER_ID&version=1`.
The earlier `/folders?version=1` guesses were incorrect. Metadata is archived in
`results/data-discovery-20261124/wselob-*-files.json` and
`data/manifests/wselob-source-locators.json`.

### Actual bounded ingestion and replay

KGHM and PEKAO, **2017-01-10, 2017-01-11, 2017-01-12**: first 4,096 contiguous
messages per stock/day, **24,576 messages total**, starting with `F` reset.
All six sample prefixes have nondecreasing timestamps. HDF5 metadata reports
698,002 rows across the six full partitions; those full partitions were not read.

Independent conservative order replay produced 192 snapshots (one per 128
messages), all with five displayed limit-price levels per side. **28 snapshots
are crossed or locked** and must be excluded from the continuous-session feature
path. Prefixes include retransmission and preopen/auction states. These samples
are not representative full-day evaluation data. No unknown modification or
deletion reference occurred in this replay.

Raw CSV prefixes, reconstructed snapshots, hashes and audits are in
`results/wselob-probe-20261124/` (KGHM) and
`results/wselob-probe-20261124-pekao/`. The first combined read stopped on an
HTTP range mismatch after KGHM; its audit preserves this interruption. A separate
PEKAO run completed, reading 786,432 response-body bytes. Transient responses
that ignore Range are closed without reading their full bodies. The reader now
allows at most three bounded retries and an 8 MiB body budget per stock.

The parser handles reset, retransmission, add, modify and delete events using
`symbol_idx + order_date + order_id`. `D` means deletion, **not verified cancellation
or spoofing**. The release's trade schema does not expose the same order identifier,
so exact order-level cancellation/execution attribution is not yet established.
Only explicit limit orders contribute to the current snapshot adapter; other
order types are counted as excluded. This adapter is an ingestion candidate,
not an independently validated exchange replay engine.

**Labels:** WSELOB does not provide confirmed manipulation labels. No AP, AUC-PR,
event recall or performance improvement is calculated from these unlabeled samples.
Later synthetic injections must be declared semi-synthetic, paired with normal
activity controls and held-out generator families. They cannot establish real
manipulation detection accuracy by themselves.

## Secondary candidate: Quant-Arena Public L1

[Publisher release](https://huggingface.co/datasets/Ashitemaru/Quant-Arena-Public-L1),
revision `fa85d7b95e56e81317ac349f52e916ca482f0f68`, claims CC BY-NC 4.0.
Its released manifest lists 289 A-share stocks, 2022–2023, up to 484 trading days,
131,889,757 rows and ten-level quotes at **15-second** intervals. Coverage varies
by stock; the manifest records it explicitly. The actual archive metadata was
retrieved with bounded byte ranges, including per-file checksums and LICENSE.
No Parquet market-data rows have been acquired or validated here.

This source remains **secondary and provenance-pending**: a publisher's license
statement alone does not independently establish exchange redistribution rights.
It also lacks individual order events and manipulation labels, and is too coarse
for subsecond spoofing claims. Do not substitute it for WSE event data. No bulk
download or scientific result is authorized by this document alone.

## Proposed expanded evaluation, before outcome inspection

After CQ storage/environment qualification and full source checksums, audit all
five WSE stocks and available dates. Candidate chronological periods are Jan–Mar
2017 train, April validation and May–June test; freeze exact valid session lists
after session-quality checks, without looking at detector outcomes. Cross-stock
evaluation uses five leave-one-stock-out folds, removing the held-out stock from
both training and validation. Combined evaluation also applies the date split.
Report per-stock/day scores and paired block uncertainty, not pooled windows alone.

The four existing supervised controls share labeled IDs and six validation-only
trials. OC-SVM and neural paper baselines, event semantics, continuous-session
filtering, realistic manipulation interventions, unseen-generator tests and matched
budget ablations remain to be implemented/qualified. No full experiment is claimed.

中文结论：已获得许可明确的事件级主数据源，并跑通两只股票、三个日期的真实样本回放；跨域训练、真实操纵标签和论文性能证据仍待补齐。
