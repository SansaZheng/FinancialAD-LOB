011b-frozen-matrix | Codex | running | configuration 6 | 2026-11-25T15:12:06.413704+00:00

Prompt: [011b](prompts/011b-frozen-matrix.md). Canonical GitHub: https://github.com/SansaZheng/FinancialAD-LOB.

Completed: fresh 15 stock-days collected (j-1125-8c5bef); 1,224,907 daily messages independently replayed and 1,500 snapshots matched (j-1125-41384c); 18,282 windows / 928 positive / 896 benign. Dataset SHA256 edf460e5a3fc84140528f35765ac21b94b966090d8f73e0e6740a2bba5d5c082. Full-batch CUDA and eleven-method fixture qualification passed on two T4 GPUs (j-1125-f2ce0f).

Fresh-date/style j-1125-161f04 completed: 10 fold-seed runs / 110 selected evaluations independently verified. Date mean AP: adapted cascade .0640; L1 .2065; price-aligned candidate .4369; no contrastive loss .4717; HGB .5161. These are partial-suite results, not a direct paper reproduction or superiority claim. Peak measured worker RSS 3,077,320 KiB in date seed0; two workers reserved 10GB RAM, including >30% margin. Peak allocated CUDA 213,105,664 bytes in that run; 1GB declared GPU allowance, provider supplies two isolated T4s.

Submitted remaining batches: stock j-1125-5788a5 and combined j-1125-58fc68, 25 fold-seed runs each. Same execution commit c34097d44f10ab42db7cd35b6d787ce4b055b8b8, unchanged frozen protocol. CQ handles shared placement. No paid rental or changes to unrelated jobs.

Stage010 date/style diagnostic j-1125-58f211 preserved; obsolete stock/combined never launched. GPU cancellation j-1125-c8115a confirmed.

Next: verify all remaining runs and paired strong-baseline contrasts, archive results, then clean only remotely verified owned working copies.

中文结论：首批新日期结果显示逐档信息有效，但当前候选模型仍落后于梯度提升；继续完成跨股票验证，不根据测试结果调整本轮方法。
