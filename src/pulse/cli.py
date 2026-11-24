# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Command line interface: smoke, run, report, test.

  python -m pulse.cli smoke                      exploratory smoke matrix (protocol section 9)
  python -m pulse.cli run --experiment EXP-001   confirmatory; refused while the protocol is unfrozen
  python -m pulse.cli run --config PATH          any experiment config (exploratory configs always allowed)
  python -m pulse.cli report --results DIR       tables, figures and PDF from validated result files
  python -m pulse.cli test                       full pytest suite
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .manifest import REPO_ROOT
from .runner import ProtocolNotFrozen, execute, load_experiment

SMOKE_CONFIG = REPO_ROOT / "experiments" / "exploratory" / "smoke.json"


def _run(config: Path, out: Path | None) -> int:
    exp = load_experiment(config)
    try:
        d = execute(exp, out_dir=out, progress=print)
    except ProtocolNotFrozen as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 3
    print(f"results: {d}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pulse")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("smoke", help="exploratory smoke matrix")
    s.add_argument("--out", type=Path, default=None)
    r = sub.add_parser("run", help="run an experiment config")
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--experiment", help="registered id, reads experiments/<ID>.json")
    g.add_argument("--config", type=Path)
    r.add_argument("--out", type=Path, default=None)
    p = sub.add_parser("report", help="build report from a result directory")
    p.add_argument("--results", type=Path, required=True)
    p.add_argument("--no-pdf", action="store_true")
    sub.add_parser("test", help="run the test suite")
    a = ap.parse_args(argv)

    if a.cmd == "smoke":
        return _run(SMOKE_CONFIG, a.out)
    if a.cmd == "run":
        cfg = a.config if a.config else REPO_ROOT / "experiments" / f"{a.experiment}.json"
        return _run(cfg, a.out)
    if a.cmd == "report":
        from .report import generate

        res = generate(a.results, pdf=not a.no_pdf)
        print(f"report: {res['out']} ({res['n_runs']} runs); pdf: {res['pdf']}")
        return 0
    if a.cmd == "test":
        return subprocess.call([sys.executable, "-m", "pytest", "-q", str(REPO_ROOT / "tests")])
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
