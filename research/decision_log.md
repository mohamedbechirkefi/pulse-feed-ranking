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

## D-011: Fitted calibration values replace the planning midpoint (2026-11-24)

- **Decided by:** the method of D-010 (owner-approved); fit by the data-freeze session. Journal CAL-ML1M (exploratory), output `results/calibration/calibration.json`, code revision 718e995 (clean).
- **Values:** L* = 0.577143 (calibration half, 491,374 ratings); c(0.1) = 0.066421; c(0.3) = 0.005990; c_ML(0.1) = 0.061067. pi_ML and topics in protocol section 15.11.
- **Consequences:** `like_midpoint` set (unrounded) in all confirmatory configs; EXP-003 split into blocks `tau0.1` and `tau0.3`; EXP-004 added (60 runs). Resolves D-008 P1 (option: recalibrate to a target like rate, as approved). P2 resolved by protocol 15.7, P3 by 15.8 (20 seeds), P4 by 15.9; P5 needed no change.

## D-012: Protocol v1.0 frozen (G-FREEZE, owner-approved 2026-11-24)

- **Decided by:** the owner ("yes for all others"; "Approve all"; owner approvals 2026-11-24, both rounds).
- **Frozen revision:** a25d4098afbd67413f17e9b98d5af15943b4169b. Freeze record: `research/freeze.json`.
- **SHA-256:** `research/protocol.md` 87fbfae1016c543f9736828d8e17d7015d42b894e62886eb798f38e3d8fcb12c; `data/manifest.json` 296b1edc9522d06275b20fc29fae08b0fc0405f880cf81fc9174ee26699a9fc0; experiment protocols and configs (file and canonical hashes) in `research/freeze.json` and the registry (EXP-001 fbb70fc9..., EXP-002 e1f4d229..., EXP-003 07e68a73..., EXP-004 dc004421...).
- **Common decisions:** C1 real data as approved (MovieLens 1M for calibration and EXP-004), synthetic otherwise; C2 pandoc and Typst PDFs; C3 authorship "Mohamed Bechir Kefi", no affiliation, AI disclosed as a research and development assistant; C4 exploratory primary-contrast values seen before the freeze listed in the freeze record (all under the planning midpoint 0.5).
- **Guard:** `pulse.runner.freeze_check` accepts the four frozen configs and refuses a changed config file, a changed config dict, a changed protocol or a changed data manifest (tests in `tests/test_freeze_guard.py`).
- **Not applied:** outdated reproduction-command text in EXP-001 to EXP-003 (not in the approved list).
- **Next:** confirmatory runs (M3) are scheduled by the coordinator; none has run.

## D-013: Analysis code for the frozen decision rules, written before any confirmatory output (2026-11-25)

- **Decided by:** the M3 session, within the frozen protocol (no protocol, config or seed changed). Committed before any confirmatory run.
- **Why:** the M2 report generator computes every paired contrast and Holm family, but not the frozen verdicts, the EXP-003 Welch skew interaction or the EXP-002 drift-form rule. Writing them after results exist would be analysis chosen after seeing data.
- **What:** `src/pulse/analysis.py`, `scripts/analyse_experiment.py`, `tests/test_analysis.py`. The decision rule is applied to the 95% paired t-interval; the bootstrap interval is reported as a check only (protocol section 7).
- **Readings of the frozen text that the code fixes (owner may review):** (1) H1 is supported only if the t upper bound is below 0 and the point estimate is at or below -0.05; otherwise the contradiction is reported with its reason (sign reversal, interval includes 0, or no practically relevant reduction). (2) EXP-003: the skew criterion is evaluated in both Zipf cells (tau 0.1 is the designated primary cell) and an interval lying entirely above 0 also meets it (protocol 15.9); "likewise for tau = 0.3" is evaluated in both tau 0.3 cells. (3) EXP-003 interaction: per tau block, mean Delta(Zipf) minus mean Delta(uniform), Welch t-interval with fractional Welch-Satterthwaite degrees of freedom. (4) EXP-002 drift form: per alpha_0, the sign of the point estimate D under additive-then-clip is compared with D under the multiplicative rule at gamma = 0.05 in the main block; |D| < 0.05 under the check also counts as dependence. (5) EXP-001 nested bandit level alpha_ucb = 0.1 has no frozen test; it is reported descriptively (per-arm summary) and any paired comparison of it is labelled exploratory.

