<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Owner review checklist (not started)

- [ ] Authorship and affiliation metadata approved by the owner.
- [ ] AI-assistance disclosure reviewed and accurate.
- [ ] Protocol freezes and approvals recorded in the decision log.
- [ ] Every experiment report read; status labels correct (confirmatory, exploratory, failed, null).
- [ ] Limitations and claims boundary accepted.
- [ ] Licence statement (D-001) correct in README, CITATION.cff and manuscript.
- [ ] Publication decision (G-PUBLIC) taken by the owner.

No box above was ticked by an agent at any milestone up to M6, so none was unticked. Only the owner ticks these boxes.

## Prepared for the owner (M6, 2026-11-25)

What to read for each box:

1. Authorship and affiliation: `research/paper/manuscript.md` (author line under the title, and section 11), `CITATION.cff` (`authors`), `articles/medium.md` line 6 (byline, filled on 2026-11-26).
2. AI-assistance disclosure: manuscript section 11; `CITATION.cff` (`message`); `research/publication/reproducibility_report.md` for what was verified and how.
3. Protocol freezes and approvals: `research/decision_log.md` D-012 (freeze), D-015, D-017, D-018, D-019 and the M6 entry D-020; `research/freeze.json`.
4. Experiment reports and status labels: `research/experiments/EXP-001/report.pdf` to `EXP-004/report.pdf` (or their `report.md`); `research/experiment_registry.csv` (EXP-005 "registered, not frozen").
5. Limitations and claims boundary: manuscript sections 7 and 8; `research/limitations.md`; `research/publication/evidence_audit.md` sections 4 and 6.
6. Licence statement: README "Licence"; `CITATION.cff` (first comment lines); manuscript section 10; `research/publication/dependency_licences.md` for third-party terms.
7. Publication decision: `research/publication/release_checklist.md`; `research/publication/reproducibility_report.md`; the PDFs `research/paper/manuscript.pdf` and `research/paper/supplementary.pdf`.

Open decisions for this repository, each the owner's alone:

- Whether and when to release anything further (release, tag, preprint, articles) (G-PUBLIC). Correction (2026-11-26): the repository is public at https://github.com/mohamedbechirkefi/pulse-feed-ranking since 2026-11-25, pushed by the coordinator on the owner's word; no tag, release, DOI or preprint exists.
- Whether to freeze EXP-005, and with which values for OPEN-1 (like-rate levels), OPEN-2 (levels for the dependence contrast), OPEN-3 (its threshold and Holm family), OPEN-4 (tau 0.3 block), OPEN-5 (MMR arm) and OPEN-6 (compute cap); until then it stays registered, not frozen and not run (G-FREEZE).
- The public repository and demo address, the Medium byline, the version and date policy, the `CITATION.cff` title, the Steck (2018) source label, the M2 smoke report, the remaining local paths, funding, competing interests and the author line: answered by the owner on 2026-11-26 (see "Owner answers recorded (2026-11-26)" below).

Remaining owner placeholders (file and line): none. The eight placeholders listed at M6 (README, demo README, demo footer, manuscript section 10, the Medium byline and links, the LinkedIn links) were filled on 2026-11-26 from the owner's answers B1 to B3.

## Owner answers recorded (2026-11-26)

Source: owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md` and `labs/_shared/owner-approvals-2026-11-26.md`, outside this repository). Applied in decision D-021. No box above was ticked; only the owner ticks them.

Answers that concern this repository and what was done:

- **A1 (out-of-date statements):** the repository is public since 2026-11-25. The "nothing has been published / nothing has left this machine / nothing has been pushed" sentences in the README, this file and `release_checklist.md` were corrected. Append-only records (`progress.md`, `research/decision_log.md`, `research/experiment_journal.jsonl`) stay as written for their dates.
- **B1 (repository URL):** https://github.com/mohamedbechirkefi/pulse-feed-ranking in the README, `demo/README.md`, the demo footer, manuscript section 10, both articles and `CITATION.cff` (`repository-code`).
- **B2 (demo URL):** https://pulse-feed-ranking.kefimohamedbechir.workers.dev; `demo/wrangler.jsonc` added (assets only, folder `./dist`); `demo/README.md` states that the page is hosted as Cloudflare Workers static assets on the free plan and deployed by the coordinator. The built page makes no request to another origin (A11Y-CHECK).
- **B3 (author line):** "Mohamed Bechir Kefi, independent researcher" in the manuscript, supplementary, the four experiment reports, the README, the Medium byline and the demo footer; `CITATION.cff` `affiliation: "Independent researcher"`. `pyproject.toml` already names the author. The frozen protocols are not edited.
- **B4:** "No funding was received." and "The author declares no competing interests." in manuscript section 11.
- **B5:** not applicable to PULSE (its AI-use statement was already approved, D-017).
- **B6, B7 (titles):** the manuscript title was already approved (D-017) and `CITATION.cff` `title` already equals it; no change.
- **B8:** `0.2.0-rc1` kept, no `date-released`; the release step is recorded in `release_checklist.md`.
- **B9 (home paths):** no editable file contains a home path; the ten remaining files are frozen, raw or append-only (`reproducibility_report.md` section 7).
- **B10:** committed PDFs kept. **B11:** no PULSE figure listed. **B13:** build-tool sentence added to the release notes draft.
- **B14:** source labels accepted, including Steck (2018) checked through a secondary source only.
- **R-PULSE-1:** EXP-005 stays registered, not frozen, not run; the owner will freeze it later with values for OPEN-1 to OPEN-6 (G-FREEZE).
- **R-PULSE-2:** the committed M2 exploratory smoke report is kept as a historical record.

Still open (owner only): B15 (read and approve the article drafts before any posting), B16 (full-text review of the manuscript and reports, then sign-off of this checklist), B18 (release, tag, optional DOI or preprint), and the EXP-005 freeze (G-FREEZE).
