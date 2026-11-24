<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Decision log (append-only)

Each entry: id, date, decision, decided by, context, alternatives, consequences.

## D-001: Licence is the owner's custom non-commercial licence (2026-11-24)

- **Decided by:** the owner.
- **Decision:** all original material in this repository is licensed under the PULSE Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-PULSE-NC-Research-1.0`), with the CLA v1.0 for contributions. Files: `LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS`, `.github/workflows/cla.yml`.
- **Context:** master prompt section 2 asks for an "owner-approved permissive code license". On 2026-11-24 the owner chose this protective licence instead, for their own protection.
- **Alternatives:** a permissive licence (MIT, Apache-2.0) as the prompt suggests. Rejected by the owner.
- **Consequences:** the project is source-available, not OSI open source. Public text must not describe it as "open source". Third-party data and dependencies keep their own licences (NOTICE.md section 2). Sessions must not change the licence files.

## D-002: Zero-cost publication toolchain without TeX (2026-11-24)

- **Decided by:** M0 session, per the owner's brief; open to owner review.
- **Decision:** Markdown is canonical. PDFs are built by pandoc 3.6.3 (Markdown to Typst, with `-V mainfont="Libertinus Serif"`) and compiled by the `typst` 0.15.0 Python package. `manuscript.tex` is generated from Markdown by pandoc and is not compiled.
- **Context:** no TeX distribution is installed (`which tex pdflatex xelatex`: not found). Installing one is unnecessary.
- **Evidence:** exploratory toolchain smoke on the manuscript skeleton produced a 1-page PDF in the session scratchpad (not committed); see `progress.md` 2026-11-24. Without `mainfont`, typst failed with "font fallback list must not be empty".
- **Consequences:** report generators (M2) must pass the font variable. LaTeX output is provided as source only.

## D-003: Synthetic data only; no external dataset (2026-11-24)

- **Decided by:** M0 session proposal; awaiting owner confirmation.
- **Decision:** all registered experiments use the synthetic generator specified in `research/protocol.md`. MovieLens, KuaiRec and MIND were checked for licence only and are not used (`data/manifest.json`).
- **Reason:** the question is about mechanisms under explicit assumptions; real logs would add rights questions (KuaiRec ShareAlike and commercial-app provenance; MovieLens same-terms redistribution; MIND licence not verified) without testing the registered hypotheses.

## D-004: Protocol proposal v0.1 is a draft (2026-11-24)

- **Decided by:** M0 session.
- **Decision:** `research/protocol.md` v0.1 and EXP-001 to EXP-003 protocols are drafts. Primary comparator: random ranker. Primary metric: final-window normalised exposure topic entropy. Primary contrast: content similarity minus random, static preferences. Not frozen (G-FREEZE: the owner freezes).
- **Pending:** owner review, possible seed-count change after the exploratory smoke run, freeze with SHA-256.

## D-005: Dependency resolution cutoff (2026-11-24)

- **Decision:** `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"`, so every locked version was published at least two weeks before 2026-11-24. Locked: numpy 2.3.5, pytest 8.4.2 (and pytest's dependencies).

## D-006: Tie rule rounds scores to 12 decimals before comparison (2026-11-24)

- **Decided by:** M2 session (implementation fix); open to owner review.
- **Decision:** every ranker rounds its scores to 12 decimal places before sorting; items with equal rounded scores are ordered by ascending tie key from the shared seeded "tiebreak" stream (`src/pulse/rankers.py`).
- **Context:** the test `test_zero_feedback_rankers_fall_back_to_tie_order` failed on first run: LinUCB cold-start scores (alpha / sqrt(lambda), equal in exact arithmetic) differed by about 1e-16, so slate order was set by floating-point round-off instead of the documented tie rule. The failure was recorded before the fix.
- **Consequences:** under zero feedback, popularity, similarity and LinUCB produce exactly the random arm's slate (tested). Scores that differ by less than 5e-13 are treated as ties.

## D-007: Operational clarifications made while implementing protocol v0.1 (2026-11-24)

- **Decided by:** M2 session; awaiting owner review before freeze. None of these changes a hypothesis, metric choice or comparator; each fixes a detail the draft left open.
- Examination: each position j (1-based) is examined independently with probability beta^(j-1) (not a cascade).
- Feedback: every examined item gets explicit feedback; rankers learn only from examined items' observed (noisy) feedback.
- Drift: uses true likes (the noise is observation noise), applied after the step in slate order; utility within a step uses p_u(t) at the start of the step.
- Gini: item exposure counts are unweighted slate appearances in the final window.
- Relevance and like rate: final window. User control: all consecutive step pairs (t, t+1), unweighted slate topic shares, one event per observed dislike of an examined item.
- Miscalibration: KL against p_u at the end of the run (equal to p_u(0) under the static model).
- Candidate pools: drawn per (user, step) by argpartition of uniform keys, then sorted by item id, so the pool order carries no information.
- Peak memory: process-wide peak RSS (runs share one process), recorded as such in each manifest.
- Seeds: confirmatory configs use 101001+, 102001+, 103001+ (EXP-001 to EXP-003); exploratory configs use 900001+ and higher, disjoint from every confirmatory seed.

## D-008: Proposed protocol amendments from the exploratory smoke runs (2026-11-24, owner decision)

