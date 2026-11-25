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

1. Authorship and affiliation: `research/paper/manuscript.md` (author line under the title, and section 11), `CITATION.cff` (`authors`), `articles/medium.md` line 6 (byline placeholder).
2. AI-assistance disclosure: manuscript section 11; `CITATION.cff` (`message`); `research/publication/reproducibility_report.md` for what was verified and how.
3. Protocol freezes and approvals: `research/decision_log.md` D-012 (freeze), D-015, D-017, D-018, D-019 and the M6 entry D-020; `research/freeze.json`.
4. Experiment reports and status labels: `research/experiments/EXP-001/report.pdf` to `EXP-004/report.pdf` (or their `report.md`); `research/experiment_registry.csv` (EXP-005 "registered, not frozen").
5. Limitations and claims boundary: manuscript sections 7 and 8; `research/limitations.md`; `research/publication/evidence_audit.md` sections 4 and 6.
6. Licence statement: README "Licence"; `CITATION.cff` (first comment lines); manuscript section 10; `research/publication/dependency_licences.md` for third-party terms.
7. Publication decision: `research/publication/release_checklist.md`; `research/publication/reproducibility_report.md`; the PDFs `research/paper/manuscript.pdf` and `research/paper/supplementary.pdf`.

Open decisions for this repository, each the owner's alone:

- Whether and when to publish anything (push, public repository, release, preprint, articles); nothing has left this machine (G-PUBLIC).
- Whether to freeze EXP-005, and with which values for OPEN-1 (like-rate levels), OPEN-2 (levels for the dependence contrast), OPEN-3 (its threshold and Holm family), OPEN-4 (tau 0.3 block), OPEN-5 (MMR arm) and OPEN-6 (compute cap); until then it stays registered, not frozen and not run (G-FREEZE).
- The public repository and demo address, which replaces every "[to be added by the owner on release]" placeholder listed below.
- The byline of the Medium article draft.
- Re-adding `date-released` to `CITATION.cff` on the day of a release; it was removed at M6 because nothing has been released.
- Whether to keep the release-candidate version `0.2.0-rc1` and the `CITATION.cff` title, which now equals the manuscript title, or to choose others.
- Whether the miscalibration formula may stay checked only against a secondary source, or whether the owner wants to obtain Steck (2018) through a legal channel before publication.
- Whether the committed exploratory smoke report from M2 should stay as a historical record (current choice) or be regenerated with the current code (finding R-1 of the reproducibility report).
- Whether the remaining local paths in the three frozen protocols, six execution logs and `progress.md` are acceptable in a public repository, since editing them would touch frozen or raw files.
- Funding, competing interests and the author line are already owner-approved (D-012 C3, D-017); the owner may still confirm them at sign-off.

Remaining owner placeholders (file and line):

- `README.md` line 80: "Repository and demo address: [to be added by the owner on release]."
- `demo/README.md` line 23: same placeholder.
- `demo/src/App.tsx` line 65: same placeholder, shown on the demo page.
- `research/paper/manuscript.md` line 248: "public URL: [to be added by the owner on release]".
- `articles/medium.md` line 6: "[author line to be added by the owner]".
- `articles/medium.md` line 50: "[repository link to be added by the owner on release]".
- `articles/linkedin.md` line 12: "[repository link to be added by the owner on release]".
- `articles/linkedin.md` line 13: "[demo link to be added by the owner on release]".
