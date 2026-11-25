<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Claims audit checklist (M4, 2026-11-25)

Details: `research/publication/evidence_audit.md` (findings F-1 to F-9), `research/publication/review_pass_2.md` and `research/publication/interpretation_m4.md`.

- [x] Every row of `research/claims_register.csv` (CLM-001 to CLM-014) has a result id, run ids, config hash, figure or table, manuscript section, evidence path and limit.
- [x] Every number in the manuscript, supplementary file, experiment reports and claims register matches the committed result it cites (audit Parts A to D, manual checks). README, demo and articles (M5, 2026-11-25): the demo's display strings are checked against the manuscript by `tests/test_demo_export.py`; every decimal number in `README.md`, `articles/medium.md` and `articles/linkedin.md` was traced to the manuscript or `research/experiments/EXP-001/tables.md` (decision D-019).
- [x] Every external claim maps to a source listed in `research/literature_review.md`, with the extent of reading marked (abstract, first page, metadata only, not opened). Open: the Steck 2018 formula check (F-5).
- [x] No claim about real platforms, real users or addiction (manuscript sections 6.3, 7, 8).
- [x] Simulated claims are typed "simulation" in scope and limited to their assumptions; the exploratory claim CLM-012 and disclosure CLM-013 are labelled exploratory.
- [x] Second review pass challenged the preferred hypothesis; findings and the resulting manuscript changes are recorded in `review_pass_2.md`.
- [x] Unsupported claims removed or qualified: per-run runtime range and complexity statement removed; MMR "roughly halved" corrected; "more than half in every test" corrected; title and conclusion qualified to the calibration regime.