- **Status:** proposals only. Not applied to `research/protocol.md` or any EXP protocol. The owner decides before freezing (G-FREEZE).
- **Disclosure:** to estimate the paired-difference SD (protocol section 6) the session necessarily saw exploratory values of the primary contrast in the primary cell (seeds 910001 to 910010, disjoint from confirmatory seeds). Any amendment adopted now is therefore informed by exploratory outcomes and must be recorded as such in the frozen protocol.
- **P1, choice-model calibration (degenerate feedback).** With the draft utility r_ui = sum_z p_uz pos_share_iz, r is about 0.10 for nearly every item when alpha_0 = 1.0, so sigmoid((r - 0.5) / 0.1) gives an observed like rate of about 0.02 at eta = 0 (sweep-EXP-001, var-probe). About 98% of feedback is "dislike", the similarity profile is dominated by subtracted embeddings, and at eta = 0.2 most observed likes are flips (like rate about 0.21 against 0.02 true). Options: (a) keep v0.1 and report the primary contrast as a property of this calibration; (b) centre the curve per user, sigmoid((r_ui - rbar_u) / tau) with rbar_u the user's mean utility over the catalog; (c) rescale utility so that a user's top topic gives r near 1 (for example r / max_z p_uz). Option (b) or (c) changes the generative model and should be justified by the like rate, not by the effect size.
- **P2, user-control reference.** The random arm, which ignores feedback, scores about -0.089 on the user-control metric (regression of slate shares after a disliked topic appears). Propose that user control is only interpreted as a paired difference against random, stated in the protocol.
- **P3, seed count.** The rule in protocol section 6 is met at n = 10 (SD of paired differences 0.0022 in the primary contrast, threshold 0.07; largest H_exp contrast SD 0.0075, popularity). Because the full matrix is cheap (about 16 minutes projected at 10 seeds), the owner may raise to 20 seeds for all experiments before the freeze; this is optional, not required by the rule. If P1 is adopted the SD must be re-estimated.
- **P4, EXP-003 interpretation under P1 = (a).** Under the Zipf catalog the random arm's H_exp falls to about 0.863 while similarity stays about 0.965 (2 seeds), so the contrast changes sign because the dislike-dominated profile pushes away from the abundant topic. The registered invalidation criterion still applies, but the protocol should state in advance how a sign reversal is reported.
- **P5, compute budget.** Projected full-matrix wall clock (single process) is about 16 minutes against the 4-hour budget; no change needed.

## D-009: Real data adopted: MovieLens 1M, licence checked (2026-11-24)

- **Decided by:** the owner ("Approve all", owner approvals 2026-11-24, second round, section 1: "PULSE | MovieLens (research use, no redistribution) | Real user and item preferences for the feed simulation"). Supersedes D-003 (synthetic only) for PULSE.
- **Licence check:** README `https://files.grouplens.org/datasets/movielens/ml-1m-README.txt`, accessed 2026-11-24 (SHA-256 908ee4aa21a8d37aec0cb6c1cdcc41f9bba3c5d2fef3d9250a8073b8e460027e). Terms: "may be used for any research purposes" on conditions: no stated or implied endorsement by the University of Minnesota or GroupLens; acknowledge use in publications (cite Harper and Konstan 2015, doi:10.1145/2827872); "may not redistribute the data without separate permission"; no commercial or revenue-bearing use without permission. This matches the approval, so the data is adopted.
- **Variant:** MovieLens 1M (smallest stable standard variant fit for the purpose; `ml-1m.zip`, 5,917,549 bytes, SHA-256 a6898adb50b9ca05aa231689da44c217cb524e7ebd39d264c56e2832f2c54e20, downloaded 2026-11-24T18:31:56Z by `scripts/download_movielens.py`, hashes pinned in the script).
- **Handling:** never committed (`data/raw/`, `data/processed/` git-ignored); only aggregates are committed. `users.dat` (age, gender, occupation, zip code) is never read. No row-level data with identifiers enters any committed file.
- **Consequences:** C1 for PULSE reads "real data as approved": calibration of the choice curve and a second test EXP-004 (protocol section 15).

## D-010: Amendments before freeze, round 2: method written before fitting (2026-11-24)

- **Decided by:** the owner (section 7 of the approvals file, approved earlier as "yes for all others": "A target like-rate fixed in advance (from MovieLens if available, otherwise stated now), with the choice curve recalibrated to it and the calibration disclosed. User control measured as the difference from random. 20 seeds. Pre-decide how a sign reversal under the Zipf catalog is reported."), together with the real-data adoption (D-009).
- **Decision:** `research/protocol.md` section 15: ingestion and topic rules, user split by UserID parity, target like rate L* from the calibration half, choice-curve midpoint c(tau) fitted by bisection on the generative model alone (no ranker, no metric), EXP-004 second test on held-out-half preference vectors, user control as arm minus random, 20 seeds, pre-decided sign-reversal reporting.
- **Order:** the method was committed before any rating was read or any value fitted (see git history). Fitted values follow in D-011.
- **Agent choices within the approval (owner may review):** using MovieLens for both calibration and a second test (the brief asks for "what is calibrated ... and what the second test is"); the parity split; the top-10-genre topic rule; fitting c per tau; leaving alpha_0 levels unchanged.
