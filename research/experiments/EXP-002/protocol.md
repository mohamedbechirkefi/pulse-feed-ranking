<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# EXP-002 protocol: ranking objective and simulated preference reinforcement under drifting preferences

**Status: FROZEN v1.0 (2026-11-24), owner-approved (G-FREEZE). SHA-256 in `research/freeze.json` and the registry.** Shared definitions: `research/protocol.md` sections 2 to 8 and 15. Section 16 below amends this file and wins where they differ.

## 1. Precise question
When simulated preferences drift toward liked topics, does the ranking objective change how much each user's preference distribution concentrates over T steps, relative to random ranking?

## 2. Mechanism
Under the drift rule p_u <- normalise((1 - gamma) p_u + gamma onehot(z_i)) after each like, exposure that concentrates on liked topics feeds more likes on those topics, which concentrates p_u further (a reinforcing loop). Random ranking still allows drift but samples topics in proportion to the pool.

## 3. Rationale from verified sources
Kalimeris et al. (KDD 2021, doi:10.1145/3447548.3467298) model users drifting toward recommended content and study conditions for preference amplification; Jiang et al. (AIES 2019, arXiv:1902.10730) formalise degeneracy of user interest under feedback loops. This experiment compares five concrete rankers under one explicit drift rule, with matched pools, as a simulation of the stated assumption only.

## 4. Competing explanations
(a) Drift functional form rather than ranker (additive-then-clip check below); (b) drift that occurs under any ranker because users like their own top topics more often (controlled by the random arm); (c) initial concentration (factor alpha_0).

## 5. Hypotheses
- Primary metric of this experiment: preference reinforcement Delta H_pref = (H(p_u(T)) - H(p_u(0))) / ln K, mean over users per run.
- H0: E[D] = 0, D = Delta H_pref(similarity) - Delta H_pref(random), paired by seed, at gamma = 0.05, alpha_0 = 1.0 (primary cell).
- H1: E[D] < 0 (similarity produces more concentration).
- Contradiction: 95% t-interval upper bound >= 0, or point estimate above -0.05.
- Secondary: other cells; other arms against random; MMR against similarity; H_exp and all secondary metrics; Holm within families.

## 6. Estimand
Mean over master seeds of the paired difference in run-level mean normalised preference-entropy change.

## 7. Unit, scope, variables
- Unit: one run. Same sizes as EXP-001. eta = 0.1 fixed.
- Independent variables: ranker (5); gamma {0.01, 0.05}; alpha_0 {1.0, 0.1}. Bandit alpha_ucb = 1.0.
- Dependent: Delta H_pref (primary of EXP-002), H_exp, Gini, relevance (evaluated against current p_u(t)), miscalibration against current p_u(t), user control, like rate.
- Preference model: drifting. Never pooled with EXP-001 (static).

## 8. Seeds and sample size
10 master seeds per cell, matched across arms: 5 x 2 x 2 x 10 = 200 runs, plus the drift-form check (similarity and random, gamma = 0.05, both alpha_0, 10 seeds) = 40 runs. Same smoke-based rule for raising to 20 seeds.

## 9. Compute budget
At most 1.5 hours wall clock.

## 10. Metric formulas
As EXP-001 section 10, plus Delta H_pref(u) = (H(p_u(T)) - H(p_u(0))) / ln K with H(p) = -sum_z p_z ln p_z.

## 11. Uncertainty
As EXP-001 section 11.

## 12. Exclusion and stopping
As protocol.md section 8.

## 13. Anticipated failure modes
Drift collapsing p_u to a vertex (entropy 0, logs of 0): handled with the convention 0 ln 0 = 0, tested. Floating-point drift of the simplex sum: renormalise each step, invariant-checked.

## 14. Sensitivity tests
Drift functional form: additive-then-clip p_u <- clip(p_u + gamma onehot(z_i)) then normalise. If the sign of D changes or |D| falls below 0.05, reinforcement is reported as dependent on the drift form.

## 15. Reproduction commands (to be implemented in M2; not runnable yet)
```
uv run python -m pulse.cli run --experiment EXP-002
uv run python -m pulse.cli report --experiment EXP-002
```

## 16. Amendments before freeze (owner-approved 2026-11-24, round 2)

- Choice curve: tau = 0.1, c = 0.066421 (fitted at alpha_0 = 1.0 without drift, protocol section 15.5 and 15.11; replaces 0.5), used in every cell including the drift-form check.
- Seeds: 20 per cell (102001 to 102020). Runs: 5 x 2 x 2 x 20 = 400, plus 80 drift-form runs: 480.
- User control: arm minus random only (protocol section 15.7).
- Compute budget unchanged.
