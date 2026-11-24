"""Retrieve only small source files from the CC BY predecessor release.

No market data, weights or archive-wide download. ZIP CRC is checked by zipfile;
the whole-archive published MD5 is not verified by selective range reads.
"""
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile
from lobbench.http_range import HTTPRangeFile

NAMES = ["models/models.py", "train/utilities.py", "03_model_training.py", "requirements.txt", "README.md"]


def main():
    with urllib.request.urlopen("https://zenodo.org/api/records/11048480", timeout=30) as response:
        metadata = json.load(response)
    if metadata["metadata"]["license"]["id"] != "cc-by-4.0":
        raise ValueError("Release license changed; inspect before proceeding")
    entry = next(x for x in metadata["files"] if x["key"] == "JFDS Repo.zip")
    if entry["checksum"] != "md5:5c44e0ee2adbcdf85309dc628252e077":
        raise ValueError("Published source identity changed")
    remote = HTTPRangeFile(entry["links"]["self"], entry["size"], max_bytes=2*1024**2,
                           headers={"User-Agent": "FinancialAD-LOB research source audit"})
    with zipfile.ZipFile(remote) as archive:
        for name in NAMES:
            if archive.getinfo(name).file_size > 100000:
                raise ValueError("Unexpected large source member")
            data = archive.read(name)
            dest = Path("vendor/jfds_reference") / name
            if dest.exists() and dest.read_bytes() != data:
                raise ValueError("Existing source differs; preserve and investigate")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            print(name, len(data), hashlib.sha256(data).hexdigest())
    print("Range bytes read:", remote.downloaded, "; whole archive NOT verified")


if __name__ == "__main__":
    main()
