# Stage012 fresh-date benchmark

Source: Marszałek, WSELOB-2017 V1, DOI10.17632/3g4mhdp899.1, CC BY4.0. Preserve [attribution](../data/ATTRIBUTION.md). Raw selected HDF partitions were acquired through bounded HTTP ranges and archived as lossless numeric NPZ derivatives. The full annual archive hash is not verified; every selected file has its own hash.

Five stocks: KGHM, PEKAO, PKNORLEN, PKOBP, PZU. Training dates:2017-01-19,20,23. Validation:24,25,26. Test:27,30,31. All45daily partitions contain3,439,144source rows, all independently replayed;4,500reference snapshots match. Source CQ jobs: j-1127-d4d017 (train), j-1127-636ebd (validation), j-1127-d531e0 (test). The benchmark job is j-1127-1d410b. Source manifests, source-shards.json and independent receipts disambiguate the three acquisitions.

Full daily source partitions were replayed; derived25-event windows are restricted to09:00–16:50 Europe/Warsaw with64-event stride. Persistent passive overlays use generator seed17088. There are51,118retained windows,2,539positive policy labels and2,459benign controls;796invalid source windows and73newly marketable overlays are excluded. Eleven primary observational collisions remain recorded. These are generated policy labels, never adjudicated manipulation intent.

Benchmark: results/cq-012/j-1127-1d410b/benchmark/benchmark.npz, SHA25601213ddbaf0ffc19d31d43ce4793839031c283b3ef241abc6a21b31472cc8d2d. The benchmark directory includes per-stock/day ledgers, manifest and full-day validation. GitHub stores every selected raw partition, reconstructed book, derived window, audit and injection ledger; sparse local checkouts omit historical binaries until explicitly restored.

The chronological fold separates all three date blocks. Each combined fold additionally holds out a test stock and a different validation stock; training excludes both. It tests simultaneous stock/date transfer rather than using the held-out stock's prior-day training data. Thirty fold-seeds use five fixed training seeds across six folds. Test evidence contains only three dates and15stock-days regardless of the number of model executions. This stage adds nine distinct source dates to earlier stages, reaching15source dates overall, not the20-date planning target.

The secondary lifetime challenge is a different test overlay on the same source windows, not an independent dataset. Seed17089 independently reverses each benign-wave level's removal offset while preserving placement, volume, source and center. It contains15,852common-ID windows:384changed controls,55retained positive-pattern collisions,one additional marketability exclusion. All15,468other inputs match byte-for-byte. Equal per-level lifetime marginals hold in the generator distribution before censoring, not necessarily in finite retained samples. Challenge hash053af4c6530bb41ebaca935a5b653cda372cdba25ba691468f753bb5f7fb3260; source job j-1127-d406c2.

The benchmark has no counterfactual market response to injected orders, no authoritative order identities or manipulator intent, one market, and one fixed seed per generator. It does not reproduce the source paper's private LOBSTER labels or inputs. All comparisons must be within a matched cohort/protocol; AP is distinct from trapezoidal PR AUC.

中文结论：本轮新增九日、五股票的完整源数据及半合成基准可追溯，但测试独立日期只有三天，标签仍不能代表真实操纵意图。
