<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Release checklist (release candidate prepared; publication is owner-controlled)

**Status (2026-11-25, M6).** Release candidate prepared and awaiting the owner's review and the G-PUBLIC decision. Correction (2026-11-26, owner's answer A1): the repository was pushed by the coordinator on the owner's word and is public at https://github.com/mohamedbechirkefi/pulse-feed-ranking since 2026-11-25; no tag, release, DOI or preprint exists, and the article drafts are unpublished. The demo is to be hosted at https://pulse-feed-ranking.kefimohamedbechir.workers.dev (owner's answer B2). A box is ticked only for what was verified in the M6 session, with its evidence; the two owner items stay open.

- [ ] All registered experiments have truthful standalone reports and PDFs built and inspected.
  Not ticked: EXP-001 to EXP-004 have reports and PDFs, built by `scripts/build_pdfs.py` and inspected (first page and every figure page; `reproducibility_report.md` section 3). EXP-005 is registered, not frozen and not run, so it has a protocol draft and no report; under 11.3 its report is due when it is run or abandoned, which depends on the owner's freeze decision.
- [x] Manuscript complete; PDF built locally (pandoc to Typst) and inspected page by page.
  Evidence: `research/paper/manuscript.pdf`, 10 pages, every page inspected; `manuscript.tex` generated; the owner-only public address placeholder (section 10) was filled on 2026-11-26 (owner's answer B1) and the PDF rebuilt and inspected.
- [x] `artifact_manifest.json` complete; claims audit passed.
  Evidence: 42 artifacts, 47 paths resolve, 28 of 28 recorded hashes match; `scripts/m4_evidence_audit.py` exit 0 with 1,260 raw files matching, 0 row-wise and 0 Part D errors (`reproducibility_report.md` section 4).
- [x] Reproducibility report completed from a clean clone.
  Evidence: `reproducibility_report.md` sections 1 and 6 (two clean clones; tests, smoke comparison, analysis regeneration, demo build and checker, export determinism).
- [x] README updated with verified findings only; citation section present.
  Evidence: `tests/test_release_checks.py::test_public_text_numbers_come_from_the_paper_or_reports` (0 numbers missing); README "Citation" section and `CITATION.cff`.
- [x] Demo works offline after load, keyboard usable, reduced motion, mobile layout.
  Evidence: `node tools/a11y_check.mjs dist` in the clean clone printed "A11Y-CHECK PASS" (keyboard 24 of 24 and 12 of 12, reduced motion 0 running animations, 0 px overflow at 360 px, offline after first load).
- [x] Articles (Medium, LinkedIn) consistent with verified results; placeholders for unpublished links.
  Evidence: the same number test for `articles/*.md` (0 missing). The byline and link placeholders were filled on 2026-11-26 (owner's answers B1 to B3); publication of the articles stays the owner's decision (B15).
- [ ] No e-mail, personal identifier or secret in tracked files.
  Not ticked: 0 e-mail addresses, 0 secrets or keys and 0 `.env` files in tracked files, but the local home path (which contains the local user name) remains in 10 tracked files that are frozen, raw or append-only (3 frozen protocols, 6 execution logs, `progress.md`); the owner decides whether they are acceptable (`reproducibility_report.md` section 5).
- [ ] Owner sign-off of `author_review.md` (owner only).
- [ ] Owner approval for any push, remote, release or preprint recorded (owner only, G-PUBLIC).

## Version and date at the release (owner's answer B8, 2026-11-26)

`CITATION.cff` keeps `version: 0.2.0-rc1` and no `date-released` until the release. At the release the version becomes `0.2.0` and `date-released` is set to the release day. `pyproject.toml` keeps its current version (`0.1.0`, unchanged since M0), because changing it would change the lockfile and the recorded environments.

## Release notes (draft)

- Figures: no PULSE figure is listed among those kept with small or clipped labels (owner's answer B11), so no figure note is needed.
- Build and check tools: external build and check tools are used but not redistributed: pandoc (GPL-2.0-or-later) for Markdown conversion, Google Chrome for the local accessibility check, the fonts embedded in the PDFs by Typst (SIL OFL 1.1 and the Bitstream Vera derived licence), the GCC runtime that some numpy wheels bundle (not present in the recorded macOS install) and MPL-2.0 lightningcss in the demo toolchain, as listed in `dependency_licences.md` (owner's answer B13).
- Sources: Steck (2018) was checked through a secondary source only; the label stated in the manuscript was accepted by the owner (B14).
- Hosting: the demo is a static page served as Cloudflare Workers static assets on the free plan (`demo/wrangler.jsonc`), deployed by the coordinator.
