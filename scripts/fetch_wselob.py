"""Full, hash-verified WSE acquisition for CQ /date or /data storage only.

Existing files are verified and reused. No existing file is overwritten or
removed. A failed .part stays for inspection; it must be resolved explicitly.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import urllib.request


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/wselob-source-locators.json"))
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--stocks", nargs="+", default=["KGHM", "PEKAO", "PKNORLEN", "PKOBP", "PZU"])
    args = parser.parse_args()
    if not os.environ.get("CQ_OUTPUT_DIR"):
        parser.error("Run full acquisition within an authorized CQ job")
    target = args.data_dir.resolve()
    if not any(target.is_relative_to(Path(p)) for p in ("/date", "/data")):
        parser.error("Full data must be backed by /date or /data")
    manifest = json.loads(args.manifest.read_text())
    entries = [manifest[k][s] for k in ("files", "trades") for s in args.stocks]
    target.mkdir(parents=True, exist_ok=True)
    need = sum(e["bytes"] for e in entries if not (target/e["filename"]).exists())
    if shutil.disk_usage(target).free < need + 2*1024**3:
        raise RuntimeError("Not enough free space plus 2 GiB reserve")
    output = Path(os.environ["CQ_OUTPUT_DIR"])
    output.mkdir(parents=True, exist_ok=True)
    receipt = {"source": manifest["source_url"], "license": manifest["license"],
               "attribution": manifest["attribution"], "files": []}
    for entry in entries:
        path = target / entry["filename"]
        if not path.exists():
            partial = path.with_suffix(path.suffix + ".part")
            request = urllib.request.Request(entry["url"], headers={"User-Agent": "Mozilla/5.0",
                                               "Referer": manifest["source_url"], "Accept-Encoding": "identity"})
            with partial.open("xb") as dest, urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 200:
                    raise RuntimeError("Full download requires HTTP 200")
                received = 0
                while True:
                    block = response.read(min(1024**2, entry["bytes"] - received + 1))
                    if not block:
                        break
                    received += len(block)
                    if received > entry["bytes"]:
                        raise RuntimeError("Source exceeds published size")
                    dest.write(block)
            if partial.stat().st_size != entry["bytes"] or sha256(partial) != entry["sha256"]:
                raise RuntimeError("Downloaded source failed size or SHA256 verification")
            # link is an atomic no-overwrite publication, on the same filesystem.
            os.link(partial, path)
            partial.unlink()
        if path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            raise RuntimeError("Existing data failed verification; preserved for inspection")
        receipt["files"].append({"filename": path.name, "bytes": path.stat().st_size,
                                  "sha256": entry["sha256"], "verified": True})
        (output/"data-acquisition.json").write_text(json.dumps(receipt, indent=2)+"\n")
        (output/"progress.txt").write_text(f"{len(receipt['files'])}/{len(entries)} verified\n")
        print(f"verified {path.name}", flush=True)


if __name__ == "__main__":
    main()
