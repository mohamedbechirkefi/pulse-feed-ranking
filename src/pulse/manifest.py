# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Run manifests: provenance recorded with every run (master prompt section 4)."""
from __future__ import annotations

import platform
import resource
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import __version__

REPO_ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def git_revision() -> dict:
    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True,
                              check=True).stdout.strip()
    try:
        rev = git("rev-parse", "HEAD")
        dirty = bool(git("status", "--porcelain", "--untracked-files=no"))
        return {"commit": rev, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


@lru_cache(maxsize=1)
def cpu_name() -> str:
    try:
        out = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True,
                             check=True).stdout.strip()
        if out:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    return platform.processor() or platform.machine()


def peak_rss_bytes() -> int:
    """Process peak resident set size so far. ru_maxrss is bytes on macOS, kilobytes on Linux."""
    v = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(v if sys.platform == "darwin" else v * 1024)


def environment() -> dict:
    return {
        "pulse_version": __version__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "os": platform.platform(),
        "cpu": cpu_name(),
        "git": git_revision(),
    }


def run_manifest(config_hash: str, seed: int, started_utc: str, runtime_s: float) -> dict:
    return {
        "config_hash": config_hash,
        "seed": seed,
        "started_utc": started_utc,
        "runtime_s": runtime_s,
        "peak_rss_bytes_process": peak_rss_bytes(),
        "peak_memory_note": "process-wide peak RSS at the end of this run (runs share one process), not a per-run peak",
        **environment(),
    }
