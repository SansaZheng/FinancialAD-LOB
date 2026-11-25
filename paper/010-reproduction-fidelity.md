# Stage 010: reproduction fidelity and fixed evaluation

Primary target: [Lin & Yang arXiv 2508.17086v2](https://arxiv.org/html/2508.17086v2), Appendix A. The paper reports best AUC-PR 0.675 on its LOBSTER-based semi-synthetic benchmark. That value is context, not a valid numerical superiority threshold for WSE.

We implement the described cascade: MSE-pretrained multilevel LOB Transformer, frozen representation, concatenated manual features, fusion autoencoder trained with reconstruction plus the paper's log-positive-sum contrastive loss, then a normal-training-embeddings-only OC-SVM or Isolation Forest. Original JFDS predecessor code is preserved under `vendor/jfds_reference`, with its independent source receipt. The 2025 paper's complete author implementation and original labeled dataset have not been acquired.

| Item | Current implementation and deviation |
|---|---|
| Data | Complete selected WSE 2017 daily order partitions, 5 Polish stocks × 3 days; not the paper's 3 US stocks on one date. CC BY 4.0, [Mendeley source](https://data.mendeley.com/datasets/3g4mhdp899/1). |
| Continuous session | Europe/Warsaw 09:00–16:50, end exclusive; clock filter only. A contemporaneous [2016 trading guide](https://www.keplercheuvreux.com/app/uploads/2020/07/Traders_Guide_UK_24.08.2016.pdf) lists these hours. No exchange phase or halt feed; invalid/crossed states are excluded and break windows. Complete source daily rows remain archived. |
| Labels | Explicit event-time snapshot-volume overlays; no matching engine, execution simulation, endogenous market response, or real-world intent ground truth. Background intent is unknown. |
| Injection ambiguity | Appendix says BidPrice1/AskPrice1 ≥1.0008, impossible for an uncrossed book; also text/table discrepancies in price offset and interarrival ranges. We do not silently repair these and call the result exact reproduction. |
| Controls | Positive layering/staggered withdrawal and benign persistent/independent additions share volume and side distributions. Ledger fields never enter predictors. An observational pattern cannot establish trader intent. |
| Timing | 25 contiguous event snapshots, stride64, spread-normalized prices and log volumes. Injection is in event steps, not paper millisecond timestamps. No oversampling of test examples. |
| Manual features | Best bid/ask log returns, their differences and log time delta available. Eight trade/cancel channels are uniformly unavailable/zero. WSE deletion D is not interpreted as cancellation. |
| JFDS architecture | Same preserved Transformer class and portable teacher-forced decoder; compact width64/FF128/layers2/heads8 rather than predecessor width128/FF512/layers6. Device adaptation is explicit. |
| Training | Paper sequence25, batch256, Adam1e-4, 10 epochs per stage. Alpha0.1 and temperature0.1 are registered assumptions, not recovered author settings. Full generated training supervision (~5% positives) differs substantially from paper ~0.03%. |
| Fusion capacity | Hidden width chosen by input dimension so all fusion variants have approximately200k parameters, within1%; same labels, batch schedule, epochs and six detector-selection trials. |
| Evaluation | Window AP and trapezoidal PR AUC both reported; no paper pointwise overlap aggregation. Date, stock, combined and held-out-style tests fixed before first results. |

Method hypothesis: price-aligned observed liquidity addition/removal sequences better preserve temporal synchronization than changes by rank, improving generalization to a held-out stock/date/style. They are **observed depth changes**, not identified cancellations. The rank-aligned and no-contrastive/no-LOB ablations test this hypothesis. A raw-window OC-SVM and dynamics OC-SVM challenge whether the learned cascade is needed. Failure to improve is reported; no test-feedback tuning is permitted on this frozen suite.

All splits are source-stock/date based. Every background segment is used once; no clean/injected twins are split across sets. Five seeds repeat initialization and training; they do not create five independent markets. A small number of dates remains a material limitation for a CCF A claim.

中文结论：本阶段是有明确复现差异记录的 WSE 半合成外部评测；只有在相同数据、划分、标签预算下稳定优于级联基线，才能声称该方法在此协议上改进。不能据此宣称精确复现或真正超过论文的 0.675。
