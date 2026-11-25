<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Evidence audit (master prompt 11.5), M4

Date 2026-11-25. Scope: the four experiment reports, `research/paper/manuscript.md`, `research/paper/supplementary.md`, `research/claims_register.csv` and `research/publication/artifact_manifest.json`. Command: `PYTHONPATH=src .venv/bin/python scripts/m4_evidence_audit.py`; full output in `research/publication/evidence_audit_output.txt` (exit status 0).

## 1. Method

| Part | Check | Independence |
| --- | --- | --- |
| A | SHA-256 of every raw run file against `run_manifest.json`; run counts, status, code revision and dirty flag; every row of `contrasts.csv` (n, mean, SD, 95% t-interval) and `summary.csv` (means, SDs) recomputed from the raw per-seed metrics; EXP-003 Welch interaction; EXP-002 drift-form values | Uses numpy only. The t quantile is computed by numerical integration of the t density and bisection, not by `src/pulse/stats.py`. |
| B | Every decimal number with two or more decimals in the reports, manuscript, supplementary file and claims register must equal, at its printed precision, a number in a committed evidence file | Value matching only: a wrong number can pass if it happens to equal another value anywhere in the evidence (see finding F-6) |
| C | Manuscript sections 5.1 to 5.4 matched only against their own experiment's outputs; Table S3 and Table 7 checked row by row against `results/derived/mmr_recovery.csv` and `results/exploratory/m4-likerate-summary.csv` | Row-wise for the derived tables |
| D | Manuscript Tables 2 to 6 checked row by row: each formatted row is rebuilt from `contrasts.csv` and must appear verbatim | Row-wise |
| Manual | Denominators, units, sample counts, derived ratios and percentages, statements in words (for example "highest relevance", "recovered about half"), external citations | Read against the source files |
| Regeneration | `scripts/analyse_experiment.py` and `scripts/report_tables.py` rerun for all four experiments | Every regenerated `verdict.json`, CSV, `tables.md` and figure was byte-identical to the committed file (`git status` clean afterwards): no stale table or figure |

## 2. Results

- **Part A.** 1,260 raw run files, all hashes match; 480, 480, 240 and 60 runs, all status ok, all at f1838f3 with a clean tree; 351 contrast rows and 63 summary rows recomputed; Welch interactions -0.105896 [-0.117031, -0.094761] (df 21.196) and -0.150342 [-0.161115, -0.139569] (df 22.441) match `verdict.json`; drift-form values match. **0 problems.**
- **Part B.** 0 unmatched numbers in the reports, the supplementary file and the claims register. One token in the manuscript, `1003.0146`, is the arXiv identifier of Li et al. (2010), not a result.
- **Part C.** 0 unmatched numbers in manuscript sections 5.1 to 5.4 against their own experiment; 0 row errors in Tables S3 and 7.
- **Part D.** 23 table rows checked, 0 errors.
- **Sample counts and denominators.** Every interval in the reports and manuscript is over n = 20 seeds (confirmatory) or n = 5 (exploratory), as stated. Like rate is observed likes per examined item; the exploratory summary converts it to a true like rate with (observed - eta) / (1 - 2 eta), stated in `scripts/m4_likerate_summary.py`. Units: H_exp and Delta H_pref unitless (normalised entropy); miscalibration in nats; Gini, relevance and like rate in [0, 1]. Precision: four decimals for contrasts, two for d_z, six for calibration constants, as in the source tables.

## 3. Findings and fixes

