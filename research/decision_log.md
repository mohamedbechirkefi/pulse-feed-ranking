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
