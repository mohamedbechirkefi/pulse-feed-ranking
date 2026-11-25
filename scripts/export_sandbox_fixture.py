# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Parity fixture for the demo sandbox (demo/src/fixtures/engine_fixture.json).

The browser sandbox (demo/src/engine.ts) is a TypeScript port of the PULSE interaction loop, rankers
and metrics. Its random-number generator is not numpy's, so the fixture records every random input of
a tiny Python run (catalog, initial preferences, candidate pools, tie keys, examination, choice and
flip draws, all from the research engine's own streams) together with the slates and metrics that
pulse.simulate.simulate produced from them. demo/src/engine.test.ts feeds the same inputs to the port
and compares slates exactly and metrics within 1e-9.

Exploratory tooling only: tiny configs, no research result. Deterministic; runs in well under a second.
Usage: PYTHONPATH=src .venv/bin/python scripts/export_sandbox_fixture.py [--check]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pulse.config import SimConfig  # noqa: E402
from pulse.model import initial_preferences, make_catalog, sample_pools, spawn_streams  # noqa: E402
from pulse.simulate import Trace, simulate  # noqa: E402

OUT = ROOT / "demo" / "src" / "fixtures" / "engine_fixture.json"
SEED = 424242
BASE = dict(n_users=5, n_items=60, n_topics=10, pool_size=12, slate_size=5, n_steps=30, window=10,
            tau=0.1, like_midpoint=0.066421)
CASES = [
    ("static", dict(eta=0.2), ("random", "popularity", "similarity", "linucb", "mmr")),
    ("drifting", dict(eta=0.1, preference_model="drifting", gamma=0.05), ("random", "similarity", "mmr")),
    ("zipf-static", dict(eta=0.1, pool_skew="zipf", alpha0=0.1), ("random", "similarity", "linucb")),
]


def draws(cfg: SimConfig, seed: int) -> dict:
    rng = spawn_streams(seed)
    cat = make_catalog(cfg, rng["catalog"])
    p0 = initial_preferences(cfg, rng["users"])
    steps = []
    U, k = cfg.n_users, cfg.slate_size
    for _ in range(cfg.n_steps):
        pool = sample_pools(cfg, rng["pools"])
        steps.append({
            "pool": pool.tolist(),
            "tie": rng["tiebreak"].random(pool.shape).tolist(),
            "exam": rng["examination"].random((U, k)).tolist(),
            "like": rng["choice"].random((U, k)).tolist(),
            "flip": rng["noise"].random((U, k)).tolist(),
        })
    return {"topics": cat.topics.tolist(), "emb": cat.emb.tolist(), "pos_share": cat.pos_share.tolist(),
            "p0": p0.tolist(), "steps": steps}


def build() -> dict:
    cases = []
    for name, over, rankers in CASES:
        cfg0 = SimConfig(**BASE, **over)
        world = draws(cfg0, SEED)
        runs = []
        for r in rankers:
            cfg = cfg0.with_overrides(ranker=r)
            tr = Trace()
            out = simulate(cfg, SEED, tr)
            runs.append({"ranker": r, "slates": [s.tolist() for s in tr.slates], "metrics": out["metrics"]})
        cases.append({"name": name, "config": cfg0.to_dict(), "seed": SEED, "world": world, "runs": runs})
    return {"fixture": "pulse-sandbox-parity", "version": 1, "tolerance": 1e-9, "cases": cases}


def render(d: dict) -> str:
    return json.dumps(d, separators=(",", ":"), allow_nan=False) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("FIXTURE-CHECK " + ("identical" if same else "DIFFERS"))
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
