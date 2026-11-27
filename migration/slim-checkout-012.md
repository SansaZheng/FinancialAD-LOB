# Mac partial-clone migration

After source commit57ab258 was pushed and independently confirmed with ls-remote, created an isolated `git clone --filter=blob:none --no-checkout` of the canonical GitHub repository. Sparse checkout includes every code/document directory, all non-CQ audit/report directories, and all completed/current stage012 benchmark, challenge and scoring job directories. Future queued job paths were included using `--skip-checks`.

Before installation, verified identical HEAD, clean tracked/untracked state in both checkouts, preservation of all old remote refs, exact Git blob hashes for every existing old tracked file, and byte equality for every retained file. Only already archived historical CQ results are omitted. No non-cache ignored files or local-only branches/stashes existed. The old checksum-clean checkout can then be removed after atomic path replacement; CQ jobs continue independently. The owned local result-fetch watcher alone was paused during replacement. The first verification refused to omit an early data-discovery notebook; all such audit directories were restored before proceeding.

Restore omitted data with `git sparse-checkout add results/cq-XXX/JOB`; Git fetches blobs from its promisor remote. The repository retains full commit/tree history but avoids downloading historical binary contents. Do not run a global sparse disable unless enough disk is available. Python environment `/Users/zyy/.local/share/financialad-lob/data-tools-venv` is unchanged.

中文结论：历史数据继续完整保留在GitHub与CQ，本地改为按需取回；代码、文档和当前实验所需文件保持一致。