| Id | Finding | Severity | Action |
| --- | --- | --- | --- |
| F-1 | The artifact manifest was empty (M0 placeholder) | gate blocker | Built by `scripts/m4_build_manifest.py`: 42 entries (figures, tables, analysis outputs, exploratory outputs and every claim), each with experiment id, run ids, metric definition, result path and SHA-256, generator script, config and protocol hash and code revision |
| F-2 | The claims register lacked the columns the M4 gate requires (result id, config hash, figure or table, section) | gate blocker | Register rebuilt with those columns; CLM-001 to CLM-008 kept, CLM-009 to CLM-014 added for claims the manuscript makes |
| F-3 | EXP-002 report said MMR "roughly halved the similarity contrast"; the data give a recovered share of 0.374 (MMR minus similarity +0.1626 against -0.4350) | wording error | Corrected in the report, with a note |
| F-4 | Draft manuscript errors caught by the audit and the second review pass before commit: (i) abstract said MMR recovered "more than half" of the loss in every exposure test, but two EXP-001 cells give 0.453 and 0.464; (ii) six MMR-minus-similarity values in the first draft of Table S3 were mistyped in the last digit; (iii) a per-run runtime range and a complexity statement had no committed source | draft errors | (i) restated as a per-cell range from `mmr_recovery.csv`; (ii) table regenerated from the derived file and now checked row by row (Part C); (iii) removed |
| F-5 | External sources: of the ten references, six were read only at the abstract page, two at the first page of the author PDF, Steck 2018 only at its metadata record, and Harper and Konstan 2015 was not opened (citation copied from the GroupLens README). The Carbonell and Goldstein DOI came from search results. The miscalibration formula attributed to Steck was never checked against the full text; a fetch of the ACM page on 2026-11-25 returned HTTP 403 | disclosure | Each reference in the manuscript is marked with what was read; related-work statements limited to those pages; the Steck formula check remains an open item for M6 |
| F-6 | Part B is permissive: it matches values, not positions, so a mistyped number can pass if it equals some other committed value (0.1785 matched an unrelated EXP-001 value) | audit limitation | Parts C and D added for the manuscript's result sections and tables; numbers in words outside those tables were checked manually |
| F-7 | `research/experiments/EXP-00N/run_manifest.json` records an absolute local path (`results_dir`) that includes the local user name | hygiene | Not changed in M4 (the files are generated analysis outputs whose hash would change); listed for the M6 scrub |
| F-8 | The exploratory runs were made at revision 17c2e5f with the M4 scripts present but uncommitted; `src/` is identical to f1838f3 (`git diff f1838f3 17c2e5f -- src` empty), and the run files record dirty = false because untracked files do not count | provenance note | Recorded in the journal, the manifest and here; the scripts are committed in the M4 commit |
| F-9 | Percentages in the manuscript (37%, 45%, 54%, 79%) are derived ratios not present in any CSV before M4 | traceability | `results/derived/mmr_recovery.csv` generated by script; each percentage rounds a value in it |

No mismatch was found between any committed result number and the raw outputs.

## 4. Strength and scope of evidence per conclusion

| Conclusion | Strength | Scope |
| --- | --- | --- |
| Similarity lowers H_exp vs random (EXP-001, EXP-004) | Strong within the model: 20 seeds, narrow intervals, replicated across four cells and on MovieLens-derived inputs | One calibrated like rate; synthetic catalog geometry; no real users |
| Similarity concentrates drifting preferences (EXP-002) | Strong within the model | One drift rule that encodes reinforcement; like rate not varied |
| Effect survives skew and flatter choice (EXP-003) | Strong at the frozen calibration | Exploratory evidence that the direction under skew reverses at low like rates |
| MMR recovers part of the loss | Strong within the model, descriptive across cells | Share varies from 0.353 to 0.793 |
| Popularity leaves topic entropy almost unchanged | Strong (interval excludes 0 but below the smallest effect of interest) | Topic-level only; item concentration rises |
| Like-rate dependence | Weak to moderate: exploratory, post hoc, 5 seeds, consistent with the pre-freeze values | One setting of tau, eta and alpha_0; static only |

## 5. Gate check (M4)

Every numerical claim in the manuscript maps to a claim id with result id, config hash and figure or table (`claims_register.csv`, `artifact_manifest.json`). Every external claim maps to a source listed in `research/literature_review.md`, with the extent of reading marked. One open item (F-5, the Steck formula) is disclosed rather than resolved.

## 6. M6 update (2026-11-25): external sources and provenance paths

This section is added at M6; the M4 sections above are kept as written.

### F-5, external sources: what was read

On 2026-11-25 every primary source was retried through free, legal copies only (arXiv, author or institutional pages; no paid access, no login, no third-party mirror). Text was extracted locally from each PDF (or, for the scanned Carbonell and Goldstein PDF, the two page images were viewed), and each statement the manuscript makes about the source was checked at the location below.

