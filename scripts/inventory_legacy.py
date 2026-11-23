"""Metadata-only inventory: never hydrate iCloud placeholders or follow symlinks."""
import argparse
import hashlib
import json
import os
import stat
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("root")
p.add_argument("--output", required=True)
a = p.parse_args()
root = Path(a.root).resolve()
rows = []
for folder, dirs, files in os.walk(root, followlinks=False):
    dirs[:] = [d for d in dirs if d not in (".git", ".venv", "__pycache__")]
    for name in files:
        path = Path(folder) / name
        s = path.lstat()
        dataless = bool(getattr(s, "st_flags", 0) & 0x40000000)
        rows.append({"path": str(path.relative_to(root)), "logical_bytes": s.st_size,
                     "allocated_bytes": s.st_blocks * 512, "dataless": dataless,
                     "symlink": stat.S_ISLNK(s.st_mode), "sha256": None,
                     "backup_verified": False, "deletion_allowed": False})
Path(a.output).write_text(json.dumps({"scope": "legacy LOB project only; excludes environment and caches",
    "inventory_is_not_a_backup": True, "files": rows,
    "logical_bytes": sum(r["logical_bytes"] for r in rows),
    "allocated_bytes": sum(r["allocated_bytes"] for r in rows)}, indent=2)+"\n")
print(f"{len(rows)} artifacts inventoried without reading contents")
