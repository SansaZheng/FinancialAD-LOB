# Fresh-date passive-order benchmark

Source: Adam Marszalek, WSELOB-2017, DOI 10.17632/3g4mhdp899.1, CC BY 4.0. Source link and immutable selected-file hashes appear in the full-session audit. Five stocks: KGHM, PEKAO, PKNORLEN, PKOBP, PZU. Three fresh dates: January 16–18, 2017. The January 10–12 stage010 cohort remains diagnostic and is not pooled.

The complete 15 source daily tables contain 1,224,907 messages. Replayed continuous-session snapshots: 1,189,279, of which 7,775 are incomplete or crossed/locked. The 09:00–16:50 Europe/Warsaw clock filter does not identify halts or all exchange phases. All daily raw rows remain archived; evaluation uses 25 contiguous-event windows at stride 64, excluding invalid snapshots or gaps over 60 seconds.

The resulting 18,282 windows contain 928 generated positive policies and 896 benign-control policies; 268 source-invalid windows and 35 marketability cases are excluded. The latter censoring rule applies to both classes. Seven random benign policies coincide with positive observable withdrawal patterns and remain in the dataset. Neither class establishes real trader intent. Snapshot additions do not cause endogenous market reactions or matching-engine fills.

Active synthetic quantities persist at their actual prices even when the base price level disappears; 1,728 such retained visible level-steps occur. Features include raw top-five books, five available manual indicators, and 40 depth-resolved price-aligned flow/coverage channels per event. Eight unavailable execution/cancellation fields are excluded consistently. Identifiers, dates, stocks, generator style and intervention ledger are metadata, never model predictors.

Archive: `results/cq-011/j-1125-8c5bef/full-sessions` (raw and books); `results/cq-011/j-1125-41384c/benchmark` (derived arrays, ledger, manifest and independent replay receipts). Dataset SHA256: `edf460e5a3fc84140528f35765ac21b94b966090d8f73e0e6740a2bba5d5c082`. CQ replay checked every daily message and 1,500 reference snapshots; full annual archive checksums were not verified because only bounded daily ranges were retrieved.

All files are independently attributed and individually below GitHub's regular-file size limit. The data are a public semi-synthetic research benchmark, not original LOBSTER2015 paper data or real manipulation adjudications.

中文结论：已补齐 15 个新股票交易日并生成可追溯半合成标签；数据的完整性和重放已验证，但只有 3 个新日期，且没有真实操纵意图标注。
