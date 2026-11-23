"""Small, bounded CPU qualification. Never a financial benchmark result."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

out = Path(os.environ["CQ_OUTPUT_DIR"])
out.mkdir(parents=True, exist_ok=True)
start = time.monotonic()
result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                        capture_output=True, text=True, timeout=90)
(out / "tests.log").write_text(result.stdout + result.stderr)
(out / "progress.txt").write_text("1/1 completed\n" if result.returncode == 0 else "0/1 failed\n")
(out / "qualification.json").write_text(json.dumps({"passed": result.returncode == 0,
    "evidence_class": "engineering_only", "seconds": time.monotonic()-start}, indent=2)+"\n")
sys.exit(result.returncode)