## D-014: M3 confirmatory execution record (2026-11-25)

- **Authority:** the owner's "Start next" of 2026-11-25, which starts M3 (coordinator brief).
- **Provenance revision:** f1838f3e8451c8c4275579a5736fe488354a8f3a (clean tree; all frozen hashes verified before launch; run guard accepted all four configs). Data manifest SHA-256 296b1edc...; MovieLens zip re-verified a6898adb... by `scripts/download_movielens.py` (no re-download); held-out preference file 75f9fb8f... (matches the config).
- **Executed:** EXP-001 480/480, EXP-002 480/480, EXP-003 240/240, EXP-004 60/60 runs, all ok, none failed, none excluded, no retry. At most two worker processes, `nice -n 10`. Wall clock: EXP-001 904.6 s, EXP-002 828.2 s (in parallel), EXP-003 252.2 s, EXP-004 72.4 s (in parallel); 2026-11-24T23:33:55Z to 23:53:26Z UTC.
- **Deviations from the frozen protocols:** none. Analysis used only the frozen rules (D-013), committed before any confirmatory output.
- **Raw results:** 4.0 MB in total (below the 20 MB threshold), so `results/raw/EXP-00N/` and `results/raw/logs/` are committed with `git add -f` (the directory is git-ignored as a precaution for large outputs). EXP-004 files hold run-level aggregates only, no MovieLens row-level data.
- **Not done:** the standalone experiment reports (`research/experiments/EXP-00N/report.md`, master prompt 11.3) were not written: the file tool refused to create them in this session and the coordinator instructed not to work around a refusal. The analysis outputs, generated tables (`tables.md`) and figures exist for each experiment. M3 is therefore not marked done.
- **Found after the results (recorded, not acted on):** the EXP-002 drift-form check is close to a reparametrisation of gamma (limitations item 12). No code, config or protocol was changed.

## D-015: Owner decision on the missing experiment reports (2026-11-25)

- **Decided by:** the owner, 2026-11-25, "approve all recommendations, RIGGED A" (`labs/_shared/owner-approvals-2026-11-25.md`, item 4, outside this repository). Item 4: the owner approves writing the missing 11.3/11.6 experiment reports (`report.md`, and `reproduction.md` where the repo uses it), from the committed results, tables and figures only; nothing is recomputed and no numbers change.
- **Applies to PULSE:** `research/experiments/EXP-00{1,2,3,4}/report.md` and `reproduction.md` (CLAUDE.md section 2 lists `reproduction.md` in the experiment folder). Items 1 to 3 and 5 to 12 concern other projects.
- **Effect on records:** no change to limitations, claims or the freeze record (writing reports is not a protocol deviation).
- **Outcome in the M3 close session:** the file tool again refused to write `report.md` (first attempt: EXP-001). As the close brief requires, the session stopped report writing and used no shell or other workaround. The reports and `reproduction.md` files remain unwritten; M3 stays open.
- **Change of plan (coordinator, 2026-11-25, `labs/_shared/report-return-note.md`):** report files are written by the coordinator, never by subagents. The M3 close session composed the four `report.md` and four `reproduction.md` files from committed results only (no recomputation, no new numbers) and returned them as text; the coordinator writes and commits them. The M3 line of `progress.md` is left to the coordinator.

## D-016: M4 interpretation, exploratory like-rate check, evidence audit and manuscript (2026-11-25)

