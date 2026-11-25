# WSE complete-day semi-synthetic benchmark, stage010

Source: Marszałek (2023), WSELOB-2017 V1, DOI10.17632/3g4mhdp899.1,
CC BY4.0. Attribution and source notices: [ATTRIBUTION](../data/ATTRIBUTION.md).
This project neither owns exchange intent ground truth nor claims source endorsement.

## Acquired and verified

Five stocks: KGHM, PEKAO, PKNORLEN, PKOBP, PZU.
Three dates:2017-01-10,2017-01-11,2017-01-12.
All1,474,126 rows of these15 source daily HDF partitions were retained;
1,438,568 event snapshots fall within the09:00–16:50 Europe/Warsaw clock filter.
8,934 snapshots are incomplete or crossed/locked and remain flagged in the
archive. Full daily source messages, including pre-open/closing phases, are
retained separately. This is a clock filter, not authoritative exchange-phase
or volatility-halt information.

CQ acquisition `j-1125-5d4369` pinned47175c4; subsequent CQ verification
`j-1125-344a3f` pinned a753e6f independently replayed every source message and
compared100 snapshots per stock-day (1,500 total) with the slower reference book.
Every comparison passed. All30 raw/book compressed files have matched SHA256
receipts. These are full **selected daily partitions**, not verified complete
annual archives; the original full-archive hash is not claimed.

Archives:
`results/cq-010/j-1125-5d4369/full-sessions/` (38.6MB total, each file<=4.1MB).
Source-time correspondence and independent checks:
`results/cq-010/j-1125-344a3f/benchmark/full-day-validation.json`.

## Generated examples

25 contiguous valid event snapshots, stride64; invalid books, missing source
rows and gaps>60seconds break windows. 22,206 accepted windows;274 rejected.
Window source segments do not overlap. Positive labels:1,141. Benign injected
controls:1,081. Remaining19,984 windows are untouched background with unknown
real-world intent. Label0 means no injected positive style, not certified
absence of real manipulation.

Generator seed17086, version`wse-event-overlay-v1`. Labels distinguish layered
or staggered withdrawal patterns from persistent or independently withdrawn
liquidity additions and untouched background. All injected groups use the same
side and volume distributions; volumes are integer shares, at least two levels
must be visible, and orders are tracked by absolute price within the observed
five levels. No matching engine, bona-fide executions, or endogenous price
response is generated. This is an event-time snapshot-overlay benchmark, not
an exact implementation of the target paper's millisecond order injection.

The complete injection ledger is archived for auditing and is never given to
predictors. Neither stock/date IDs nor style names enter models. Eight manual
execution/cancellation channels are unavailable and uniformly zero across all
classes. Deletion events are not relabeled as cancellations. Observed book
changes are called liquidity additions/removals, not proven order intentions.

Dataset:
`results/cq-010/j-1125-344a3f/benchmark/benchmark.npz` (9,176,524bytes).
SHA256:`3c1b76a7a82acff1c689f397b359b2a96b3620918e8d515a1c0be6cd47018009`.
Numeric/fixed-string arrays only; load with`allow_pickle=False`.
Features: raw(N,25,20), manual(N,25,13), aligned/rank(N,25,12).
Metadata: y, stock, date, id, kind, start_ns, end_ns. The latter fields are used
only for fixed partitions and auditing/metrics, never as model input features.

## Fixed evaluation and limitations

See [registered settings](../configs/010-preregistered.json) and
[reproduction fidelity](../paper/010-reproduction-fidelity.md).
Date splits are chronological; stock and combined tests hold out entire stocks.
Style tests hold out staggered positives from training/validation. All same-source
windows remain in the same partition; there are no split-across-set clean/injected
twins. Fitted normalizers and one-class detectors use training only; validation
AP selects among six fixed trials. Test metrics cannot change these choices.

The source paper's0.675 is not directly comparable: markets, dates, label prevalence,
injection mechanics, manual-feature availability, architecture budget and score
aggregation differ. Three dates and synthetic patterns are insufficient evidence
of reliable real-world intent detection or a CCF A-level research contribution.

中文结论：已获得可追溯的完整日数据和明确标注为半合成的22,206个窗口，可用于固定协议比较；真实操纵标签、更多独立日期和原论文同数据复现仍待补齐。
