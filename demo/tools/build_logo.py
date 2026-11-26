# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
# Usage (needs fontTools and brotli): python3 -I tools/build_logo.py node_modules/@fontsource-variable/unbounded/files/unbounded-latin-wght-normal.woff2 public/brand
import re
# Builds the PULSE mark and lockup SVGs. Wordmark outlined from Unbounded (OFL) at wght 640.
import sys, os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
font_path, out = sys.argv[1], sys.argv[2]
f = TTFont(font_path)
f = instantiateVariableFont(f, {"wght": 640})
gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f["head"].unitsPerEm
cap = f["OS/2"].sCapHeight
TOPIC_A, TOPIC_B, TOPIC_C, TOPIC_D, TOPIC_E = "#7CC0FF", "#F2C14E", "#6FD3A8", "#C79BFF", "#FF7466"
def rr(x, y, w, h, r):
    return f"M{x+r} {y}H{x+w-r}A{r} {r} 0 0 1 {x+w-r} {y+h}H{x+r}A{r} {r} 0 0 1 {x+r} {y}Z"
# rows on a 256 grid: three segments, two, one (many topics narrowing to one)
H, R = 48, 24
rows = [
  [(24, 40, 56), (100, 40, 56), (176, 40, 56)],
  [(24, 104, 94), (138, 104, 94)],
  [(24, 168, 208)],
]
cols = [[TOPIC_A, TOPIC_B, TOPIC_E], [TOPIC_A, TOPIC_E], [TOPIC_E]]
def mark_paths(colour=None, dx=0):
    out = []
    for ri, row in enumerate(rows):
        for ci, (x, y, w) in enumerate(row):
            c = colour or cols[ri][ci]
            out.append(f'<path fill="{c}" d="{rr(x+dx, y, w, H, R)}"/>')
    return "\n  ".join(out)
def word(colour, x0, baseline, height):
    s = height / cap; pen_x = 0; parts = []
    for ch in "Pulse":
        g = cmap[ord(ch)]
        sp = SVGPathPen(gs)
        tp = TransformPen(sp, (s, 0, 0, -s, x0 + pen_x * s, baseline))
        gs[g].draw(tp)
        parts.append(re.sub(r"-?\d+\.\d+", lambda m: ("%g" % round(float(m.group()), 1)), sp.getCommands()))
        pen_x += gs[g].width - 18  # slight tightening
    return f'<path fill="{colour}" d="{" ".join(parts)}"/>', x0 + pen_x * s
def svg(w, h, body, title):
    return f'<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{title}"><title>{title}</title>\n  {body}\n</svg>\n'
os.makedirs(out, exist_ok=True)
W = lambda n, s: open(os.path.join(out, n), "w").write(s)
W("pulse-mark.svg", svg(256, 256, mark_paths(), "Pulse"))
W("pulse-mark-mono.svg", svg(256, 256, mark_paths("#0F1B2A"), "Pulse"))
W("pulse-mark-on-dark.svg", svg(256, 256, mark_paths("#E9EEF2"), "Pulse"))
# favicon: mark on a gallery tile
tile = '<path fill="#0F1B2A" d="M56 0H200A56 56 0 0 1 256 56V200A56 56 0 0 1 200 256H56A56 56 0 0 1 0 200V56A56 56 0 0 1 56 0Z"/>'
small_rows = mark_paths()
W("favicon.svg", svg(256, 256, tile + "\n  " + small_rows, "Pulse"))
# lockup, height 256: mark then wordmark with cap height 132 aligned to mark rows
for name, mc, wc in [("pulse-lockup.svg", None, "#E9EEF2"), ("pulse-lockup-light.svg", None, "#0F1B2A"), ("pulse-lockup-mono.svg", "#0F1B2A", "#0F1B2A"), ("pulse-lockup-on-dark.svg", "#E9EEF2", "#E9EEF2")]:
    wp, end = word(wc, 284, 216, 176)
    W(name, svg(int(end) + 24, 256, mark_paths(mc) + "\n  " + wp, "Pulse"))
print("ok", cap, upm)
