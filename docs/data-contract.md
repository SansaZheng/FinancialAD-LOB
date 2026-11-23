# Data contract and acquisition gates

Every JSONL row has `id`, `stock`, ISO `date`, `source_id`, numerical `start` and
`end` timestamps, `event_id` (null for ordinary background), binary `label`, and
numeric `features`. `source_id` identifies the immutable dataset lineage, not
an arbitrary per-window ID. Events and source hashes must survive every transform.

The manifest contains `sha256` of the exact JSONL bytes, ordered `feature_names`,
`evidence_class` (`synthetic_engineering`, `semi_synthetic`, `real_labeled`),
`features_use_future: false`, `generator_metadata_in_features: false`, and
`preprocessing: raw_or_window_causal`. These declarations require a source audit;
they are not established merely by setting booleans. Store source URLs, download
dates, hashes, tick size, timestamp units, session calendars, label definitions,
license, generator revision and partition recipe alongside them.

For timely event recall, positive rows additionally carry authoritative
`event_start` and `event_end` in the same timestamp units. An alert emitted after
the event ends is not a timely hit. Without these fields the runner reports only
`window_covered_event_recall` as a proxy and leaves `event_recall` null.

Never put IDs, stock names, date encodings, generator family, injected flags,
future cancellation times, labels or future returns into the feature vector.
Only data available by the endpoint may contribute. Normalization is fitted
inside the training pipeline. The same feature schema is shared by controls.

## Current acquisition status

* Original 2015 CSCO/TSLA/INTC benchmark: not available; exact reproduction blocked.
* Legacy public INTC sample: metadata inventory only in this session; Mac copy is
  an iCloud placeholder. Prior 2012 pilot is not the original benchmark.
* [Official LOBSTER samples](https://php.lobsterdata.com/info/DataSamples.php):
  five stock samples available; single-day samples alone cannot prove cross-date
  generalization. Download on authorized server storage after CQ qualification.
* [JFDS predecessor archive](https://zenodo.org/records/11048480): published MD5
  `5c44e0ee2adbcdf85309dc628252e077`. Source archive is not the multilevel 2025
  benchmark; preserve this distinction.
* [FI-2010 catalogue](https://etsin.fairdata.fi/dataset/73eb48d7-4dbc-4a10-a52a-da745b47a649):
  acquisition/license/identity boundaries not verified in this session. Consider
  for representation robustness, not as ground-truth manipulation labels.

Cross-date experiments stay blocked until multiple real trading dates with
verifiable stock/session identity are present. Do not manufacture dates or reuse
intraday segments as different days.

## Public GitHub storage

This repository is public. Code, protocols, non-sensitive aggregate outputs,
manifests and permitted synthetic fixtures belong in Git. Large redistributable
artifacts belong in versioned GitHub Releases/LFS with byte hashes and download
verification. Restricted raw market data stay on authorized server storage;
GitHub holds reproducible acquisition instructions and hashes instead.

LOBSTER's [terms page](https://php.lobsterdata.com/termsAndConditions.php) says
subscription terms are issued with the contract. Public availability of samples
is not an explicit redistribution grant. Raw uploads are therefore pending
license verification, not automatically assumed permissible.

中文结论：跨股票与跨日期需要真实可核验的分组信息；数据许可未确认前，公开仓库保存清单与重建步骤，不直接公开原始行情。