- **Authority:** the owner, 2026-11-25, "Approve all recommendations, push then next" (`labs/_shared/owner-approvals-2026-11-25b.md`, item 5: M4 for each project that has finished M3), and the coordinator's M4 brief (`labs/_shared/M4-brief.md`). No PULSE-specific follow-up is listed in that file.
- **Exploratory check XPL-M4-LIKERATE (agent choice within the brief: "new computation only when cheap and clearly labelled exploratory").** The confirmatory design fixes one like rate, and the freeze record shows a null primary contrast at the planning like rate; no committed result could say whether the main interpretation depends on it. The check refits the midpoint by the frozen calibration method for seven target like rates plus the planning midpoint, under the EXP-003 tau 0.1 settings, with arms random and similarity, uniform and Zipf catalogs, 5 seeds (960001 to 960005): 160 runs, 0 failed, two worker processes, about one minute each. Labelled exploratory everywhere, kept in `results/exploratory/`, never pooled, and it changes no frozen verdict. It was designed after the confirmatory results were seen.
- **Outcome:** the similarity effect is below the smallest effect of interest at like rates of 0.15 or less (uniform) and reverses sign under Zipf at those like rates. The interpretation of every confirmatory result is restated as conditional on the calibrated like rate (limitations 17; manuscript section 5.5; report addenda).
- **Evidence audit:** `scripts/m4_evidence_audit.py` (independent recomputation from raw files and number trace), `scripts/m4_build_manifest.py` (artifact manifest), `scripts/m4_derived_ratios.py` (MMR recovery shares). No mismatch between committed result numbers and raw outputs. One wording error corrected in the EXP-002 report ("roughly halved" to the measured 37%, F-3).
- **Claims register:** rebuilt with result id, run ids, config hash, figure or table and manuscript section; CLM-009 to CLM-014 added.
- **Manuscript:** synthesised to master prompt 11.4 (version 0.2), revised after the second review pass (`research/publication/review_pass_2.md`). Status: independent research manuscript / preprint draft, not peer-reviewed. No PDF built (M6).
- **Not changed:** no frozen protocol, config, seed or verdict; no confirmatory rerun.
- **Owner may review:** whether the post hoc like-rate dependence should become a new registered experiment (EXP-005) with its own frozen protocol before any public release; the manuscript's title choice.

## D-017: Manuscript title and statements, owner-approved after M4 (2026-11-25)

- **Authority:** owner, 2026-11-25, "Approve all" (post-M4) (`labs/_shared/owner-approvals-2026-11-25c.md`, items 1 and 2, outside this repository). Item 1: "The titles proposed in M4 are approved for SWARM, PULSE, CHAOS, STREAK, MATCH, FARE, HERD and VIRAL." Item 2: "The wording drafted in each manuscript is approved. Where a draft still has a placeholder that needs a fact only the owner knows, it stays a placeholder."
- **Title (item 1):** the M4 proposal is the title already in `research/paper/manuscript.md` version 0.2, "Content-similarity ranking and topic exposure in a matched-pool recommender simulation: confirmatory effects and a like-rate boundary". It is the only proposed title: `research/publication/review_pass_2.md` section 2 records the 0.1 draft title as rejected and this one as its revision. No change to the file was needed; the title is now owner-approved.
- **Statements (item 2):** the funding, competing-interest and AI-use wording of manuscript section 11 ("No funding. No competing interests. An AI system (Claude, Anthropic) acted as research and development assistant ...") and the authorship and AI line under the title are owner-approved. No wording changed.
- **Placeholders kept:** listed in `progress.md` under "Owner placeholders for M5".

## D-018: EXP-005 registered, not frozen: like-rate dependence of the primary contrast (2026-11-25)

