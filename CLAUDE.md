<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# PULSE: how every session works

PULSE studies, in simulation only, how ranking objectives influence exposure diversity and simulated preference reinforcement. `master_prompt.md` is the authority. Never edit it.

## 1. Reading order (before modifying anything)

1. `master_prompt.md` (entire file).
2. `roadmap.md` (milestones, status, blockers).
3. `progress.md` (append-only journal; read the latest entry and its "next action").
4. `research/protocol.md` (protocol status: DRAFT until the owner freezes it).
5. `research/claims_register.csv` (no claim exists without a row).

Then run `git status` and inspect existing files. Do not overwrite owner changes. State the current milestone and the next bounded task before working.

## 2. Mandatory requirements (master prompt section 11, all sessions)

- **Publication tree (11.1).** Maintain `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical, manuscript.tex generated, references.bib, figures/, supplementary.md), `research/experiments/EXP-NNN/` (protocol.md, report.md, config.json, run_manifest.json, metrics.csv, figures/, reproduction.md) and `research/publication/` (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md).
- **Stable identifiers.** EXP-NNN for experiments, RUN ids inside experiments, FIG ids, CLM ids. A seed is a run, not an experiment. A new question or materially different protocol gets a new EXP id.
- **Before each experiment (11.2).** A complete `EXP-NNN/protocol.md`, registered in the registry, frozen with a version and hash, with recorded owner approval, before any confirmatory run. Post-hoc changes are exploratory, dated and justified.
- **Every registered experiment gets a standalone report (11.3)** with the 12-part structure, including failed, null, abandoned and exploratory experiments, each visibly labelled.
- **One integrated manuscript (11.4)**, Markdown canonical, LaTeX and PDF generated locally with free tooling. No placeholder results; no claimed PDF that was not built and inspected.
- **Evidence pipeline (11.5).** Tables and figures are generated once from versioned results and reused everywhere. Every quantitative claim maps to experiment id, run ids, metric definition, result path, generator script, config or protocol hash and code revision. A second review pass challenges the preferred hypothesis.
- **Milestone additions (11.6).** M0/M1: registry, manuscript skeleton, experiment protocols, zero-cost toolchain confirmed, freeze before execution. M2: versioned output schemas, run manifests and report generators alongside the core. M3: reports written as experiments finish; failures and deviations recorded at once. M4: finished reports, evidence audit, synthesis including contradictory results and sensitivity. M5: demo, paper, reports and articles use identical verified results. M6: compile and inspect PDFs, verify references and links, clean-clone smoke reproduction, owner review checklist.
- **Release package (11.7)** is prepared but never released without the owner.

## 3. Toolchain (zero-cost, decision D-002)

- Python 3.12 via uv: `/Users/bechir/research/labs/.tools/py/bin/uv sync`, `uv run pytest`.
- Lockfile: `uv.lock` (resolution limited by `exclude-newer` in `pyproject.toml`).
- PDFs: pandoc (`/Users/bechir/research/labs/.tools/pandoc`) converts Markdown to Typst; the `typst` Python package (in `/Users/bechir/research/labs/.tools/py/`) compiles it. `manuscript.tex` is generated from Markdown by pandoc. No TeX distribution is installed or required.
- Node 22 at `/Users/bechir/research/helix/.tools/node/bin` is read-only for this project (M5 demo only). Never modify that folder.

## 4. Rules

- **Gates.** Never push, add a remote, create a GitHub repository or publish anything (G-PUBLIC). No paid service of any kind. Never freeze a protocol: freezing belongs to the owner (G-FREEZE). Confirmatory experiments run only after the owner freezes the protocol; anything else is labelled exploratory.
- **Scope.** Work only inside this repository, except read-only use of the tools listed above. Do not touch any other folder under `/Users/bechir/research`. Never kill processes you did not start. Never delete anything you did not create in the current session.
- **Truthfulness.** Never fabricate results, citations, test counts or PDFs. Record commands and their actual outputs. Unverified means labelled unverified. Never mark incomplete work done.
- **Files and style.** New text and code files start with `SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0` as a comment where the format allows; JSON and CSV are covered by `NOTICE.md`. English. No em dashes. Plain, formal register. No e-mail address, personal identifier or secret in any committed file (git author metadata excepted). Refer to the owner as "the owner" (they/them).
- **Licence.** The licence files are the owner's decision (D-001). Do not change them. Development commands may be appended to CONTRIBUTING.md.
- **Claims boundary (master prompt section 10).** Do not claim that any real platform uses these algorithms. Do not measure or claim addiction or real human behaviour. Simulated agents are not participants. No engagement-maximising deployment, no data collection.
- **Commits.** Local only: `git -c user.name=mohamedbechirkefi -c user.email=<owner address given in the session brief, never written in the repository> commit`, message ending with a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Run `git status` before and after.
- **Session end.** Append a dated entry to `progress.md` (commands, real outputs, failures, changed files, risks, next action) and update `roadmap.md`.
