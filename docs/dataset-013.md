# Stage013 fresh dates and common-cohort controls

Source: Marszałek, WSELOB-2017 V1, DOI10.17632/3g4mhdp899.1, CC BY4.0. Retain [attribution](../data/ATTRIBUTION.md). Selected HDF partitions are stored as numeric NPZ derivatives with per-file hashes. Numeric values and field names are retained; the original annual-container hash and HDF dtype metadata are not claimed preserved.

Five stocks: KGHM, PEKAO, PKNORLEN, PKOBP, PZU. Train:2017-02-01,02,03; validation:02-06,07,08; test:02-09,10,13,14,15,16. All60stock-days contain4,712,637source rows. Four original acquisitions are j-1128-a02e9d,j-1128-a5de09,j-1128-dcd9a2,j-1128-3545ea; scripts.verify_source_archives independently confirms their SHA256, complete declared row counts and causal book/source indices. CQbenchmark job j-1128-e7a9cf must separately replay every source row and compare100reference snapshots per stock-day before producing labels. Its completion receipt, rather than this plan, establishes that gate.

The unchanged passive generator forms25-event windows,64-event stride,09:00–16:50 Europe/Warsaw, with frozen seed17090. Labels describe injected observable order policies, not adjudicated manipulator intent. The final manifest records exclusions, controls, collisions, per-day windows and benchmark hash. All methods receive identical source IDs, labels, train caps, date/stock splits and validation-selection rules. The combined fold excludes both test and separate validation stocks from training; it measures joint date/stock transfer.

Stage013 adds12new source dates to the prior15, reaching27source dates overall. It contains six distinct test dates and30test stock-days, not420independent markets. Distinct dates can remain serially dependent. One market and one generator family remain; the10dataset and recent-published-baseline planning targets remain unmet. Source days from older stages are development evidence and are not pooled into the new test estimate.

The generator has no market response to injected orders, no authoritative intent labels, and no guarantee that every legitimate burst resembles its benign controls. Original-paper private LOBSTER data are absent. This cohort cannot establish a direct improvement over the original0.675. AP and trapezoidal PR AUC are separately retained, never substituted.

中文结论：新日期将完整源数据覆盖扩展到27天，但本轮测试证据仍只有六个不同日期、五只股票和一个市场；半合成标签不能替代真实操纵标签。
