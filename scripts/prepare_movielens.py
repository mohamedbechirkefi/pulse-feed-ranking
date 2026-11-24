# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Ingest MovieLens 1M (protocol sections 15.2 to 15.6) into data/processed/ (git-ignored).

Writes:
  data/processed/ml1m_prefs_calibration.json  preference vectors, calibration half (odd user ids)
  data/processed/ml1m_prefs_heldout.json      preference vectors, held-out half (even user ids)
  data/processed/ml1m_summary.json            aggregates only (topics, pi, L*, counts, file hashes)
Vectors carry no user id. Deterministic: same zip, same bytes out.

Usage: python scripts/prepare_movielens.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pulse.movielens import ingest, read_zip  # noqa: E402

RAW = ROOT / "data" / "raw" / "movielens-1m" / "ml-1m.zip"
OUT = ROOT / "data" / "processed"


def write(path: Path, obj) -> str:
    blob = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    path.write_bytes(blob)
    return hashlib.sha256(blob).hexdigest()


def main() -> int:
    if not RAW.exists():
        print("run scripts/download_movielens.py first", file=sys.stderr)
        return 1
    res = ingest(*read_zip(RAW))
    OUT.mkdir(parents=True, exist_ok=True)
    h_cal = write(OUT / "ml1m_prefs_calibration.json", {"vectors": res.prefs_calibration.tolist()})
    h_held = write(OUT / "ml1m_prefs_heldout.json", {"vectors": res.prefs_heldout.tolist()})
    summary = {
        "source_zip_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
        "topics": res.topics,
        "genre_movie_counts": res.genre_movie_counts,
        "pi_ml": res.pi.tolist(),
        "like_rate_calibration_L_star": res.like_rate_calibration,
        "counts": res.counts,
        "files": {"ml1m_prefs_calibration.json": h_cal, "ml1m_prefs_heldout.json": h_held},
    }
    (OUT / "ml1m_summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
