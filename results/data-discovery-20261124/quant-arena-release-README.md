# Quant Arena L1: A-share ten-level quotes at 15-second resolution, 2022-2023

## What this is

L1 is a public sample of exchange order-book quotes for China A-share stocks.
For a seeded 10% sample of stocks it gives the exchange's own ten-level
bid/ask snapshots, resampled to a regular 15-second grid, for every trading
day from 2022-01-01 to 2023-12-31.

The values are the exchange's published snapshots. No order book is rebuilt
and nothing is interpolated or adjusted. Prices are not adjusted for splits
or dividends.

## Files

| File | Content |
|---|---|
| `<symbol>.parquet` | One file per stock (for example `000012.SZ.parquet`) with all of its trading days. Parquet, zstd compression, row groups of 8,192 rows. |
| `manifest.json` | Release name, sampling policy, seed and symbol list, date range, schema, availability rule, and per-file row count, byte size, sha256 and first/last day. |
| `SHA256SUMS` | Checksums in `sha256sum` format. Verify with `sha256sum -c SHA256SUMS`. |
| `README.md` | This data card. |
| `LICENSE` | Creative Commons Attribution-NonCommercial 4.0 International legal text. |

## Coverage

- Market: A shares (codes `00xxxx` and `30xxxx`). B shares, funds and bonds are excluded.
- Dates: 2022-01-01 to 2023-12-31 (484 trading days). No data from 2024 or later.
- Stocks: 289 of 2,894 stocks (10%).
- Rows: 131,889,757 in total. Compressed size: 6.23 GB (6,229,746,952 bytes).
- Stocks listed or delisted during the range are included for the days they traded, so some files cover fewer days than others (see `first_day`, `last_day` and `trading_days` in `manifest.json`). Days on which a stock was suspended have no rows.

## Sampling

The population is every A-share stock with codes `00xxxx` and `30xxxx`
with at least one exchange quote snapshot on any trading day of the range,
delisted and newly listed stocks included: 2,894 stocks.

Each stock is ranked by `sha256("<seed>:<symbol>")` (lowercase hex digest,
UTF-8), and the round(10%) stocks with the lowest digests are kept. The
seed is `quant-arena-l1-20261019` and was fixed before the release was built.
The list of selected symbols is in `manifest.json` under `sampling.symbols`.

## Schema

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `symbol` | string | | Exchange-qualified code, for example `000012.SZ` |
| `available_at` | timestamp[ns, tz=Asia/Shanghai] | China Standard Time (UTC+08:00) | The 15-second boundary this row describes |
| `source_event_time` | timestamp[ms, tz=Asia/Shanghai] | China Standard Time (UTC+08:00) | Exchange timestamp of the snapshot used; never later than `available_at` |
| `bid_price_1` ... `bid_price_10` | decimal128(28, 4) | CNY per share | Bid price at levels 1 (best) to 10 |
| `bid_volume_1` ... `bid_volume_10` | int64 | shares | Total bid quantity at that level |
| `ask_price_1` ... `ask_price_10` | decimal128(28, 4) | CNY per share | Ask price at levels 1 (best) to 10 |
| `ask_volume_1` ... `ask_volume_10` | int64 | shares | Total ask quantity at that level |
| `missing_depth` | bool | | The best bid or the best ask (level 1) is empty |
| `stale` | bool | | The snapshot used is more than 15 seconds older than `available_at` |

There are 45 columns. All files share the same schema.

## 15-second sampling rule

Only snapshots inside the regular trading sessions are used. Each session of
each day is resampled on its own:

1. Boundaries are the multiples of 15 seconds of the clock, from the first boundary at or after the session's first snapshot to the first boundary at or after its last snapshot (never past the session end).
2. A row at boundary `t` takes the latest snapshot stamped at or before `t` within the same session of the same day. When several snapshots share a timestamp, the last one the exchange published is used.
3. Nothing is carried across sessions: the first row of a session never reuses a snapshot from an earlier session, and no day reuses the previous day's book.

A row therefore uses only information available at `available_at`. When no
new snapshot arrived for more than 15 seconds the previous one is repeated
and `stale` is true. The exchange publishes a snapshot every few seconds when
something changes and less often otherwise, so `stale` is frequent on thinly
traded stocks.

## Nulls and flags

- The exchange encodes an empty book level as zero price and zero volume. L1 publishes an empty level as null in both its price and volume columns: a level is either fully present or fully null. Prices and volumes are never zero.
- `missing_depth` is true when level 1 of the bid or of the ask is null (no best bid or no best ask, for example at limit-up/limit-down or during an auction). Gaps at deeper levels are visible only as nulls in those columns.
- `stale` is described above.

## Row order

Each file holds one stock. Rows are ordered by `symbol`, then `available_at`
ascending, so concatenating the files in symbol order gives one table ordered
by symbol and time.

## Reading the data

```python
import pyarrow.parquet as pq
table = pq.read_table("000012.SZ.parquet")
df = table.to_pandas()          # prices become decimal.Decimal objects
```

```python
import polars as pl
df = pl.scan_parquet("*.parquet").filter(pl.col("missing_depth").not_()).collect()
```

## Licence

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).
See `LICENSE` or https://creativecommons.org/licenses/by-nc/4.0/legalcode.

## Disclaimer

This dataset is provided for research and educational purposes only. It is
provided "as is", without warranty of any kind, including accuracy,
completeness or fitness for a particular purpose. Nothing in it is
investment advice or a recommendation to buy or sell any security. Past
market data does not indicate future results.