| Key | Copy opened | Label | Manuscript statement checked | Location |
| --- | --- | --- | --- | --- |
| chaney2018algorithmic | arXiv:1710.11214 (9 pages) | read in full | simulations; data confounded by the system's own recommendations; homogenised user behaviour without increased utility | abstract; section 2; section 5.2 |
| mansoury2020feedback | arXiv:2007.13019 (5 pages) | read in full | offline simulation of the feedback loop; popularity bias amplified; aggregate diversity declines | abstract; section 2; section 4.3 |
| jiang2019degenerate | arXiv:1902.10730 (10 pages) | read in full | formalises degenerate feedback loops; separates echo chamber from filter bubble; simulation with bandit algorithms | abstract; introduction (page 1); section "Simulation Experiments" |
| kalimeris2021preference | author PDF on the Facebook Research site (11 pages) | read in full | users drift toward recommended content (drift function); conditions for preference amplification | abstract; section 2.1 (Definition 1); section 3 |
| ie2019recsim | arXiv:1909.04847 (23 pages) | read in full | configurable user model, document model and user-choice model | section 3.1 |
| lucherini2021trecs | arXiv:2107.08959 (17 pages) | read in full | simulation tool with configurable users, items and preference dynamics | sections 4, 4.1, 4.2 |
| li2010contextual | arXiv:1003.0146 (10 pages) | read in full | LinUCB with ridge regression (A_a initialised to the identity) and exploration parameter alpha, which is how the bandit arm is implemented | section 3.1, equation (5), Algorithm 1 |
| carbonell1998mmr | author PDF (cs.cmu.edu), 2 pages, scanned | read in full | MMR = Arg max over unselected documents of lambda Sim1(D_i, Q) - (1 - lambda) max over selected Sim2(D_i, D_j); pages 335 to 336 | section 2; printed page numbers |
| harper2015movielens | author preprint (files.grouplens.org), 20 pages | read in full | MovieLens 1M: 6,040 users, 3,706 movies, 1,000,209 ratings, 1 to 5 stars | section 3, Table II |
| steck2018calibrated | none: ACM full text returned HTTP 403 (again on 2026-11-25); copies found by search were on third-party sites and were not used | unverified (metadata only) | KL miscalibration with q mixed with p at weight 0.01 | checked only against dasilva2025calibrated |
| dasilva2025calibrated (new, secondary) | arXiv:2507.02643 (27 pages) | read in full | restates Steck's measure: C_KL(p, q~) with q~ = (1 - alpha) q + alpha p and "a commonly used value for alpha is 0.01" | sections 3.1.4 (equation 5) and 3.1.5 (equation 6) |

Counts: 10 read in full (9 primary sources and 1 secondary source), 0 abstract only, 1 unverified (Steck 2018, metadata only). No checked statement disagreed with its source. Claim qualified: the manuscript now says that the miscalibration formula was checked against a secondary source only (sections 2 and 7). The Carbonell and Goldstein DOI and the Harper and Konstan volume, issue and DOI still come from search results and the GroupLens README respectively, and are marked so.

### F-7, absolute path in run manifests: resolved

`src/pulse/analysis.py` now records `results_dir` relative to the repository (`results/raw/EXP-00N`). `scripts/analyse_experiment.py EXP-00N` was re-run for N = 1 to 4 on the committed raw files: every analysis output (metrics, summary, contrasts, verdict, runs, config, figures) was byte-identical except the one `results_dir` line of each `run_manifest.json`. `scripts/m4_evidence_audit.py` after the change: exit 0; 1,260 raw files and 8 set files match their recorded SHA-256; Parts C and D 0 errors; the manuscript has 2 unmatched decimal tokens, both arXiv identifiers (1003.0146 and 2507.02643).

Absolute local paths remain, by design, in files that are frozen or raw: the frozen protocols (`research/protocol.md`, `research/experiments/EXP-001/protocol.md`, `research/experiments/EXP-004/protocol.md`), the execution logs (`results/raw/logs/EXP-00N.log`, `results/exploratory/logs/m4-likerate-*.log`) and the append-only `progress.md`. They are listed in `research/publication/reproducibility_report.md`, section 5.
