<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Second review pass: arguing against the preferred hypothesis

Date 2026-11-25 (M4). Reviewed: manuscript draft 0.1 (written in this session from the committed results), the four experiment reports, the claims register and `interpretation_m4.md`. The preferred hypothesis is "the ranking objective, specifically content similarity, reduces exposure diversity and reinforces simulated preferences". This pass tries to break it. It is internal AI quality control, not external peer review.

## 1. Strongest alternative readings

**A1. The headline effect is a product of the calibration regime, chosen with a null in view.** Under the planning midpoint (like rate about 0.02) the exploratory primary contrast was -0.000688 on 10 seeds (freeze record C4). The recalibration to L* = 0.577 was approved after that value was seen, and under it the contrast is -0.4000. A sceptical reader can say the study found its effect by changing the user model.

- *Assessment: the challenge holds in part.* The stated reason for recalibrating was the degenerate like rate (98% dislikes), the method was written before the fit, and the target came from data rather than from the effect size. But the choice remained a researcher degree of freedom exercised with the exploratory contrast available. The M4 exploratory check shows the consequence directly: the effect is below the smallest effect of interest at like rates of 0.15 or less.
- *Change made.* The abstract now states that the calibration was chosen after a pre-freeze null; section 7 adds a limitation on it; the title no longer states the conditional as a finding ("only when ...") and instead names a "like-rate boundary"; the conclusion is restated as holding "in this model and at this calibration".

**A2. Narrowing is mechanical, not learned.** With one dominant topic per item and a profile built from summed embeddings, a similarity ranker must concentrate on whichever topics have accumulated likes; the result may say more about the embedding geometry than about "the ranking objective".

- *Assessment: holds as a scope limit.* The design cannot separate objective from geometry; item noise was never varied.
- *Change made.* Listed as an open competing explanation (`interpretation_m4.md` 1.1), named as a follow-up in the manuscript conclusion; the manuscript already says the direction was expected by construction.

**A3. Under skew, similarity can diversify exposure.** The pre-freeze sweep and the M4 check both show positive Zipf contrasts at low like rates. The frozen EXP-003 verdict ("not restricted to balanced pools") could be read as general robustness.

- *Assessment: holds.* The verdict stands under the frozen rule, but it is scoped to the frozen calibration.
- *Change made.* Manuscript sections 5.3, 5.5 and 6.2 and the claims register (CLM-006, CLM-007) state the scope; the reversal is in the abstract.

**A4. EXP-004 is not independent support for "real preferences".** It shares the like-rate target with EXP-001, uses constructed vectors, and resamples one pool of 3,020 users.

- *Assessment: holds.* Agreement with EXP-001 shows that replacing the Dirichlet generator did not change the result at one calibration; it does not show robustness to calibration or to the preference construction.
- *Change made.* Manuscript section 6.2 and `interpretation_m4.md` 1.4 list these as open; CLM-008's limit field names them.

**A5. EXP-002 shows only that the drift rule encodes reinforcement.** Under the multiplicative rule, any ranker that shows more of a topic produces more likes of it and more drift toward it.

- *Assessment: holds; already disclosed* (limitations 4). The drift-form check does not rescue it (limitations 12).
- *Change made.* None beyond keeping both limitations next to the result.

## 2. Overgeneralisation

| Draft text (0.1) | Problem | Revision (0.2) |
| --- | --- | --- |
| Title: "Similarity ranking narrows simulated exposure, but only when simulated users like much of what they see" | States an exploratory, 5-seed, post hoc pattern as the headline finding, and "only when" was never tested beyond one setting | Title names the confirmatory effects and a "like-rate boundary" |
| Abstract: "Diversity-aware re-ranking recovered 37% to 79% of the loss" | Mixes a preference metric (EXP-002) with exposure; later draft "more than half in every exposure test" was false (0.453 and 0.464 in two EXP-001 cells) | "between 45% and 79% of the exposure-entropy loss across cells (supplementary Table S3)" |
| Section 6.2: "the similarity effect needs a like rate of roughly 0.3 or more to appear" | Over-precise threshold from 8 levels and 5 seeds in one setting | Threshold stated as somewhere between 0.15 and 0.30, not located, exploratory |
| Section 6.3: "narrows topic exposure strongly once simulated users like a substantial share" | Presents the exploratory condition as supported | Split into a confirmatory statement at the calibrated like rate and an exploratory qualifier |
| Section 9: "they weaken to nothing at low like rates" | Generalises beyond the settings covered | "under the settings it covered, the exposure effect falls below the smallest effect of interest" |
| Section 6.2: drift "overwriting the initial preference" | Inference from equal like rates, presented as fact | Marked as a hypothesis, with the static comparison given |

## 3. Stale or untraceable figures

- All tables and figures were regenerated from the raw files in this session; every output was byte-identical to the committed file. No stale figure.
- Draft 0.1 contained numbers with no committed source: a per-run runtime range ("0.8 to 3 seconds") and a complexity bound for the rankers that was not checked against the code. Both were removed.
- Six values in the first draft of supplementary Table S3 were mistyped in the last digit; the table now matches `results/derived/mmr_recovery.csv` row by row, and the audit script checks it.
- Percentages are now derived by script (`scripts/m4_derived_ratios.py`).

## 4. Leakage

- **Calibration and test users.** L* and c_ML use the calibration half (odd user ids) only; EXP-004 samples the held-out half (even ids). Catalog weights pi_ML are item-level and use no user. No leakage found.
- **Calibration and outcome.** The fit uses the generators only, with no ranker or metric (protocol 15.5, `src/pulse/calibrate.py`). The outcome could not enter the fit, but the decision to recalibrate was taken with the exploratory outcome visible (A1).
- **Seeds.** Confirmatory, calibration (700001 to 700020) and exploratory ranges (900001 onward, including 960001 to 960005 for M4) are disjoint.

## 5. Missing failed runs

- Confirmatory: 1,260 of 1,260 runs ok, none excluded; verified against the raw files and manifests (evidence audit, Part A).
- Exploratory: all earlier exploratory sets and the M4 sets (160 of 160 ok) are committed under `results/exploratory/`, including the pre-freeze sets whose values contradict the confirmatory Zipf result.
- Not run: the M4 check did not cover drifting preferences, MovieLens inputs, eta or alpha_0 variations, or other tau values. These are stated as gaps, not as failures.

## 6. Statistical challenges

- **Large d_z, small seed variance.** Effects such as popularity's -0.0089 are "significant" with Holm-adjusted p < 0.0001 yet practically null. The manuscript uses the smallest effect of interest, not p-values, to interpret them (limitations 14). No change needed.
- **Multiplicity across experiments.** Holm is applied within families; no adjustment across experiments. The primary tests are pre-registered one per experiment, so the family-wise concern is limited; disclosed.
- **Exploratory intervals.** The 5-seed intervals in Table 7 are t-intervals with 4 degrees of freedom; they are wide relative to the confirmatory ones and are labelled exploratory.

## 7. Verdict of this pass

The confirmatory verdicts stand as computed under the frozen rules. The interpretation does not stand in its general form: the strongest alternative reading (A1, calibration regime) is supported by both the pre-freeze values and the M4 exploratory check. The manuscript was revised to version 0.2 accordingly (changes listed in sections 1 to 3). Remaining open: embedding geometry (A2), like-rate dependence under drift and with MovieLens inputs, a structurally different drift rule, and the Steck formula check.
