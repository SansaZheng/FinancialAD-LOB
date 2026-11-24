---
license: cc-by-nc-4.0
pretty_name: Quant-Arena Public L1
language:
- en
tags:
- finance
- quantitative-finance
- market-microstructure
- limit-order-book
- time-series
- benchmark
- llm-agents
task_categories:
- time-series-forecasting
size_categories:
- 100M<n<1B
---

# Quant-Arena Public L1

Quant-Arena Public L1 is the public market-data release used by the
Quant-Arena benchmark. It contains Level-2 order-book quotes (ten-level
bid/ask snapshots) for a fixed universe of 289 China A-share stocks,
resampled to a regular 15-second grid for every trading day from
2022-01-01 to 2023-12-31 (484 trading days). No data from 2024 or later is
included.

- Stocks: 289 (a seeded 10% sample of 2,894 A-share stocks with codes `00xxxx` and `30xxxx`)
- Rows: 131,889,757
- Columns: 45 (`symbol`, `available_at`, `source_event_time`, ten levels of bid/ask price and volume, `missing_depth`, `stale`)
- Format: Parquet (zstd), one file per stock, about 6.23 GB

Values are the exchange's published snapshots. No order book is rebuilt and
nothing is interpolated or adjusted. Each row uses only information
available at its `available_at` timestamp. The full data card (schema,
sampling rule, null conventions, flags) is `README.md` inside the archive,
and per-file row counts, sizes, hashes and date coverage are in
`manifest.json`.

## Files in this repository

| File | Content |
|---|---|
| `quant-arena-public-l1-v1.tar` | Plain tar archive of the release directory `quant-arena-public-l1-v1/` |
| `quant-arena-public-l1-v1.tar.sha256` | SHA-256 of the archive |
| `README.md` | This card |

Inside the archive:

```
quant-arena-public-l1-v1/
  <symbol>.parquet   289 files, e.g. 000012.SZ.parquet
  manifest.json      release metadata, schema, per-file rows/bytes/sha256/date range
  SHA256SUMS         checksums of every file in the directory
  README.md          full data card
  LICENSE            CC BY-NC 4.0 legal text
```

## Download and verify

```bash
huggingface-cli download Ashitemaru/Quant-Arena-Public-L1 --repo-type dataset --local-dir quant-arena-l1
cd quant-arena-l1
sha256sum -c quant-arena-public-l1-v1.tar.sha256
tar -xf quant-arena-public-l1-v1.tar -C .
cd quant-arena-public-l1-v1 && sha256sum -c SHA256SUMS
```

(Equivalently, from the parent directory: `tar -xf quant-arena-l1/quant-arena-public-l1-v1.tar -C quant-arena-l1`.)

## Reading the data

```python
import polars as pl
df = pl.scan_parquet("quant-arena-l1/quant-arena-public-l1-v1/*.parquet").collect()
```

Prices are `decimal128(28, 4)` in CNY per share; volumes are `int64` shares;
timestamps are `Asia/Shanghai` (UTC+08:00). An empty book level is null in
both its price and volume columns.

## Licence

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).
See https://creativecommons.org/licenses/by-nc/4.0/legalcode.

## Disclaimer

This dataset is provided for research and educational purposes only, "as is",
without warranty of any kind. Nothing in it is investment advice.

## Citation

If you use this dataset, please cite:

```bibtex
@misc{quantarena2026,
  title  = {Quant-Arena: Benchmarking LLM Agents for Quantitative Trading Research},
  author = {TBD},
  year   = {2026},
  note   = {Citation details to be added}
}
```
