<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# PULSE: recommendation feedback and attention (simulation study)

**Question.** How do ranking objectives influence exposure diversity and simulated preference reinforcement?

**Status: M0 (bootstrap and feasibility), 2026-11-24.** No simulation code, no experiment run, no findings. The protocol is a draft awaiting the owner's freeze.

## Why it matters

Recommender systems learn from feedback on the items they themselves chose to show. Prior simulation studies report that such loops can narrow exposure and amplify preferences. PULSE aims to compare five standard ranking objectives (random, popularity, content similarity, LinUCB bandit, MMR diversity-aware) on identical candidate pools, with synthetic users whose preferences are either static or drifting, and to report effect sizes with seed-level uncertainty. It is a simulation: it makes no claim about real platforms, real users or addiction.

## What exists now

- Control files: `CLAUDE.md`, `roadmap.md`, `progress.md`.
- Draft protocol: `research/protocol.md`; experiment protocols `research/experiments/EXP-001` to `EXP-003`; registry `research/experiment_registry.csv`.
- Preliminary literature scan: `research/literature_review.md`. Data policy: `data/manifest.json` (synthetic only).
- Manuscript skeleton (headings only): `research/paper/manuscript.md`.
- Locked Python environment: `pyproject.toml`, `uv.lock`; a toolchain smoke test in `tests/`.

## Quick start (environment only)

```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen
/Users/bechir/research/labs/.tools/py/bin/uv run pytest -q
```

Experiment commands will be added in M2.

## Licence

PULSE Source-Available Non-Commercial Research License v1.0 (`LICENSE`, `NOTICE.md`). This is a custom licence, not an OSI open-source licence. Third-party material keeps its own terms.

## Citation

See `CITATION.cff`.
