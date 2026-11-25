<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Compiled from installed metadata, not from memory: Python from the `.venv` created by `uv sync --frozen --all-groups --all-extras` (distribution metadata, `importlib.metadata`), npm from `demo/package-lock.json` and each installed `demo/node_modules/*/package.json`. Accepted without a flag: MIT, BSD, ISC, Apache-2.0, PSF, MPL-2.0, 0BSD, Zlib and similarly permissive licences. Nothing here is a legal opinion; the licence of the project itself is the owner's decision (D-001) and is not discussed.

## Python (6 distributions)

| Package | Version | Role | Licence (metadata) | Flag |
| --- | --- | --- | --- | --- |
| numpy | 2.3.5 | runtime | BSD-3-Clause (classifier "BSD License"); bundled components listed below | see note 1 |
| pytest | 8.4.2 | test | MIT | none |
| pluggy | 1.7.0 | test | MIT | none |
| iniconfig | 2.3.1 | test | MIT | none |
| packaging | 26.3 | test | Apache-2.0 OR BSD-2-Clause | none |
| Pygments | 2.21.0 | test | BSD-2-Clause | none |

Note 1. The numpy `LICENSE.txt` lists bundled components: lapack-lite (BSD-3-Clause), dragon4 (MIT), libdivide (Zlib), vendored Meson (Apache-2.0), spin (BSD-3-Clause), tempita (MIT), OpenBLAS and LAPACK (BSD-3-Clause variants), the GCC runtime library (GPL-3.0-or-later WITH GCC-exception-3.1) and libquadmath (LGPL-2.1-or-later). The last two ship only in wheels that carry `numpy/.dylibs` or `numpy.libs`; the installed macOS arm64 wheel has no `numpy/.dylibs` folder, so they are not present here. On platforms whose wheel bundles them, they are dynamically linked runtime libraries under the GCC runtime exception and the LGPL. PULSE does not redistribute numpy. Informational flag for the owner, no action needed for a source release.

## npm (demo; 84 lock entries, 53 installed on this machine)

Runtime (bundled into `demo/dist`): react 19.3.1 (MIT), react-dom 19.3.1 (MIT), scheduler 0.28.0 (MIT). No flag.

Build and test only (not shipped in `dist`):

| Licence | Packages |
| --- | --- |
| MIT | @jridgewell/sourcemap-codec 1.6.0, @oxc-project/types 0.156.0, @rolldown/binding-* 1.2.19 (darwin-arm64 installed; other platforms optional, not installed), @rolldown/pluginutils 1.1.1, @standard-schema/spec 1.1.0, @types/chai 5.2.3, @types/deep-eql 4.0.2, @types/estree 1.0.11, @types/react 19.3.0, @types/react-dom 19.3.0, @vitejs/plugin-react 6.1.2, @vitest/expect, mocker, pretty-format, runner, snapshot, spy and utils 4.1.12, assertion-error 2.0.1, chai 6.3.0, convert-source-map 2.0.0, csstype 3.2.4, es-module-lexer 2.3.2, estree-walker 3.0.3, fdir 6.5.0, fsevents 2.3.3, magic-string 0.30.21, nanoid 3.3.20, obug 2.2.1, pathe 2.0.3, picomatch 4.0.7, postcss 8.5.33, rolldown 1.2.19, stackback 0.0.2, std-env 4.3.0, tinybench 2.9.0, tinyexec 1.4.0, tinyglobby 0.2.17, tinyrainbow 3.2.0, vite 8.3.5, vitest 4.1.12, why-is-node-running 2.3.0; optional, not installed: @emnapi/core, @emnapi/runtime, @emnapi/wasi-threads, @napi-rs/wasm-runtime, @tybys/wasm-util |
| Apache-2.0 | detect-libc 2.1.2, expect-type 1.4.0, typescript 5.9.3 |
| MPL-2.0 | lightningcss 1.33.0 and lightningcss-darwin-arm64 1.33.0 (other platform binaries optional, not installed) |
| ISC | picocolors 1.1.1, siginfo 2.0.0 |
| BSD-3-Clause | source-map-js 1.2.4 |
| 0BSD | tslib 2.9.1 (optional, not installed) |

No npm package is flagged.

## Tools used to build, not distributed

| Tool | Use | Licence | Flag |
| --- | --- | --- | --- |
| pandoc 3.6.3 | Markdown to Typst and LaTeX | GPL-2.0-or-later | informational: a build tool only; its output documents are not covered by its licence, and it is not shipped |
| typst (Python package 0.15.0) | PDF compilation | Apache-2.0 | none |
| Libertinus Serif and DejaVu Sans Mono (embedded in the PDFs by Typst) | fonts | SIL OFL 1.1 and the Bitstream Vera derived licence | none: both permit embedding in documents |
| uv 0.9.5 | locked install | Apache-2.0 OR MIT | none |
| Node 22.23.3 | demo build | MIT (with bundled third-party notices) | none |
| Google Chrome (local install) | headless browser for `demo/tools/a11y_check.mjs` | proprietary freeware | informational: an optional local test tool, not a dependency and not shipped; any Chromium build can be used through the `CHROME` variable |

## Data

MovieLens 1M is not a software dependency; its terms (research use, no redistribution, acknowledgement) are recorded in `data/manifest.json` and respected: no row-level data is committed.
