// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
  it("rejects a missing exposure heatmap", () => {
    const r = good();
    delete r.exposure_heatmap;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a heatmap with a missing arm-cell value", () => {
    const r = good();
    r.exposure_heatmap.values.pop();
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a heatmap entropy outside [0, 1]", () => {
    const r = good();
    r.exposure_heatmap.values[0].mean = 1.2;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an inverted like-rate interval", () => {
    const r = good();
    const p = r.likerate_curve.points[0];
    [p.ci_low, p.ci_high] = [p.ci_high, p.ci_low];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a like-rate point without display text", () => {
    const r = good();
    delete r.likerate_curve.points[0].display;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("keeps EXP-005 as registered, not run, with no estimate", () => {
    const e = validateResults(good()).experiments.find((x) => x.id === "EXP-005");
    expect(e?.status).toBe("registered, not frozen, not run");
    expect(e?.estimates.length).toBe(0);
  });
});
