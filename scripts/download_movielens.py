# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Download MovieLens 1M (GroupLens) into data/raw/movielens-1m/ and record its provenance.

Deterministic: fixed URLs, fixed file names, SHA-256 verified against the pinned values below
(pinned at the first download on 2026-11-24). The files are never committed: the GroupLens
licence forbids redistribution without separate permission (data/manifest.json, decision D-009).

Usage: python scripts/download_movielens.py [--force]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "raw" / "movielens-1m"
FILES = {
    "ml-1m.zip": "https://files.grouplens.org/datasets/movielens/ml-1m.zip",
    "ml-1m-README.txt": "https://files.grouplens.org/datasets/movielens/ml-1m-README.txt",
}
# Pinned SHA-256 from the first download (2026-11-24T18:31:56Z). A mismatch stops the script.
PINNED: dict[str, str | None] = {
    "ml-1m.zip": "a6898adb50b9ca05aa231689da44c217cb524e7ebd39d264c56e2832f2c54e20",
    "ml-1m-README.txt": "908ee4aa21a8d37aec0cb6c1cdcc41f9bba3c5d2fef3d9250a8073b8e460027e",
}
MAX_BYTES = 50_000_000  # the zip is about 5.9 MB; refuse anything far larger


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, out: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "pulse-feed-ranking research download"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise SystemExit(f"{url} exceeds {MAX_BYTES} bytes; stop and report")
    out.write_bytes(data)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="download again even if the files exist")
    a = ap.parse_args(argv)
    DEST.mkdir(parents=True, exist_ok=True)
    record = {"dataset": "MovieLens 1M", "downloaded_utc": None, "files": []}
    for name, url in FILES.items():
        out = DEST / name
        if a.force or not out.exists():
            fetch(url, out)
            record["downloaded_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        digest = sha256(out)
        pinned = PINNED[name]
        if pinned is not None and digest != pinned:
            print(f"SHA-256 mismatch for {name}: {digest} != pinned {pinned}", file=sys.stderr)
            return 1
        record["files"].append({"name": name, "url": url, "bytes": out.stat().st_size, "sha256": digest})
    prev = DEST / "download_record.json"
    if record["downloaded_utc"] is None and prev.exists():
        record["downloaded_utc"] = json.loads(prev.read_text())["downloaded_utc"]
    prev.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
