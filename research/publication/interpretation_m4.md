<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# M4 interpretation: confounder inspection, sensitivity and expected versus observed

Date 2026-11-25. Milestone M4. Inputs: the frozen protocols, the four experiment reports, `verdict.json`, `contrasts.csv` and `summary.csv` of each experiment, the freeze record and one new exploratory check (XPL-M4-LIKERATE). No frozen verdict is changed by anything in this file.

## 1. Competing explanations, per confirmatory conclusion

Status codes: **addressed** (a committed confirmatory result tests it), **partly** (tested only in part, or by a weak test), **exploratory** (only the M4 exploratory check speaks to it), **open** (nothing tests it).

### 1.1 EXP-001: similarity ranking lowers exposure topic entropy (static preferences)

| Competing explanation (protocol) | Evidence | Status |
| --- | --- | --- |
| (a) Candidate-pool composition, not the objective | Common random numbers: pools identical across arms within a seed. Across catalogs: EXP-003 (Zipf, gap widened, -0.5060) and EXP-004 (pi_ML catalog, -0.4095) | addressed at the frozen calibration; the direction under skew depends on the like rate (section 2) |
| (b) Feedback noise masking or creating narrowing | Factor eta {0.0, 0.2}: -0.4000 and -0.3959 at alpha_0 1.0 | addressed |
| (c) Initial preference concentration | Factor alpha_0 {1.0, 0.1}: -0.4000 and -0.3938 at eta 0 | addressed |
| (d) Tie-breaking or other implementation artefacts | 153 tests (ties, feedback updates, seed determinism, topic distributions, zero feedback); random arm H_exp 0.9932 close to pool entropy 0.9983; independent recomputation of all contrasts (evidence audit) | addressed for the tested behaviours; an untested defect remains possible |
| Not in the protocol: choice-curve calibration (like rate) | One midpoint per tau fixed at the freeze. Pre-freeze exploratory value at like rate about 0.02: -0.000688. M4 check: -0.0032 at 0.02, -0.0057 at 0.05, -0.0384 at 0.15, -0.2396 at 0.30, -0.3960 at 0.45 | exploratory: the effect needs a like rate between 0.15 and 0.30 or more to exceed the smallest effect of interest |
| Not in the protocol: embedding geometry (one dominant topic per item, item noise 0.3) | None | open |

### 1.2 EXP-002: similarity ranking concentrates drifting preferences

| Competing explanation (protocol) | Evidence | Status |
| --- | --- | --- |
| (a) Drift functional form, not the ranker | Additive-then-clip check: -0.4363 and -0.4351, rule not met. The check is nearly a reparametrisation of gamma (limitations 12) | partly (weak test) |
| (b) Drift that occurs under any ranker | Random arm as control: Delta H_pref +0.0971 under random (preferences spread), -0.3379 under similarity | addressed |
| (c) Initial concentration | Factor alpha_0: -0.4350 and -0.4336 at gamma 0.05 | addressed |
| Not in the protocol: like rate | Not tested under drift; the M4 check covers static preferences only | open |
| Not in the protocol: reinforcement built into the assumption | By design (limitations 4) | not testable within the design; disclosed |

### 1.3 EXP-003: the EXP-001 contrast survives catalog skew and a flatter choice curve

| Competing explanation | Evidence | Status |
| --- | --- | --- |
| The skew verdict depends on the calibration | Pre-freeze sweep at like rate about 0.02 (2 seeds, earlier code state): +0.102649 and +0.090614. M4 check (5 seeds, current code): +0.1045 at 0.02, +0.1026 at 0.05, +0.0724 at 0.15, then -0.1258 at 0.30 and down to -0.7106 at 0.85 | exploratory: confirms limitations 15 with the current code; the frozen verdict holds only at the frozen like rate |
| Choice sharpness confounded with like rate | tau varied at a matched like rate (refitted midpoint), so sharpness and like rate are separated | addressed (by design) |
| Unpaired interaction | Welch interval with fractional df; recomputed independently in the audit | addressed |

### 1.4 EXP-004: the contrast holds with MovieLens-derived inputs

| Competing explanation (protocol) | Evidence | Status |
| --- | --- | --- |
| (a) Catalog skew rather than preference realism | EXP-003 isolates skew on synthetic users; EXP-004 combines both, so their separate roles are not identified | partly |
| (b) Preference construction (add-one smoothing, division by catalog share) | Not varied | open (limitations 10) |
| (c) Selection in MovieLens ratings | Shapes the vectors and L*; not varied | open (limitations 9) |
| Not in the protocol: like rate | EXP-004 runs at c_ML fitted to the same L*; the M4 check does not cover MovieLens inputs | open |
| Seeds resample one population | 20 seeds draw 200 of the same 3,020 vectors | disclosed: inference is conditional on that population |

