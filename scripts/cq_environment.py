"""Read-only provider environment qualification; no shared environment mutations."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time

start = time.monotonic()
out = Path(os.environ["CQ_OUTPUT_DIR"])
out.mkdir(parents=True, exist_ok=True)
versions, errors = {}, {}
for name in ("numpy", "sklearn", "torch", "h5py"):
    try:
        module = importlib.import_module(name)
        versions[name] = module.__version__
    except Exception as error:
        errors[name] = type(error).__name__ + ": " + str(error)
files = ["lobbench/sequence_models.py", "lobbench/sequence_run.py", "lobbench/liquidity.py"]
report = {"passed": not errors, "python": sys.version, "platform": platform.platform(),
          "versions": versions, "errors": errors, "seconds": time.monotonic()-start,
          "max_rss_native_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          "source_sha256": {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in files},
          "evidence_class": "environment_qualification_only", "package_install_performed": False}
(out/"environment.json").write_text(json.dumps(report, indent=2)+"\n")
(out/"progress.txt").write_text("1/1 complete\n" if not errors else "0/1 missing dependencies\n")
print(json.dumps(report, indent=2))
sys.exit(0 if not errors else 1)
