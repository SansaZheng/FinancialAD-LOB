# Archive and cleanup status — 2026-11-23

The legacy project inventory covers 189 files excluding the Python environment,
Git internals and bytecode caches: 296,574,050 logical bytes, **0 allocated data
bytes** at inspection. These were iCloud dataless placeholders. SHA256 and remote
backup verification remain unset; no old source/result was treated as migrated.
Small reads of the old configuration and reference source timed out. The legacy
files remain unchanged. The generated inventory is not a copy of their contents.

The new independent staging checkout is outside iCloud. It contains only newly
implemented code, docs, small engineering logs and metadata. Its GitHub push and
remote verification are recorded separately in workflow state.

No old raw data were deleted; actual old-data bytes freed: **0**. Other projects,
shared environments and the iCloud account were not modified. Do not report the
291 MB apparent data size as recovered disk space. The Mac had approximately
414 MiB available at the first check, so no bulk download or dependency install
was started here.

Remaining steps: regain readable legacy contents or verify their lab copies via
CQ; review public redistribution permission; upload permitted artifacts; verify
remote hashes; remove only redundant physical local payloads. A broader Mac
cleanup would require identifying other user-owned data outside this project.

中文结论：旧 LOB 文件尚未完成内容备份，且目前不占实际数据空间；没有盲目删除，也没有虚报释放空间。