## 2. Exploratory sensitivity: XPL-M4-LIKERATE

- **Why.** The freeze record (C4) shows that under the planning midpoint the exploratory primary contrast was null (-0.000688, 10 seeds) and the Zipf contrasts were positive. The recalibration to L* = 0.577 was approved with these values available. The confirmatory design fixed one like rate, so no confirmatory result can say whether the main effect depends on it. This was the single largest gap between the registered competing explanations and the evidence.
- **What.** Settings of the EXP-003 tau 0.1 block (static, eta 0.1, alpha_0 1.0); midpoint refitted by the frozen calibration method (protocol 15.5) for target true like rates 0.05, 0.15, 0.30, 0.45, 0.577, 0.70 and 0.85, plus the planning midpoint 0.5; arms random and similarity; uniform and Zipf catalogs; 5 seeds (960001 to 960005); 160 runs, 0 failed; about 61 s per catalog with two worker processes.
- **Result (manuscript Table 7, `results/exploratory/m4-likerate-summary.csv`, FIG-M4-X01).** Uniform: near zero up to 0.05, -0.0384 at 0.15, -0.2396 at 0.30, a plateau between -0.3910 and -0.3961 from 0.45. Zipf: positive up to 0.15, negative from 0.30, growing to -0.7106 at 0.85. At the frozen calibration the check reproduces the confirmatory values (-0.3961 against -0.4001; -0.5021 against -0.5060).
- **Status.** Exploratory, post hoc, 5 seeds, one setting of tau, eta and alpha_0. It bounds the interpretation; it does not replace or alter any frozen verdict.

## 3. What the review changed in the conclusions

1. The main interpretation "the ranking objective reduces exposure diversity" is restated as conditional on the calibrated like rate: confirmed at 0.577; exploratory evidence that it vanishes at low like rates.
2. EXP-003's frozen verdict ("not restricted to balanced pools") stands as a verdict, but its scope is stated as "at the frozen calibration". The pre-freeze sign reversal is now reproduced with the current code and reported beside the verdict with equal prominence.
3. EXP-002's drift-form robustness is reported as weak, not as evidence of robustness to drift form.
4. EXP-004's agreement with EXP-001 is reported as agreement at one shared like-rate target, not as independence from calibration.
5. Diversity-aware re-ranking: the recovered share is reported per cell (0.353 to 0.793), not as a single figure.

## 4. Expected versus observed

| Test | Prediction (protocol) | Observation | Verdict under the frozen rule |
| --- | --- | --- | --- |
| EXP-001 primary | Similarity lowers H_exp vs random (expected by construction) | -0.4000 [-0.4028, -0.3972] | H1 supported |
| EXP-001 secondary cells | Same, per (eta, alpha_0) cell | -0.3938 to -0.3959 | H1 supported in all three |
| EXP-001 other arms | Holm-adjusted secondary contrasts, no directional rule | popularity -0.0089, bandit -0.2920, MMR -0.1853, MMR - similarity +0.2147 | no frozen verdict; popularity below the smallest effect of interest |
| EXP-001 nested bandit level | Descriptive only (D-013) | alpha_ucb 0.1 lower H_exp than 1.0 in all four cells | no test |
| EXP-002 primary | Similarity concentrates preferences more than random | -0.4350 [-0.4387, -0.4313] | H1 supported |
| EXP-002 secondary cells | Same, per (gamma, alpha_0) cell | -0.4336 to -0.4583 | H1 supported in all three |
| EXP-002 drift form | Dependent if sign changes or abs(D) < 0.05 | -0.4363, -0.4351 | not dependent (weak check) |
| EXP-002, random arm | Not predicted | preferences spread under random (+0.0971) | unanticipated; reported |
| EXP-003 skew | Gap may shrink; restrict to balanced pools if criterion met | -0.5060 (tau 0.1), -0.5365 (tau 0.3): gap widened | criterion not met; no sign reversal |
| EXP-003 sharpness | Effect may weaken at tau 0.3 | -0.3861 (uniform), -0.5365 (Zipf) | criterion not met |
| EXP-003 interaction | Non-directional | -0.1059 [-0.1170, -0.0948], -0.1503 [-0.1611, -0.1396] | reported |
| EXP-004 primary | Contrast may shrink with real preferences | -0.4095 [-0.4210, -0.3980] | H1 supported; EXP-001 interpretation not restricted to the synthetic generator |
| XPL-M4-LIKERATE (exploratory) | No registered prediction; the pre-freeze values suggested a null at low like rates | null at 0.02 to 0.05 (uniform); reversal at 0.02 to 0.15 (Zipf) | none (exploratory) |
