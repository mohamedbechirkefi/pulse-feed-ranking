<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# EXP-003 protocol: sensitivity of the primary contrast to candidate-pool skew and choice-model sharpness

**Status: FROZEN v1.0 (2026-11-24), owner-approved (G-FREEZE). SHA-256 in `research/freeze.json` and the registry.** Shared definitions: `research/protocol.md` sections 2 to 8 and 15. Section 16 below amends this file and wins where they differ.

## 1. Precise question
Does the EXP-001 primary contrast (content similarity minus random in final-window exposure entropy) and the MMR recovery effect persist when the catalog topic distribution is skewed and when the like-probability curve is flatter?

## 2. Mechanism
Under a skewed pool, the random arm itself shows lower entropy, so the gap attributable to the ranker may shrink. A flatter choice curve (larger tau) weakens the signal a similarity ranker learns from, which may weaken narrowing.

## 3. Rationale from verified sources
Simulation conclusions depend on modelling assumptions; T-RECS (Lucherini et al. 2021, arXiv:2107.08959) and RecSim (Ie et al. 2019, arXiv:1909.04847) both present simulation as configurable assumptions, which motivates testing the assumptions most likely to drive the result.

## 4. Competing explanations
This experiment is itself the test of competing explanation (a) and of choice-model sharpness for EXP-001.

## 5. Hypotheses
- Primary contrast per cell: Delta = H_exp(similarity) - H_exp(random), paired by seed.
- Invalidation criterion (pre-registered): if, in the Zipf-skew cells, the 95% interval for Delta includes 0 or the point estimate is above -0.05, the EXP-001 interpretation is restricted to balanced pools. Likewise for tau = 0.3.
- Secondary: Delta_MMR = H_exp(MMR) - H_exp(similarity) per cell.

## 6. Estimand
Mean paired difference per cell, and the difference of that difference between skewed and uniform pools (interaction), with its interval computed over seeds.

## 7. Unit, scope, variables
- Unit: one run. Static preferences, eta = 0.1, alpha_0 = 1.0, sizes as EXP-001.
- Independent variables: ranker {random, similarity, MMR}; pool skew {uniform, Zipf with s = 1 over topics}; tau {0.1, 0.3}.
- Dependent: H_exp (primary), Gini, relevance, miscalibration.

## 8. Seeds and sample size
3 x 2 x 2 = 12 cells x 10 seeds = 120 runs, matched across rankers inside each (skew, tau) cell. The interaction interval uses seeds as units; skew cells use distinct catalogs, so the interaction is unpaired across skew levels and is reported with a Welch interval.

## 9. Compute budget
At most 1 hour wall clock.

## 10. Metric formulas
As EXP-001 section 10. Zipf topic weights pi_z proportional to 1 / z^s, z = 1..K.

## 11. Uncertainty
Paired t and bootstrap within cells; Welch t-interval for the skew interaction.

## 12. Exclusion and stopping
As protocol.md section 8.

## 13. Anticipated failure modes
Under skew, some topics may have very few items in a pool of 50; entropy remains defined. Reported per-cell topic counts of pools.

## 14. Sensitivity tests
This experiment is the sensitivity analysis registered in protocol.md section 10.

## 15. Reproduction commands (to be implemented in M2; not runnable yet)
```
uv run python -m pulse.cli run --experiment EXP-003
uv run python -m pulse.cli report --experiment EXP-003
```

## 16. Amendments before freeze (owner-approved 2026-11-24, round 2)

- Choice curve: each tau level has its own fitted midpoint, so that sharpness varies at a matched target like rate: tau = 0.1 with c = 0.066421, tau = 0.3 with c = 0.005990 (protocol section 15.5 and 15.11; replaces 0.5). In the config the two tau levels are two blocks, `tau0.1` and `tau0.3`, each with the factor pool skew {uniform, Zipf}; the cells are the same 12 as section 8. The primary cell is block `tau0.1`, pool skew Zipf.
- Seeds: 20 per cell (103001 to 103020). Runs: 12 x 20 = 240.
- Sign reversal under the Zipf catalog: reported by the pre-decided rule of protocol section 15.9.
- Compute budget unchanged.
