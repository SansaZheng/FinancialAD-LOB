# Reproduction and execution steps

1. Read `paper/workflow/current.md`, `docs/protocol.md` and `docs/data-contract.md`.
2. Acquire permitted data on authorized server storage through CQ. Record input
   hashes, license, real stock/date identities and event labels. Do not download
   bulk files to the Mac. An old metadata inventory does not establish backup.
3. Prepare source-versioned windows inside disjoint partitions; audit causal
   features and event leakage. Freeze actual date/stock fold tables. Files in
   `configs/*.engineering-example.json` are test examples, not production splits.
4. Qualify storage and inputs using the preflight CQ job, then build a project-only
   conda runtime, run CPU/GPU smoke, and only then submit dependent experiment
   batches. Bind every batch to the pushed code SHA and input manifest hash.
5. For each fold and seed, freeze a shared label subset. Fit preprocessing on
   training samples; all supervised controls use exactly the same labels. Run
   six validation trials per current tabular control. Record compute separately.
6. Add the original-paper reference only after its data/generator/settings are
   recovered. Qualify same-input TCN and Transformer controls before claiming
   gains from the candidate. Neural training/augmentation integration is pending.
7. Score frozen tests, save predictions/checkpoints/trials and calculate paired
   stock-date uncertainty, per-domain metrics and event-level operational metrics.
8. Archive permitted outputs in GitHub. Large files use Releases/LFS with download
   and checksum receipts. For restricted data record hashes/acquisition steps
   without making raw records public. Scan for credentials before publication.
9. Fetch a remote artifact independently and compare its SHA256 to the source.
   Only verified redundant local copies may be removed. iCloud placeholders are
   not physical payloads; unlinking them can delete the cloud copy as well.
10. Update the evidence map and workflow event log. Finish reports with a Chinese
    conclusion. Distinguish engineering tests, semi-synthetic experiments, exact
    reproduction and real-world validity.

中文结论：每个实验必须从合法可核验的数据、固定代码版本和公平协议开始，结果备份核验后才进行本地清理。
