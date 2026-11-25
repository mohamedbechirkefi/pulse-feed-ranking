// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
// Hand-written SVG and HTML charts. Every chart has a plain-language caption; no value is shown only
// on hover. Published charts read the validated results file; sandbox charts read sandbox output.
import type { Estimate, Heatmap, LikeRateCurve } from "./results";

export const TOPIC_NAMES = Array.from({ length: 10 }, (_, z) => `Topic ${z + 1}`);

/** Shared axis for the interval glyphs of one experiment table: covers every interval and zero. */
export function axisFor(es: Estimate[]): [number, number] {
  let lo = 0;
  let hi = 0;
  for (const e of es) {
    lo = Math.min(lo, e.ci_low ?? e.estimate, e.estimate);
    hi = Math.max(hi, e.ci_high ?? e.estimate, e.estimate);
  }
  const pad = (hi - lo) * 0.06 || 0.05;
  return [lo - pad, hi + pad];
}

/** Interval glyph for one estimate on a shared axis, with the zero line. Decorative: the numbers are in the row. */
export function IntervalGlyph({ e, axis }: { e: Estimate; axis: [number, number] }) {
  const W = 160;
  const H = 18;
  const x = (v: number) => ((v - axis[0]) / (axis[1] - axis[0])) * W;
  const lo = e.ci_low ?? e.estimate;
  const hi = e.ci_high ?? e.estimate;
  return (
    <svg className="glyph" width={W} height={H} viewBox={`0 0 ${W} ${H}`} aria-hidden="true" focusable="false">
      <line x1={x(0)} x2={x(0)} y1={1} y2={H - 1} className="zero" />
      <line x1={x(lo)} x2={x(hi)} y1={H / 2} y2={H / 2} className="ci" />
      <line x1={x(lo)} x2={x(lo)} y1={H / 2 - 4} y2={H / 2 + 4} className="ci" />
      <line x1={x(hi)} x2={x(hi)} y1={H / 2 - 4} y2={H / 2 + 4} className="ci" />
      <circle cx={x(e.estimate)} cy={H / 2} r={3.2} className="pt" />
    </svg>
  );
}

const BINS = [0.6, 0.7, 0.8, 0.9, 0.95];
/** Darker cell = lower entropy = more concentrated exposure. */
function level(v: number): number {
  let l = 5;
  for (const b of BINS) if (v >= b) l -= 1;
  return l;
}

