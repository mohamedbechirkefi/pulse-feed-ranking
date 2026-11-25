# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Check every relative Markdown link and image in the tracked Markdown files (M6).

A link resolves when its target file exists relative to the linking file and, if it carries an
anchor, the target (or the same file) has a heading whose GitHub-style slug equals the anchor.
External links (http, https, mailto) are listed but not fetched. Prints LINK-CHECK PASS or the
broken links and exits 1.

    .venv/bin/python scripts/check_links.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^(```|~~~)")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")


def markdown_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.splitlines() if "node_modules/" not in p]


def _body_lines(text: str) -> list[str]:
    """Lines outside fenced code blocks, with inline code removed."""
    lines, fenced = [], False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            fenced = not fenced
            continue
        if not fenced:
            lines.append(re.sub(r"`[^`]*`", "", line))
    return lines


def slug(heading: str) -> str:
    s = re.sub(r"[*_`]|<[^>]+>", "", heading).strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    out = set()
    for line in _body_lines(path.read_text(encoding="utf-8")):
        m = HEADING.match(line)
        if m:
            base = slug(m.group(1))
            n = seen.get(base, 0)
            seen[base] = n + 1
            out.add(base if n == 0 else f"{base}-{n}")
    return out


def check(files: list[Path] | None = None) -> tuple[int, int, list[str]]:
    """Return (relative links checked, external links seen, broken-link messages)."""
    files = files if files is not None else markdown_files()
    n_rel = n_ext = 0
    broken: list[str] = []
    for f in files:
        for lineno, line in enumerate(_body_lines(f.read_text(encoding="utf-8")), 1):
            for target in LINK.findall(line):
                if re.match(r"^(https?:|mailto:)", target):
                    n_ext += 1
                    continue
                n_rel += 1
                path_part, _, anchor = target.partition("#")
                dest = (f.parent / path_part).resolve() if path_part else f
                rel = f.relative_to(ROOT)
                if not dest.exists():
                    broken.append(f"{rel}: missing target {target}")
                elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                    broken.append(f"{rel}: missing anchor {target}")
    return n_rel, n_ext, broken


def main() -> int:
    files = markdown_files()
    n_rel, n_ext, broken = check(files)
    print(f"{len(files)} Markdown files, {n_rel} relative links checked, {n_ext} external links not fetched")
    for b in broken:
        print("BROKEN", b)
    print("LINK-CHECK PASS" if not broken else f"LINK-CHECK FAIL ({len(broken)})")
    return 0 if not broken else 1


if __name__ == "__main__":
    raise SystemExit(main())
