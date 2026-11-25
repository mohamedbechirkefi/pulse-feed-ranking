<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# EXP-005 protocol: dependence of the primary contrast on the calibrated like rate

**Status: REGISTERED, NOT FROZEN (draft v0.1, 2026-11-25).** Registered by the owner's decision of 2026-11-25 (owner, 2026-11-25, "Approve all" (post-M4), item 3; decision D-018). No confirmatory run may start before the owner freezes this protocol (G-FREEZE): the registry carries no protocol hash, so the run guard (`src/pulse/runner.py`, `protocol_frozen`) refuses `pulse.cli run --experiment EXP-005`. No data of this experiment exists. Parameters marked **OPEN** are not derivable from the frozen design v1.0 and are left to the owner at freeze; this draft does not choose them.

Shared definitions: `research/protocol.md` sections 2 to 8 and 15 (frozen v1.0) apply unchanged unless this file says otherwise. Config draft: `research/experiments/EXP-005/config.json`.

## 0. Disclosure: written after the results it follows up

This experiment was designed after the confirmatory results of EXP-001 to EXP-004 and after the exploratory check XPL-M4-LIKERATE (decision D-016; journal XPL-M4-LIKERATE; `results/exploratory/m4-likerate-summary.csv`; limitations 17) had been seen. It is not a blind preregistration. What freezing it will guarantee is narrower: the levels, seeds, decision rules and analysis are fixed before any run of this experiment, on seeds disjoint from every earlier run, so the confirmatory answer cannot be tuned to its own outcome. The exploratory values are never pooled with EXP-005 and are never used as its evidence.

## 1. Precise question

In the static-preference world of the EXP-003 `tau0.1` block, does the paired contrast Delta = H_exp(similarity) - H_exp(random) depend on the target like rate to which the choice curve is calibrated, under the uniform and the Zipf (s = 1) catalogs?

## 2. Mechanism

The similarity ranker learns a profile from liked items (added) and disliked items (subtracted) (protocol section 2). When simulated users like few of the items they examine, the profile is dominated by dislikes and pushes exposure away from the topics already shown, rather than toward the user's preferred topic; when they like many, the profile concentrates on the preferred topic and exposure narrows. Under a skewed catalog, a dislike-dominated profile is pushed away from the abundant topic, which can make similarity exposure more diverse than random (the candidate mechanism of protocol 15.9, item 3, and decision D-008, P4). The like rate is set by the choice-curve midpoint c (protocol 15.5), so varying c at fixed tau varies the balance of likes and dislikes without changing preferences, catalog or pools.

## 3. Rationale

- **Gap in the frozen design.** Every confirmatory result holds at one calibrated like rate, L* = 0.577 (protocol 15.4, 15.11; limitations 16). No confirmatory run varies it.
- **Internal evidence motivating the question (exploratory, not evidence for EXP-005).** Pre-freeze runs under the planning midpoint (like rate about 0.02) gave a near-zero primary contrast and a positive Zipf contrast (freeze record C4; manuscript section 4). The M4 check XPL-M4-LIKERATE (5 seeds) found the contrast below the smallest effect of interest at true like rates of 0.15 or less under the uniform catalog and positive at those like rates under Zipf (limitations 17).
- **Literature.** Simulation conclusions depend on configurable modelling assumptions (T-RECS, Lucherini et al. 2021, arXiv:2107.08959; RecSim, Ie et al. 2019, arXiv:1909.04847; both as cited in EXP-003 section 3), which motivates testing the assumption that most changed the result. Selected-exposure ratings such as MovieLens give a like rate that is not a like rate under random exposure (protocol 15.4; limitations 9), so the calibrated value itself is uncertain.

## 4. Competing explanations

1. **Like rate (the hypothesis under test).** The sign and size of Delta are governed by the share of feedback that is positive.
2. **Midpoint position, not like rate.** Moving c also moves where the sigmoid is steep relative to the utility distribution, which changes how strongly likes discriminate between items. EXP-005 cannot separate the two at one tau; if the owner includes tau = 0.3 (section 8, OPEN-4), a dependence that holds at both tau values at matched like rates is evidence against a pure steepness reading.
3. **Catalog skew acting through the random baseline.** Under Zipf the random arm's H_exp is lower (EXP-003), so the room for narrowing differs; this is why the two catalogs are analysed separately and never pooled.
4. **Chance in the exploratory check.** Five seeds; EXP-005 uses fresh seeds and the frozen seed count.

