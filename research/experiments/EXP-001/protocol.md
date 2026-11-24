<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# EXP-001 protocol: ranking objective and exposure diversity under static preferences

**Status: FROZEN v1.0 (2026-11-24), owner-approved (G-FREEZE). SHA-256 in `research/freeze.json` and the registry.** Shared definitions: `research/protocol.md` sections 2 to 8 and 15. Section 16 below amends this file and wins where they differ.

## 1. Precise question
With static simulated preferences and identical candidate pools, how much does each ranking objective (popularity, content similarity, LinUCB bandit, MMR diversity-aware) change final-window exposure topic entropy relative to random ranking?

## 2. Mechanism
A ranker that scores items by similarity to a profile built from observed likes concentrates slates on the topics already liked; with static preferences the narrowing comes from the ranker alone, since the user does not change. Popularity concentrates exposure on items liked by many users. LinUCB trades exploitation for exploration. MMR penalises redundancy inside a slate.

## 3. Rationale from verified sources
Simulation studies report homogenisation from feedback loops (Chaney et al. 2018, arXiv:1710.11214) and popularity-bias amplification (Mansoury et al. 2020, arXiv:2007.13019); exploration is discussed as a mitigation (Jiang et al. 2019, arXiv:1902.10730). This experiment isolates the ranker's contribution with static users, matched candidate pools and explicit noisy feedback. See `research/literature_review.md` for access dates.

## 4. Competing explanations
(a) Candidate-pool composition rather than the objective (tested in EXP-003); (b) feedback noise masking or creating narrowing (factor eta); (c) initial preference concentration: concentrated users may receive low-entropy slates from any adaptive ranker (factor alpha_0); (d) implementation artefacts in tie-breaking (unit tests in M2).

## 5. Hypotheses
- H0: E[Delta] = 0, where Delta = H_exp(similarity) - H_exp(random), paired by seed, at eta = 0.0 and alpha_0 = 1.0 (primary cell).
- H1: E[Delta] < 0.
- Contradiction: the 95% t-interval upper bound for E[Delta] is >= 0, or the point estimate is above -0.05 (no practically relevant reduction).
- Secondary: the same contrast in the other three (eta, alpha_0) cells; popularity, bandit and MMR each against random; MMR against similarity; all secondary metrics. Holm adjustment within each metric's five-contrast family.

## 6. Estimand
Mean over master seeds of the paired difference in run-level mean-over-users final-window normalised exposure topic entropy.

## 7. Unit, scope, variables
- Unit: one run (master seed). U = 200 users, N = 1000 items, K = 10, C = 50, k = 10, T = 200, W = 50.
- Independent variables: ranker (5 levels); eta {0.0, 0.2}; alpha_0 {1.0, 0.1}; nested for the bandit arm only, alpha_ucb {0.1, 1.0}.
- Dependent variables: H_exp (primary); Gini exposure concentration, relevance, miscalibration KL, user control, like rate (secondary).
- Treatment: each non-random ranker. Control and baseline: random ranker.
- Preference model: static.

## 8. Seeds and sample size
10 master seeds per cell (protocol.md section 6), matched across arms. Runs: 5 x 2 x 2 x 10 = 200, plus 40 bandit runs at alpha_ucb = 0.1. The seed count rises to 20 before freeze if the smoke run estimates the paired-difference SD above 0.07.

## 9. Compute budget
At most 1.5 hours wall clock for the whole experiment on the M1 Pro, CPU single process.

## 10. Metric formulas
- H_exp(u) = -sum_z q_uz ln q_uz / ln K, q_u position-weighted topic shares (weights beta^(j-1)) over the last W slates.
- Gini over item exposure counts c_i (final window, all users): G = sum_i sum_j |c_i - c_j| / (2 N sum_i c_i).
- Relevance: mean r_ui over examined items, final window.
- Miscalibration: KL(p_u || (1 - 0.01) q_u + 0.01 p_u), nats.
- User control: mean over dislike events of (share of topic z in slate t+1 minus share in slate t).
- Like rate: observed likes / examined items.

## 11. Uncertainty
Paired t-interval (95%) and percentile bootstrap over seeds (10,000 resamples, bootstrap seed 20261124), d_z, per-seed raw values.

## 12. Exclusion and stopping
As protocol.md section 8. No early stopping; all 240 runs execute.

## 13. Anticipated failure modes
Cosine of a zero profile (cold start) undefined: handled by fallback tie-break, tested. LinUCB matrix ill-conditioning: ridge lambda = 1. Entropy of an empty window: impossible by construction (every step shows k items); asserted. Popularity ties at start: all counts zero, seeded tie-break.

## 14. Sensitivity tests
EXP-003 (pool skew, choice sharpness). Within EXP-001: result reported separately for each (eta, alpha_0) cell; no pooling across cells.

## 15. Reproduction commands (to be implemented in M2; not runnable yet)
```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen
uv run python -m pulse.cli smoke
uv run python -m pulse.cli run --experiment EXP-001
uv run python -m pulse.cli report --experiment EXP-001
```

## 16. Amendments before freeze (owner-approved 2026-11-24, round 2)

- Choice curve: like probability sigmoid((r - c) / tau) with tau = 0.1 and c = 0.066421 (fitted, protocol section 15.5 and 15.11; replaces 0.5). The same c is used in all four (eta, alpha_0) cells.
- Seeds: 20 per cell (101001 to 101020). Runs: 5 x 2 x 2 x 20 = 400, plus 80 bandit runs at alpha_ucb = 0.1: 480. The conditional rule of section 8 is superseded.
- User control: interpreted only as arm minus random; its Holm family is the four arm-minus-random contrasts (protocol section 15.7).
- Second test: EXP-004 repeats the primary contrast on MovieLens-derived preferences and catalog topic weights (protocol section 15.6).
- Compute budget unchanged.
