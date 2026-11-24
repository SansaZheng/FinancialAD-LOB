"""Replay saved contiguous prefixes and write deterministic diagnostics."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from lobbench.wselob import WSEBook


def audit(folder):
    source = json.loads((folder / "audit.json").read_text())
    results = []
    for p in source["partitions"]:
        path = folder / p["sample_file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != p["sample_sha256"]:
            raise ValueError("Source sample hash mismatch")
        book = WSEBook()
        snapshots = []
        crossed = complete = count = 0
        with path.open() as stream:
            for count, row in enumerate(csv.DictReader(stream), 1):
                book.apply(row)
                if count % 128 == 0:
                    snapshot = book.snapshot()
                    snapshots.append(snapshot)
                    crossed += snapshot["crossed_or_locked"]
                    complete += snapshot["complete_depth"]
        dest = folder / f"{p['stock']}-{p['date']}-snapshots.json"
        dest.write_text(json.dumps(snapshots, indent=2) + "\n")
        results.append({"stock": p["stock"], "date": p["date"], "messages_replayed": count,
                        "snapshots": len(snapshots), "crossed_or_locked": crossed,
                        "complete_five_level_depth": complete, "live_orders": len(book.orders),
                        "snapshots_sha256": hashlib.sha256(dest.read_bytes()).hexdigest()})
    report = {"evidence_class": "real_data_replay_engineering_only", "partitions": results,
              "snapshot_stride_events": 128, "limit_orders_only": True,
              "manipulation_labels": None, "AP": None,
              "warning": "Prefixes include retransmission and preopen/auction states; not a continuous-session benchmark."}
    (folder / "replay-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("folder", type=Path)
    audit(p.parse_args().folder)
