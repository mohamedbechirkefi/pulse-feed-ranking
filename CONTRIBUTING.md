<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Contributing to PULSE

PULSE is an independent, source-available research project maintained by Mohamed Bechir Kefi: recommendation feedback and attention.

Technical suggestions, bug reports, reproducibility results, corrections and Pull Requests are welcome. The project is available for non-commercial research under the PULSE Source-Available Non-Commercial Research License v1.0 ([LICENSE](LICENSE)); it is not OSI-approved open-source software.

## 1. Before you start

For major changes, open an Issue first. Read `master_prompt.md`, `research/protocol.md` and `research/claims_register.csv`: frozen protocols are never changed silently, and every reported number must trace to a result file.

## 2. Pull Request requirements

- Your contribution is original or appropriately licensed, and you have the right to submit it.
- No credentials, secrets, confidential information or personal data.
- Relevant tests are included and pass; you report what you actually ran.
- Third-party dependencies and data sources are identified with their licenses.
- New files carry the header `SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0` where the format allows.
- You accept the Contributor License Agreement before your contribution is merged.

## 3. Contributor License Agreement

A recorded acceptance of [CLA.md](CLA.md) is required before merging copyrightable contributions. When you open a Pull Request, the "CLA Assistant" check comments on it; read the CLA, then post this exact comment:

    I have read the PULSE CLA v1.0 and I hereby sign it

The check records your public GitHub username and account ID, the date and the PR. You sign once. If the check does not update, comment `recheck`. Checking a box is not a signature; the comment is.

The CLA lets the maintainer use, modify, distribute, relicense and commercially exploit accepted contributions. You keep the copyright in your original contributions.

## 4. Governance

Mohamed Bechir Kefi is the project owner and lead maintainer, and the only person who can change the protected `main` branch. The maintainer decides the research direction, protocol freezes, claims, releases and licensing.

## 5. Privacy and disclosure

Never commit an e-mail address, a name or any other personal identifier in code, logs, fixtures or results. Report security issues privately through GitHub's private vulnerability reporting.

## 6. Development commands

    uv sync --frozen --all-groups --all-extras   # install locked dependencies (uv 0.9 or later)
    uv run pytest -q                             # run the test suite

Experiment and report commands (M2). The package is not installed; set `PYTHONPATH=src`:

    PYTHONPATH=src uv run python -m pulse.cli smoke                              # exploratory smoke matrix
    PYTHONPATH=src uv run python -m pulse.cli run --config experiments/exploratory/var-probe.json
    PYTHONPATH=src uv run python -m pulse.cli run --experiment EXP-001           # refused until the owner freezes the protocol
    PYTHONPATH=src uv run python -m pulse.cli report --results results/exploratory/smoke
    PYTHONPATH=src uv run python -m pulse.cli test

Demo (M5). Node 22 is required (the maintainer's local copy is read-only); dependencies are pinned in `demo/package-lock.json`:

    .venv/bin/python scripts/export_demo_data.py                     # demo/public/data/results.json from committed results
    PYTHONPATH=src .venv/bin/python scripts/export_sandbox_fixture.py   # engine parity fixture for the sandbox
    cd demo && npm ci && npm test && npm run build && npm run preview
    node tools/a11y_check.mjs dist --screenshots <dir>                # offline and accessibility check

Release candidate (M6). pandoc and the `typst` Python package are needed for the PDFs (`PULSE_PANDOC` and `PULSE_TYPST_PYTHON` override their locations):

    PYTHONPATH=src .venv/bin/python scripts/build_pdfs.py [--png <dir>]   # manuscript, supplementary and report PDFs, manuscript.tex
    .venv/bin/python scripts/check_links.py                              # every relative Markdown link and anchor
