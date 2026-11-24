<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# EXP-004 protocol: second test of the primary contrast on MovieLens-derived preferences and catalog

**Status: FROZEN v1.0 (2026-11-24), owner-approved (G-FREEZE). SHA-256 in `research/freeze.json` and the registry.** Shared definitions: `research/protocol.md` sections 2 to 8 and 15 (this experiment is defined by section 15.6).

## 1. Precise question
Does the EXP-001 primary contrast (content similarity minus random in final-window exposure topic entropy, static preferences, eta = 0) hold when users' initial preferences and the catalog's topic weights come from MovieLens 1M instead of the synthetic Dirichlet and uniform generators?

## 2. Mechanism
As EXP-001 section 2. Real preferences are more heterogeneous across users and topics than a symmetric Dirichlet, and the catalog is skewed (Drama and Comedy are 46% of included movies), which may change how much a similarity ranker narrows exposure relative to random.

## 3. Rationale from verified sources
Simulation conclusions depend on the assumed preference distribution (Lucherini et al. 2021, arXiv:2107.08959; Ie et al. 2019, arXiv:1909.04847). MovieLens (Harper and Konstan 2015, doi:10.1145/2827872) is the standard public source of real user-item preferences for such calibration. This experiment uses it only as input to the same simulation; it makes no claim about MovieLens users or any platform.

## 4. Competing explanations
(a) Catalog skew rather than preference realism (EXP-003 isolates skew on synthetic users); (b) the preference construction (add-one smoothing, division by catalog share) rather than the data; (c) selection in MovieLens ratings (users rate what they chose to watch), which shapes the vectors and L*.

## 5. Hypotheses
- H0: E[Delta] = 0, Delta = H_exp(similarity) - H_exp(random), paired by seed.
- H1: E[Delta] < 0.
- Contradiction: the 95% t-interval upper bound is >= 0, or the point estimate is above -0.05 (no practically relevant reduction).
- Sign reversal (interval entirely above 0): reported by protocol section 15.9.
- Secondary: MMR minus random, MMR minus similarity, secondary metrics (user control: arm minus random only), Holm within each metric family.
- Interpretation (protocol section 15.6): if EXP-001 supports H1 and EXP-004 meets its contradiction rule, the EXP-001 interpretation is restricted to the synthetic preference generator. Never pooled with EXP-001.

## 6. Estimand
Mean over master seeds of the paired difference in run-level mean-over-users final-window normalised exposure topic entropy.

## 7. Unit, scope, variables
- Unit: one run (master seed). U = 200 users sampled without replacement per seed from the 3,020 held-out-half preference vectors (even MovieLens user ids); N = 1000 synthetic items with primary topics drawn from pi_ML; K = 10 (the ten most frequent MovieLens genres); C = 50, k = 10, T = 200, W = 50.
- Fixed: static preferences, eta = 0.0, tau = 0.1, c = c_ML = 0.061067 (fitted on the calibration half, protocol 15.11), beta = 0.85, MMR lambda = 0.5.
- Independent variable: ranker (random, similarity, MMR).
- Dependent: H_exp (primary); Gini, relevance, miscalibration KL, user control, like rate (secondary).

## 8. Seeds and sample size
20 master seeds (104001 to 104020), matched across the three arms: 60 runs.

## 9. Compute budget
At most 15 minutes wall clock (projected about 1 minute).

## 10. Metric formulas
As EXP-001 section 10.

## 11. Uncertainty
As EXP-001 section 11.

## 12. Exclusion and stopping
As protocol.md section 8. A missing or altered preference file (SHA-256 mismatch) fails every run before any simulation step; that is an implementation failure, fixed by regenerating the file with the scripts below, never by editing the config.

## 13. Anticipated failure modes
The held-out preference file is absent on a fresh clone (never committed): the runner fails with a clear message. Rare topics (pi about 0.037) give few pool items per step; entropy stays defined.

## 14. Sensitivity tests
None beyond EXP-003 (pool skew on synthetic users). Not extended after results.

## 15. Reproduction commands
```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python scripts/download_movielens.py
.venv/bin/python scripts/prepare_movielens.py
PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-004
PYTHONPATH=src .venv/bin/python -m pulse.cli report --results results/raw/EXP-004
```
