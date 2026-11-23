"""CQ read-only qualification of legacy inputs and authorized output storage.

This does not train or claim that legacy files are verified backups. Hashing bulk
data is a separate bounded job after storage, permission and ownership checks.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

out = Path(os.environ["CQ_OUTPUT_DIR"])
out.mkdir(parents=True, exist_ok=True)
resolved = out.resolve()
allowed = any(resolved == Path(r) or Path(r) in resolved.parents for r in ("/date", "/data"))
disk = shutil.disk_usage(out)
result = {"evidence_class": "engineering_only", "output_storage_allowed": allowed,
          "output_realpath": str(resolved), "free_bytes": disk.free,
          "minimum_free_bytes": 60 * 1024**3, "legacy_locations": []}
for raw in ("/date/zyy/FinancialAD/lob-manipulation", "/data/zyy/FinancialAD/lob-manipulation"):
    # stat runs in a bounded subprocess; a stale NFS path must not freeze preflight.
    code = "import os,json; p=" + repr(raw) + "; print(json.dumps({'path':p,'exists':os.path.isdir(p)}))"
    try:
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=5)
        result["legacy_locations"].append(json.loads(r.stdout) if r.returncode == 0 else {"path": raw, "error": "stat failed"})
    except subprocess.TimeoutExpired:
        result["legacy_locations"].append({"path": raw, "error": "stat timeout"})
result["storage_passed"] = allowed and disk.free >= result["minimum_free_bytes"]
(out/"preflight.json").write_text(json.dumps(result, indent=2)+"\n")
(out/"progress.txt").write_text("1/1 preflight checked\n")
print(json.dumps(result))
sys.exit(0 if result["storage_passed"] else 2)