export function MeasuredHeatmap({ h }: { h: Heatmap }) {
  const val = (arm: string, cell: string) => h.values.find((v) => v.arm === arm && v.cell === cell)!;
  return (
    <figure className="figure">
      <div id="heatmap-exp-001" className="table-scroll" role="region" aria-label="Measured exposure heatmap, EXP-001" tabIndex={0}>
        <table className="heat">
          <caption>
            Mean final-window exposure topic entropy H_exp by ranker (rows) and cell (columns); {h.uncertainty}.
          </caption>
          <thead>
            <tr>
              <th scope="col">Ranker</th>
              {h.cells.map((c) => (
                <th scope="col" key={c.id}>{c.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {h.arms.map((a) => (
              <tr key={a.id}>
                <th scope="row">{a.label}</th>
                {h.cells.map((c) => {
                  const v = val(a.id, c.id);
                  return (
                    <td key={c.id} className={`h${level(v.mean)}`}>{v.display}</td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="legend" aria-hidden="true">
        <span className="sw h0" /> 0.95 or more <span className="sw h1" /> 0.90 <span className="sw h2" /> 0.80{" "}
        <span className="sw h3" /> 0.70 <span className="sw h4" /> 0.60 <span className="sw h5" /> below 0.60
      </p>
      <figcaption>
        Measured, confirmatory ({h.experiment_id}). A value of 1 means slates spread evenly over all ten topics; lower
        values mean narrower exposure, and darker cells are narrower. Random ranking stays near the pool's own topic mix;
        similarity ranking is the narrowest in every cell, and the bandit and MMR lie between. Popularity concentrates
        exposure on items, not on topics, so its topic entropy stays close to random. Source: <code>{h.source}</code>.
      </figcaption>
    </figure>
  );
}

export function LikeRateChart({ c }: { c: LikeRateCurve }) {
  const W = 640;
  const H = 300;
  const m = { l: 56, r: 16, t: 16, b: 46 };
  const x0 = 0;
  const x1 = 0.9;
  const y0 = Math.min(...c.points.map((p) => p.ci_low), -c.sesoi) - 0.05;
  const y1 = Math.max(...c.points.map((p) => p.ci_high), c.sesoi) + 0.05;
  const X = (v: number) => m.l + ((v - x0) / (x1 - x0)) * (W - m.l - m.r);
  const Y = (v: number) => m.t + ((y1 - v) / (y1 - y0)) * (H - m.t - m.b);
  const series = [
    { id: "uniform", label: "Uniform catalog", cls: "sa", dx: -4 },
    { id: "zipf", label: "Zipf catalog", cls: "sb", dx: 4 },
  ];
  const yTicks = [-0.6, -0.4, -0.2, 0, 0.2].filter((v) => v >= y0 && v <= y1);
  const xTicks = [0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9];
  return (
    <figure className="figure">
      <svg viewBox={`0 0 ${W} ${H}`} className="chart" role="img" aria-labelledby="lr-title lr-desc">
        <title id="lr-title">Similarity minus random in H_exp against the target like rate (exploratory)</title>
        <desc id="lr-desc">
          Two series, uniform and Zipf catalog, with 95% intervals over 5 seeds. The shaded band is the smallest effect of
          interest around zero. The dashed vertical line is the frozen calibration.
        </desc>
        <rect x={m.l} width={W - m.l - m.r} y={Y(c.sesoi)} height={Y(-c.sesoi) - Y(c.sesoi)} className="band" />
        {yTicks.map((v) => (
          <g key={v}>
            <line x1={m.l} x2={W - m.r} y1={Y(v)} y2={Y(v)} className={v === 0 ? "zero" : "grid"} />
            <text x={m.l - 6} y={Y(v) + 4} textAnchor="end" className="tick">{v.toFixed(1)}</text>
          </g>
        ))}
        {xTicks.map((v) => (
          <text key={v} x={X(v)} y={H - m.b + 16} textAnchor="middle" className="tick">{v.toFixed(2)}</text>
        ))}
        <text x={(m.l + W - m.r) / 2} y={H - 8} textAnchor="middle" className="axis">Target true like rate</text>
        <text x={14} y={(m.t + H - m.b) / 2} textAnchor="middle" className="axis" transform={`rotate(-90 14 ${(m.t + H - m.b) / 2})`}>
          Similarity - random, H_exp
        </text>
        <line x1={X(c.frozen_like_rate)} x2={X(c.frozen_like_rate)} y1={m.t} y2={H - m.b} className="frozen" />
        {series.map((s) => {
          const pts = c.points.filter((p) => p.catalog === s.id).sort((a, b) => a.target_like_rate - b.target_like_rate);
          return (
            <g key={s.id} className={s.cls}>
              <polyline points={pts.map((p) => `${X(p.target_like_rate) + s.dx},${Y(p.estimate)}`).join(" ")} className="line" />
              {pts.map((p) => (
                <g key={p.target_label}>
                  <line x1={X(p.target_like_rate) + s.dx} x2={X(p.target_like_rate) + s.dx} y1={Y(p.ci_low)} y2={Y(p.ci_high)} className="ci" />
                  {s.id === "zipf" ? (
                    <rect x={X(p.target_like_rate) + s.dx - 3.5} y={Y(p.estimate) - 3.5} width={7} height={7} className="pt" />
                  ) : (
                    <circle cx={X(p.target_like_rate) + s.dx} cy={Y(p.estimate)} r={3.5} className="pt" />
                  )}
                </g>
              ))}
            </g>
          );
        })}
      </svg>
      <p className="legend" aria-hidden="true">
        <span className="key sa">Uniform catalog (blue circles, solid line)</span> <span className="key sb">Zipf catalog (rust squares)</span>{" "}
        <span className="key band-key">shaded: within the smallest effect of interest ({c.sesoi})</span>{" "}
        <span className="key">dashed: frozen calibration ({c.frozen_like_rate})</span>
      </p>
      <figcaption>
        Measured, exploratory ({c.experiment_id}, designed after the confirmatory results; {c.uncertainty}). Below zero,
        similarity ranking gives narrower exposure than random. Under the uniform catalog the effect is near zero when
        simulated users like few of the items they see and levels off at higher like rates; under the Zipf catalog the sign
        reverses at low like rates. The exact values are in the XPL-M4-LIKERATE table above.
      </figcaption>
    </figure>
  );
}

/** Sandbox line chart of one per-step series for the two arms. */
export function StepLines({
  title,
  desc,
  a,
  b,
  labelA,
  labelB,
  marker,
}: {
  title: string;
  desc: string;
  a: number[];
  b: number[];
  labelA: string;
  labelB: string;
  marker: number;
}) {
  const W = 420;
  const H = 180;
  const m = { l: 40, r: 10, t: 10, b: 28 };
  const n = a.length;
  const X = (i: number) => m.l + (i / Math.max(n - 1, 1)) * (W - m.l - m.r);
  const Y = (v: number) => m.t + (1 - v) * (H - m.t - m.b);
  const path = (s: number[]) => s.map((v, i) => `${X(i)},${Y(v)}`).join(" ");
  const id = title.replace(/\W+/g, "-").toLowerCase();
  return (
    <figure className="figure small">
      <svg viewBox={`0 0 ${W} ${H}`} className="chart" role="img" aria-labelledby={`${id}-t ${id}-d`}>
        <title id={`${id}-t`}>{title}</title>
        <desc id={`${id}-d`}>{desc}</desc>
        {[0, 0.5, 1].map((v) => (
          <g key={v}>
            <line x1={m.l} x2={W - m.r} y1={Y(v)} y2={Y(v)} className="grid" />
            <text x={m.l - 6} y={Y(v) + 4} textAnchor="end" className="tick">{v.toFixed(1)}</text>
          </g>
        ))}
        <text x={m.l} y={H - 8} className="tick">step 1</text>
        <text x={W - m.r} y={H - 8} textAnchor="end" className="tick">step {n}</text>
        <line x1={X(marker)} x2={X(marker)} y1={m.t} y2={H - m.b} className="frozen" />
        <polyline points={path(a)} className="line sa" />
        <polyline points={path(b)} className="line sb dashed" />
      </svg>
      <figcaption>
        <span className="key sa">{labelA} (solid)</span> <span className="key sb">{labelB} (dashed)</span>. {desc}
      </figcaption>
    </figure>
  );
}

/** Sandbox exposure heatmap: topics (rows) by step bins (columns); darker = larger share. No text on cells. */
export function StepHeatmap({ shares, label, marker }: { shares: number[][]; label: string; marker: number }) {
  const bin = 5;
  const nb = Math.ceil(shares.length / bin);
  const K = shares[0]?.length ?? 10;
  const cells: number[][] = Array.from({ length: K }, () => new Array<number>(nb).fill(0));
  for (let b = 0; b < nb; b++) {
    const rows = shares.slice(b * bin, (b + 1) * bin);
    for (let z = 0; z < K; z++) cells[z][b] = rows.reduce((s, r) => s + r[z], 0) / rows.length;
  }
  const W = 420;
  const m = { l: 64, t: 4, r: 4, b: 22 };
  const cw = (W - m.l - m.r) / nb;
  const ch = 14;
  const H = m.t + K * ch + m.b;
  const top = cells.map((row, z) => ({ z, v: row[nb - 1] })).sort((p, q) => q.v - p.v)[0];
  const vmax = Math.max(...cells.flat(), 1e-9);
  return (
    <figure className="figure small">
      <svg viewBox={`0 0 ${W} ${H}`} className="chart" role="img" aria-label={`Exposure heatmap, ${label}: topic share of slate positions per ${bin}-step bin. In the last bin, ${TOPIC_NAMES[top.z]} has the largest share, ${Math.round(top.v * 100)}%.`}>
        {cells.map((row, z) => (
          <g key={z}>
            <text x={m.l - 6} y={m.t + z * ch + ch - 3} textAnchor="end" className="tick">{TOPIC_NAMES[z]}</text>
            {row.map((v, b) => (
              <rect key={b} x={m.l + b * cw} y={m.t + z * ch} width={cw - 1} height={ch - 1} className="hcell" fillOpacity={0.06 + 0.94 * (v / vmax)} />
            ))}
          </g>
        ))}
        <rect x={m.l + Math.floor(marker / bin) * cw - 1} y={m.t - 1} width={cw + 1} height={K * ch + 1} className="mark" />
        <text x={m.l} y={H - 6} className="tick">step 1</text>
        <text x={W - m.r} y={H - 6} textAnchor="end" className="tick">step {shares.length}</text>
      </svg>
      <figcaption>
        {label}. Each column is a {bin}-step bin; darker cells mean a larger share of position-weighted exposure over all
        simulated users (full colour marks the largest share in this chart). The outlined column holds the step shown in the feeds. In the last
        bin, {TOPIC_NAMES[top.z]} has the largest share ({Math.round(top.v * 100)}%).
      </figcaption>
    </figure>
  );
}
