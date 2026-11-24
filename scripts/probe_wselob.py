"""Read bounded, contiguous public WSE prefixes; no training or intent labels.

Run with python -m scripts.probe_wselob --output results/wselob-probe-YYYYMMDD.
Dependency: h5py==3.12.1. Source HDF attributes are never unpickled.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

from lobbench.http_range import HTTPRangeFile


def probe(source_manifest, output, stocks, days, rows):
    output.mkdir(parents=True, exist_ok=True)
    source = json.loads(source_manifest.read_text())
    report = {"status": "partial", "requested_stocks": stocks, "requested_days": days,
              "evidence_class": "real_public_data_ingestion_only", "dataset": source["dataset"],
              "source_url": source["source_url"], "license": source["license"],
              "attribution": source["attribution"], "h5py": h5py.__version__,
              "numpy": np.__version__, "label_status": "No manipulation labels provided or inferred",
              "sampling": "First contiguous rows per requested stock/day; not random or representative",
              "full_source_hash_verified": False, "partitions": [], "transfers": []}
    for stock in stocks:
        spec = source["files"][stock]
        remote = HTTPRangeFile(spec["url"], spec["bytes"], max_bytes=8*1024**2,
                               headers={"User-Agent": "Mozilla/5.0", "Referer": source["source_url"]})
        with h5py.File(remote, "r") as hdf:
            for day in days:
                table = hdf["d" + day.replace("-", "")]["table"]
                values = table[:min(rows, len(table))]
                fields = values.dtype.names
                if values.dtype.hasobject:
                    raise ValueError("Object dtype is not accepted")
                path = output / f"{stock}-{day}-prefix.csv"
                with path.open("w", newline="") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(fields)
                    for row in values:
                        writer.writerow([v.decode("ascii") if isinstance(v, bytes) else int(v) for v in row])
                item = {"stock": stock, "date": day, "source_rows": len(table),
                        "sample_rows": len(values), "fields": list(fields),
                        "action_counts": dict(Counter(x.decode("ascii") for x in values["action_type"])),
                        "symbol_ids": sorted(set(map(int, values["symbol_idx"]))),
                        "time_ns_min": int(values["time"].min()), "time_ns_max": int(values["time"].max()),
                        "timestamp_backsteps": int(np.sum(np.diff(values["time"]) < 0)),
                        "first_action": values[0]["action_type"].decode("ascii"),
                        "sample_file": path.name, "sample_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                report["partitions"].append(item)
                (output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
                print(f"{stock} {day}: {len(values)}/{len(table)} rows; {item['action_counts']}", flush=True)
        report["transfers"].append({"stock": stock, "bytes": remote.downloaded, "requests": remote.requests,
                                    "range_rejections": remote.range_rejections,
                                    "source_size": spec["bytes"], "full_file_downloaded": False})
        (output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
        remote.close()
    report["status"] = "complete"
    (output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source-manifest", type=Path, default=Path("data/manifests/wselob-source-locators.json"))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--stocks", nargs="+", default=["KGHM", "PEKAO"])
    p.add_argument("--days", nargs="+", default=["2017-01-10", "2017-01-11", "2017-01-12"])
    p.add_argument("--rows", type=int, default=4096)
    args = p.parse_args()
    if not 0 < args.rows <= 10000 or len(args.stocks) > 5 or len(args.days) > 3:
        p.error("Bounded probe permits <=10000 rows, <=5 stocks and <=3 dates")
    probe(args.source_manifest, args.output, args.stocks, args.days, args.rows)