- **Authority:** owner, 2026-11-25, "Approve all" (post-M4) (`labs/_shared/owner-approvals-2026-11-25c.md`, item 3): "PULSE: like-rate dependence (EXP-005). Each gets a protocol and config written before any data. The freeze needs the owner's G-FREEZE word as usual."
- **Done:** `research/experiments/EXP-005/protocol.md` (11.2 structure, draft v0.1) and `research/experiments/EXP-005/config.json` (draft, not runnable); registry row with status "registered, not frozen" and no protocol hash, so the run guard refuses a confirmatory run.
- **Derived from the frozen design v1.0:** world and settings of the EXP-003 `tau0.1` block; arms random and similarity; uniform and Zipf catalogs; midpoint fitted by the frozen method of protocol 15.5, fitted on the uniform world and reused under Zipf; reference level L* = 0.577 with its frozen midpoint; 20 seeds per cell (protocol 15.8), first seed 105001 by the EXP-00N convention; per-level decision rules of protocol section 3 and 15.9; uncertainty, exclusion and stopping of protocol sections 7 and 8.
- **Left open for the owner at freeze (not chosen):** OPEN-1 like-rate levels; OPEN-2 levels designated for the dependence contrast; OPEN-3 its threshold and Holm family; OPEN-4 tau 0.3 block; OPEN-5 MMR arm; OPEN-6 compute budget.
- **Disclosure:** designed after the confirmatory results and the exploratory XPL-M4-LIKERATE check were seen (protocol section 0). The exploratory values are never pooled with EXP-005.
- **Not done:** no computation, no midpoint fit, no hash added to `research/freeze.json`, no config in `experiments/`. Before freeze, still to write and test: the midpoint-fit script for the owner's levels and the analysis extension for several levels and the dependence contrast.

## D-019: M5 interactive page, exported results, sandbox port and consistency checks (2026-11-25)

- **Authority:** owner, 2026-11-25, "Next" (`labs/_shared/owner-approvals-2026-11-25d.md`, outside this repository), which starts M5 in the repositories whose M4 is done, PULSE among them. Stack named there: "The master prompt's default stack is used: TypeScript, React and Vite. Versions are pinned and come from the shared template, `labs/_shared/demo-template/`, which was verified on 2026-11-25." The same record states that "Next" does not freeze PULSE EXP-005 (G-FREEZE), authorise any push (G-PUBLIC) or decide any owner-only fact. Coordinator brief: `labs/_shared/M5-brief.md`.
- **Stack:** the shared template copied into `demo/` without `node_modules`, `npm ci --prefer-offline` (53 packages), `.npmrc` kept (install scripts disabled). No pinned version changed and no dependency added; charts are hand-written SVG.
- **Exported results:** `scripts/export_demo_data.py` writes `demo/public/data/results.json` (schema `lab-demo-results` 1.0.0) from committed files only: `verdict.json` and `contrasts.csv` of EXP-001 to EXP-004, EXP-001 `summary.csv` and `tables.md`, `results/exploratory/m4-likerate-summary.csv`, the pre-freeze probe's `contrasts.csv`, the registry, the claims register, the artifact manifest and `research/limitations.md`, each listed with its SHA-256. Nothing is recomputed; no timestamp. `code_revision` is the revision recorded for every confirmatory artifact in the manifest (f1838f3e8451c8c4275579a5736fe488354a8f3a, the revision of the confirmatory runs). Seven entries: EXP-001 to EXP-004 (confirmatory), XPL-M4-LIKERATE and XPL-VAR-PROBE (exploratory, shown with the same format and weight), EXP-005 (registered, not frozen, not run; no estimate). Project keys `exposure_heatmap` (measured EXP-001 per-arm H_exp with SD) and `likerate_curve` (manuscript Table 7), validated fail-closed by the extended `validateResults`.
- **Exception to "display text verbatim in the manuscript":** the heatmap prints per-arm means with SDs, which the manuscript tabulates only for two arms; those strings are checked verbatim against the committed report table `research/experiments/EXP-001/tables.md` instead (`tests/test_demo_export.py`).
- **Sandbox (labelled "illustrative, not the research engine"):** `demo/src/engine.ts` ports the loop, the five rankers, the tie rule (D-006) and the metrics. `scripts/export_sandbox_fixture.py` records every random input of three tiny Python runs (11 ranker runs) from the research engine's own streams; `demo/src/engine.test.ts` replays them and requires identical slates and metrics within 1e-9 (all pass). The browser uses seeded mulberry32 streams, Box-Muller normals and Marsaglia-Tsang gamma draws instead of numpy's generators, and a reduced world (60 users, 300 items, pools of 30, slates of 10, 120 steps, window 30), so a sandbox seed never reproduces a research run. The label is therefore "illustrative, not the research engine", although the loop itself matches the research code on shared inputs.
- **No compulsive-use design:** bounded runs, no autoplay, no endless feed, no score or reward; items are numbered synthetic items, not content. No visitor data is collected, stored or sent; the optional JSON save is a local download.
- **Checker extension (stricter, never weaker):** `demo/tools/a11y_check.mjs` keeps every template check and adds step 8: after the offline sandbox run it checks that the feeds render, 360 px overflow, light and dark contrast, and keyboard reach of every sandbox control. Region and control ids were added on the page because the template's keyboard check keys elements by id or text, and identical tables or selects collided.
- **Manuscript:** section 10 now describes the demo; section 9 records that the like-rate test is registered as EXP-005, not frozen, not run. No number changed (`scripts/m4_evidence_audit.py` unchanged result: one explained arXiv token).
- **Texts:** README rewritten from its M0 state (status, verified results table, navigation, demo quick start, screenshot `docs/demo.png`); article drafts `articles/medium.md` and `articles/linkedin.md` written; every decimal number in them traced to the manuscript or EXP-001 `tables.md`. Placeholders kept visible: repository and demo address, article byline. `research/publication/author_review.md` has no ticked box (nothing to untick). No sentence claiming that the owner had not reviewed something was found.
- **Not changed:** no frozen protocol, config, seed or result; EXP-005 protocol and config untouched; no run; no push.

