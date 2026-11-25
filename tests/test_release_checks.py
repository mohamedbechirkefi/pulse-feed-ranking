# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Release-candidate checks (M6): links, numbers outside the manuscript, citations, CITATION.cff, PDFs."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "research/paper/manuscript.md"
NUM = re.compile(r"(?<![\w./])-?\d[\d,]*\.\d+(?![\d])")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_relative_markdown_link_resolves():
    n_rel, _, broken = _load("check_links").check()
    assert n_rel > 0
    assert broken == []


def test_link_checker_detects_a_broken_link(tmp_path):
    f = tmp_path / "x.md"
    f.write_text("# Title\n\n[ok](#title) [bad](missing.md) [bad anchor](#nope)\n", encoding="utf-8")
    mod = _load("check_links")
    old_root = mod.ROOT
    mod.ROOT = tmp_path
    try:
        _, _, broken = mod.check([f])
    finally:
        mod.ROOT = old_root
    assert len(broken) == 2


def _numbers(path: Path) -> set[str]:
    return {t.lstrip("-+") for t in NUM.findall(path.read_text(encoding="utf-8"))}


@pytest.mark.parametrize("rel", ["README.md", "articles/medium.md", "articles/linkedin.md", "articles/README.md", "demo/README.md"])
def test_public_text_numbers_come_from_the_paper_or_reports(rel):
    """Every decimal number in the README and articles is printed in the manuscript, supplementary or a report."""
    sources = set().union(_numbers(MS), _numbers(ROOT / "research/paper/supplementary.md"),
                          *(_numbers(p) for p in sorted(ROOT.glob("research/experiments/EXP-00*/report.md"))))
    missing = sorted(_numbers(ROOT / rel) - sources)
    assert missing == []


def test_every_bib_entry_is_cited_and_every_reference_has_an_entry():
    bib = (ROOT / "research/paper/references.bib").read_text(encoding="utf-8")
    keys = re.findall(r"@\w+\{(\w+),", bib)
    text = MS.read_text(encoding="utf-8")
    refs = text.split("## References", 1)[1].split("## Supplementary appendix", 1)[0]
    ref_lines = [ln for ln in refs.splitlines() if ln.startswith("- ")]
    assert len(keys) == len(ref_lines) == len(set(keys))
    for key in keys:
        surname = re.match(r"[a-z]+", key).group(0)
        year = re.search(r"\d{4}", key).group(0)
        body = text.split("## References", 1)[0].lower().replace(" ", "")
        assert surname in body and year in body, key
        assert any(ln.lower().replace(" ", "").startswith(f"-{surname}") and f"({year})" in ln for ln in ref_lines), key


def test_citation_cff_release_candidate():
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    for key in ("cff-version: 1.2.0", "message:", "title:", "authors:", "type: software", "version:"):
        assert key in cff
    assert "date-released" not in cff
    assert re.search(r"^version: \d+\.\d+\.\d+-rc\d+$", cff, re.M)
    title = re.search(r'^title: "(.*)"$', cff, re.M).group(1)
    h1 = re.search(r"^# (.*)$", MS.read_text(encoding="utf-8"), re.M).group(1)
    assert title == h1
    assert "@" not in cff


PDFS = ["research/paper/manuscript.pdf", "research/paper/supplementary.pdf",
        *[f"research/experiments/EXP-00{n}/report.pdf" for n in (1, 2, 3, 4)]]


@pytest.mark.parametrize("rel", PDFS)
def test_pdf_present_small_and_clean(rel):
    pdf = ROOT / rel
    assert pdf.exists()
    data = pdf.read_bytes()
    assert data.startswith(b"%PDF") and len(data) < 5 * 1024 * 1024
    assert b"/Title" in data
    assert b"/Users/" not in data and not re.search(rb"[\w.+-]+@[\w-]+\.[a-z]{2,}", data)


def test_run_manifests_record_repo_relative_paths():
    """F-7 (M6): provenance records the result directory relative to the repository, no local home path."""
    import json

    for n in (1, 2, 3, 4):
        man = json.loads((ROOT / f"research/experiments/EXP-00{n}/run_manifest.json").read_text(encoding="utf-8"))
        assert man["results_dir"] == f"results/raw/EXP-00{n}"
    from pulse.analysis import _repo_relative

    assert _repo_relative(ROOT / "results" / "raw" / "EXP-001") == "results/raw/EXP-001"
    assert _repo_relative(Path("/elsewhere/x")) == "/elsewhere/x"
