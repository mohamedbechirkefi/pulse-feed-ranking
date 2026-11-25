// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
}

export interface Experiment {
  id: string;
  title: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface Source {
  path: string;
  sha256: string;
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  exposure_heatmap: Heatmap;
  likerate_curve: LikeRateCurve;
}

/** PULSE extension: measured EXP-001 per-arm H_exp (mean, SD over seeds) by cell. */
export interface Heatmap {
  experiment_id: string;
  label: string;
  metric: string;
  uncertainty: string;
  source: string;
  arms: { id: string; label: string }[];
  cells: { id: string; label: string }[];
  values: { arm: string; cell: string; mean: number; sd: number; n: number; display: string }[];
}

/** PULSE extension: exploratory like-rate dependence of the primary contrast (manuscript Table 7). */
export interface LikeRatePoint {
  catalog: string;
  target_like_rate: number;
  target_label: string;
  n_seeds: number;
  estimate: number;
  ci_low: number;
  ci_high: number;
  display: string;
  interval_display: string;
}

export interface LikeRateCurve {
  experiment_id: string;
  label: string;
  metric: string;
  uncertainty: string;
  sesoi: number;
  frozen_like_rate: number;
  points: LikeRatePoint[];
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
  };
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    exposure_heatmap: heatmap(o.exposure_heatmap),
    likerate_curve: likerateCurve(o.likerate_curve),
  };
}

function idLabels(o: Obj, k: string, where: string): { id: string; label: string }[] {
  const out = arr(o, k, where).map((v, i) => {
    const x = obj(v, `${where}.${k}[${i}]`);
    return { id: str(x, "id", `${where}.${k}[${i}]`), label: str(x, "label", `${where}.${k}[${i}]`) };
  });
  if (out.length === 0) throw new ResultsError(`${where}.${k}: empty`);
  if (new Set(out.map((x) => x.id)).size !== out.length) throw new ResultsError(`${where}.${k}: duplicate id`);
  return out;
}

function heatmap(v: unknown): Heatmap {
  const w = "exposure_heatmap";
  const o = obj(v, w);
  const arms = idLabels(o, "arms", w);
  const cells = idLabels(o, "cells", w);
  const values = arr(o, "values", w).map((x, i) => {
    const e = obj(x, `${w}.values[${i}]`);
    const mean = num(e, "mean", `${w}.values[${i}]`) as number;
    const sd = num(e, "sd", `${w}.values[${i}]`) as number;
    if (mean < 0 || mean > 1) throw new ResultsError(`${w}.values[${i}].mean: outside [0, 1]`);
    if (sd < 0) throw new ResultsError(`${w}.values[${i}].sd: negative`);
    return {
      arm: str(e, "arm", `${w}.values[${i}]`),
      cell: str(e, "cell", `${w}.values[${i}]`),
      mean,
      sd,
      n: num(e, "n", `${w}.values[${i}]`) as number,
      display: str(e, "display", `${w}.values[${i}]`),
    };
  });
  const keys = new Set(values.map((x) => `${x.arm}|${x.cell}`));
  for (const a of arms)
    for (const c of cells)
      if (!keys.has(`${a.id}|${c.id}`)) throw new ResultsError(`${w}: missing value for ${a.id} in ${c.id}`);
  if (keys.size !== values.length || values.length !== arms.length * cells.length) {
    throw new ResultsError(`${w}.values: duplicate or unknown arm/cell`);
  }
  return {
    experiment_id: str(o, "experiment_id", w),
    label: str(o, "label", w),
    metric: str(o, "metric", w),
    uncertainty: str(o, "uncertainty", w),
    source: str(o, "source", w),
    arms,
    cells,
    values,
  };
}

function likerateCurve(v: unknown): LikeRateCurve {
  const w = "likerate_curve";
  const o = obj(v, w);
  const points = arr(o, "points", w).map((x, i) => {
    const p = obj(x, `${w}.points[${i}]`);
    const at = `${w}.points[${i}]`;
    const pt: LikeRatePoint = {
      catalog: str(p, "catalog", at),
      target_like_rate: num(p, "target_like_rate", at) as number,
      target_label: str(p, "target_label", at),
      n_seeds: num(p, "n_seeds", at) as number,
      estimate: num(p, "estimate", at) as number,
      ci_low: num(p, "ci_low", at) as number,
      ci_high: num(p, "ci_high", at) as number,
      display: str(p, "display", at),
      interval_display: str(p, "interval_display", at),
    };
    if (pt.ci_low > pt.ci_high) throw new ResultsError(`${at}: ci_low exceeds ci_high`);
    if (pt.target_like_rate <= 0 || pt.target_like_rate >= 1) throw new ResultsError(`${at}.target_like_rate: outside (0, 1)`);
    return pt;
  });
  if (points.length < 2) throw new ResultsError(`${w}.points: fewer than two points`);
  return {
    experiment_id: str(o, "experiment_id", w),
    label: str(o, "label", w),
    metric: str(o, "metric", w),
    uncertainty: str(o, "uncertainty", w),
    sesoi: num(o, "sesoi", w) as number,
    frozen_like_rate: num(o, "frozen_like_rate", w) as number,
    points,
  };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "no interval";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