## D-020: M6 release candidate prepared (2026-11-25)

- **Authority:** owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`, outside this repository): "M6 (release candidate) in the 19 repositories whose M5 is done: block, chaos, echo, evolve, fare, flow, frame, herd, house, market, match, memory, paradox, pulse, rigged, streak, swarm, trust, viral. M6 is local work: a clean clone, PDFs, checks, and a release candidate prepared for the owner's review." Coordinator default applied under it: "`CITATION.cff` `date-released`: the field is removed until a release exists, because no release has been made." The same record states that it does not decide any push, release, licence change or publication (G-PUBLIC), the ticking of any `author_review.md` box, or the freeze of PULSE EXP-005 (G-FREEZE). Coordinator brief: `labs/_shared/M6-brief.md`.
- **Clean clone:** two clean clones (the M5 commit, then the fix commit); results in `research/publication/reproducibility_report.md`.
- **PDFs:** new builder `scripts/build_pdfs.py` (pandoc to Typst, the shared typst package; same toolchain as D-002), because `pulse.report.build_pdf` serves the exploratory report generator and was left unchanged. It sets the PDF title from the first heading, sizes table columns to content and lets long hashes break; `manuscript.tex` is generated by pandoc. The PDFs are committed (no rule excludes them).
- **F-7 resolved (code change, no result change):** `src/pulse/analysis.py` records `results_dir` relative to the repository. The four `run_manifest.json` files were regenerated from the committed raw files; only that line changed, and every other analysis output was byte-identical. This touches provenance metadata, not a frozen protocol, config, seed or result value.
- **F-5 narrowed:** nine primary sources and one new secondary source (`dasilva2025calibrated`, arXiv:2507.02643) read in full from free, legal copies; Steck 2018 remains metadata only (ACM HTTP 403; third-party copies not used). The manuscript says the formula was checked against a secondary source only.
- **CITATION.cff:** `date-released` removed (coordinator default above); version `0.2.0-rc1`, chosen to match manuscript version 0.2 and to mark a release candidate; title set to the owner-approved manuscript title (D-017), as the brief requires the citation title to match the manuscript. Structure checked against CFF 1.2.0 (required keys `cff-version`, `message`, `title`, `authors` present with the expected types; parsed as YAML by pandoc). The owner may choose differently at release.
- **Path and identifier scrub:** home-directory paths removed from current documents; kept in frozen protocols, execution logs and the append-only journal, which are not edited. The commit-trailer address in `CLAUDE.md` replaced by a reference to the session brief.
- **Not changed:** no frozen protocol, config, seed or result value; no confirmatory run; EXP-005 untouched (registered, not frozen, not run); no `author_review.md` box ticked; no licence file; no push, tag, release or remote.
- **Status:** M6 is "release candidate prepared, awaiting owner review and G-PUBLIC"; it is not done until the owner signs off.