## 5. Hypotheses and decision rules

All rules below are the frozen rules of protocol v1.0 applied per level; nothing new is invented except where marked OPEN.

- **Per-level primary contrast** (each like-rate level l, each catalog): Delta_l = H_exp(similarity) - H_exp(random), paired by seed.
  - H1_l: E[Delta_l] < 0. Contradiction (frozen rule, protocol section 3; EXP-001 section 5): the 95% t-interval upper bound is >= 0, or the point estimate is above -0.05 (smallest effect of interest). The second case is reported as "no practically relevant reduction", never as equivalence.
  - Sign reversal: if the 95% t-interval of Delta_l lies entirely above 0, the pre-decided reporting rule of protocol 15.9 applies (items 1, 3 and 4; item 2 refers to EXP-001's interpretation and applies as written).
- **Dependence contrast (the registered question).** D_l = Delta_l - Delta_ref, paired by seed, where the reference level is the frozen calibration L* = 0.5771428687720555 (protocol 15.4; derived: it is the level at which every confirmatory result holds).
  - H1_dep: for at least one level l in the set designated by the owner (OPEN-2), |E[D_l]| >= 0.05 with the 95% interval of D_l excluding 0. The threshold 0.05 is the frozen smallest effect of interest, reused for a difference of contrasts (OPEN-3: the owner confirms or replaces this reuse).
  - Contradiction of H1_dep: for every designated level, the 95% interval of D_l includes 0 or |point estimate| < 0.05. Reported as "no practically relevant dependence detected over the registered levels", never as independence.
  - Multiplicity: OPEN-3 (the family over which Holm is applied, following the frozen practice of protocol section 7, is not derivable because the level set is open).
- **What would contradict the M4 exploratory reading:** under the uniform catalog, Delta_l meeting H1_l (interval below 0 and point estimate at or below -0.05) at every designated level below L*; under Zipf, no level with Delta_l's interval entirely above 0.

## 6. Estimand

For each catalog and level: the mean over master seeds of the paired difference in run-level, mean-over-users, final-window normalised exposure topic entropy (EXP-001 section 6), and the mean over seeds of the paired difference-in-differences D_l. The random arm does not use feedback, so for a given seed its exposure is identical across levels (observed in XPL-M4-LIKERATE: one random-arm H_exp value per catalog across all eight levels); D_l is therefore paired by seed.

## 7. Unit, scope, variables, treatment and control

- **Unit:** one run (master seed). Users inside a run are not independent; per-user values are aggregated per run (protocol section 6).
- **Scope (derived from the EXP-003 `tau0.1` block, frozen):** static preferences; U = 200, N = 1000, K = 10, C = 50, k = 10, T = 200, W = 50; eta = 0.1; alpha_0 = 1.0; zipf_s = 1.0; synthetic generator only (no MovieLens inputs).
- **Independent variables:** target like rate (levels OPEN-1, each mapped to a midpoint c by the frozen method of protocol 15.5); pool skew {uniform, Zipf} (derived: EXP-003 primary cell is Zipf, and its reference is uniform); ranker; tau (0.1 derived; 0.3 OPEN-4).
- **Treatment:** content-similarity ranker. **Control and baseline:** random ranker (protocol section 4). MMR (lambda_mmr = 0.5, as EXP-003): OPEN-5.
- **Dependent variables:** H_exp (primary); observed and implied true like rate per cell (reported, used to check the calibration); Gini exposure concentration, relevance and miscalibration KL (secondary, descriptive unless the owner registers a family).
- **Midpoint under Zipf (derived from protocol 15.5):** the midpoint fitted on the uniform synthetic world is also used under Zipf, as in the frozen design; the Zipf like rates therefore differ from the targets and are reported as observed.

## 8. Seed plan and sample size

- **Seeds per cell: 20** (frozen rule, protocol 15.8). First seed **105001** (derived from the convention 101001, 102001, 103001, 104001), so seeds 105001 to 105020, disjoint from every confirmatory, calibration (700001 to 700020) and exploratory (900001 and up, including 960001 to 960005) range. Matched across arms and levels inside each catalog.
- **Sample-size rationale:** at n = 20 the paired t half-width factor is 0.468 times the SD of paired differences (protocol 15.8). The exploratory SDs of Delta (XPL-M4-LIKERATE, 5 seeds, at most about 0.022) give a planning half-width near 0.01, well below 0.05; this is a planning projection from exploratory values, and the seed count is not re-derived from them.
- **Runs (formula):** arms x levels x catalogs x tau values x 20. With the derived minimum (2 arms, 2 catalogs, tau 0.1): 80 runs per like-rate level, including the reference level L*. The total depends on OPEN-1, OPEN-4 and OPEN-5.

## 9. Compute budget

OPEN-6: the cap for this experiment. The frozen 4-hour budget (protocol 15.10) covered EXP-001 to EXP-004 only. Planning projection, not a measurement of EXP-005: XPL-M4-LIKERATE ran 80 runs of the same size in 61.3 s and 60.4 s per process (progress.md, M4), so 80 runs per level is about one minute per level and catalog pair on the same machine. Stop rule as protocol section 8 if the cap is exceeded.

## 10. Metric formulas and units

As EXP-001 section 10 and protocol sections 4 and 5. Like probability sigmoid((r_ui - c) / tau) (protocol 15.5). Implied true like rate under random ranking: the like rate of the random arm, corrected for the flip noise eta as in `scripts/m4_likerate_summary.py` (that script is exploratory; the analysis script of EXP-005 is written and tested before any run, as D-013 did for EXP-001 to EXP-004).

## 11. Uncertainty

Paired 95% t-interval and percentile bootstrap over seeds (10,000 resamples, fixed bootstrap seed), d_z and raw per-seed values, for each Delta_l and D_l (protocol section 7). No test treats users or steps as independent. Uniform and Zipf are analysed separately and never pooled. Holm family: OPEN-3.

## 12. Exclusion and stopping

As protocol section 8: exclusion only for a documented implementation failure, rerun once with the same seed after a committed fix, recorded as a deviation. Fixed design, no early stopping on results, no level dropped after seeing results.

## 13. Anticipated failure modes

- **Extreme midpoints.** For very high or very low targets the bisection of protocol 15.5 may sit near the bracket [-1, 2]; a level whose fit does not converge inside the bracket is reported and removed before freeze, not after any run.
- **Zipf like rates off target.** Expected by construction (section 7); reported per cell.
- **Degenerate feedback.** At very low like rates almost all feedback is negative (D-008, P1); the profile is then dislike-dominated by design, and that is the condition under test, not a failure.
- **Analysis code.** Must handle more than one level per catalog and the D_l contrast; it is written and tested before the freeze, with no EXP-005 output available.

## 14. Sensitivity tests

- tau = 0.3 at matched like rates (OPEN-4), addressing competing explanation 2.
- Like-rate dependence of MMR recovery (OPEN-5).
- Not included and stated as untested: drifting preferences, MovieLens inputs, other eta and alpha_0 values (limitations 17).

## 15. Reproduction commands (runnable only after the freeze)

```
PYTHONPATH=src .venv/bin/python scripts/exp005_fit_midpoints.py      # to be written before freeze: frozen 15.5 method, owner's levels
PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-005
PYTHONPATH=src .venv/bin/python scripts/analyse_experiment.py EXP-005  # extended and tested before freeze
```

At freeze the fitted midpoints replace the OPEN entries of the config, the config is copied to `experiments/EXP-005.json`, and the protocol and config hashes are added to `research/freeze.json` and the registry by the owner's G-FREEZE decision.

## 16. Open decisions for the owner at freeze

| Id | Parameter | Why it is not derivable from the frozen design |
| --- | --- | --- |
| OPEN-1 | Set of target like rates (besides the reference L*) | The frozen design has one like rate. The exploratory grid (0.05, 0.15, 0.30, 0.45, L*, 0.70, 0.85 and the planning midpoint 0.5) is a record of what was tried, not a proposal. |
| OPEN-2 | Levels designated for the dependence contrast D_l | Depends on OPEN-1. |
| OPEN-3 | Threshold for a practically relevant D_l (0.05 reused, or another) and the Holm family | The frozen smallest effect of interest is defined for Delta, not for a difference of contrasts; the family depends on OPEN-1 and OPEN-2. |
| OPEN-4 | Include tau = 0.3 (with midpoints fitted per level at that tau) | Frozen EXP-003 has both tau values, but its primary block is tau 0.1; adding 0.3 doubles the runs. |
| OPEN-5 | Include the MMR arm | The registered question concerns the primary contrast only; EXP-003 included MMR for its secondary contrast. |
| OPEN-6 | Compute budget cap for EXP-005 | The frozen budget covers EXP-001 to EXP-004 only. |
