// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
// Parity of the TypeScript port with the Python research engine. The fixture holds every random
// input of tiny Python runs (scripts/export_sandbox_fixture.py) and the slates and metrics that
// pulse.simulate.simulate produced. Tolerance: slates identical; metrics within 1e-9 absolute.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { BrowserDraws, quantise, Simulation, type RankerId, type SimSettings, type StepDraws, type World } from "./engine";

interface FixtureStep { pool: number[][]; tie: number[][]; exam: number[][]; like: number[][]; flip: number[][] }
interface FixtureCase {
  name: string;
  config: Record<string, number | string | null>;
  world: { topics: number[]; emb: number[][]; pos_share: number[][]; p0: number[][]; steps: FixtureStep[] };
  runs: { ranker: RankerId; slates: number[][][]; metrics: Record<string, number | null> }[];
}

const fx = JSON.parse(readFileSync("src/fixtures/engine_fixture.json", "utf8")) as { tolerance: number; cases: FixtureCase[] };
const TOL = 1e-9;
const flat = (a: number[][]) => Float64Array.from(a.flat());

function settings(c: FixtureCase["config"]): SimSettings {
  const n = (k: string) => c[k] as number;
  return {
    nUsers: n("n_users"), nItems: n("n_items"), nTopics: n("n_topics"), poolSize: n("pool_size"),
    slateSize: n("slate_size"), nSteps: n("n_steps"), window: n("window"), beta: n("beta"), tau: n("tau"),
    likeMidpoint: n("like_midpoint"), eta: n("eta"), preferenceModel: c.preference_model as "static" | "drifting",
    gamma: n("gamma"), alphaUcb: n("alpha_ucb"), ridgeLambda: n("ridge_lambda"), lambdaMmr: n("lambda_mmr"),
    calibAlpha: n("calib_alpha"),
  };
}

describe("TypeScript port against the Python research engine (shared random inputs)", () => {
  it("fixture states the tolerance used here", () => {
    expect(fx.tolerance).toBe(TOL);
    expect(fx.cases.length).toBeGreaterThanOrEqual(3);
  });
  for (const c of fx.cases) {
    for (const run of c.runs) {
      it(`${c.name} / ${run.ranker}: identical slates, metrics within ${TOL}`, () => {
        const s = settings(c.config);
        const w: World = {
          topics: Int32Array.from(c.world.topics), emb: flat(c.world.emb), posShare: flat(c.world.pos_share), p0: flat(c.world.p0),
        };
        const sim = new Simulation(run.ranker, s, w);
        for (const st of c.world.steps) {
          const d: StepDraws = {
            pool: Int32Array.from(st.pool.flat()), tie: flat(st.tie), exam: flat(st.exam), like: flat(st.like), flip: flat(st.flip),
          };
          sim.step(d);
        }
        expect(sim.slates.map((x) => Array.from(x))).toEqual(run.slates.map((x) => x.flat()));
        const m = sim.metrics() as unknown as Record<string, number | null>;
        for (const [k, v] of Object.entries(run.metrics)) {
          if (v === null) expect(m[k]).toBeNull();
          else expect(Math.abs((m[k] as number) - v)).toBeLessThanOrEqual(TOL);
        }
      });
    }
  }
});

describe("browser random inputs", () => {
  const s: SimSettings = {
    nUsers: 6, nItems: 80, nTopics: 10, poolSize: 15, slateSize: 5, nSteps: 12, window: 4, beta: 0.85, tau: 0.1,
    likeMidpoint: 0.066421, eta: 0.1, preferenceModel: "drifting", gamma: 0.05, alphaUcb: 1, ridgeLambda: 1, lambdaMmr: 0.5, calibAlpha: 0.01,
  };
  const opts = { skew: "zipf" as const, alpha0: 0.1, itemSignal: 1, itemNoise: 0.3 };
  const run = (seed: number) => {
    const d = new BrowserDraws(seed, s, opts);
    const sim = new Simulation("similarity", s, d.world);
    for (let t = 0; t < s.nSteps; t++) sim.step(d.next());
    return sim.metrics();
  };
  it("are deterministic per seed and differ across seeds", () => {
    expect(run(7)).toEqual(run(7));
    expect(run(7).h_exp).not.toBe(run(8).h_exp);
  });
  it("produce valid pools and simplex preferences", () => {
    const d = new BrowserDraws(3, s, opts);
    const p = d.next().pool;
    for (let u = 0; u < s.nUsers; u++) {
      const row = Array.from(p.subarray(u * s.poolSize, (u + 1) * s.poolSize));
      expect(new Set(row).size).toBe(s.poolSize);
      expect(row).toEqual([...row].sort((a, b) => a - b));
    }
    for (let u = 0; u < s.nUsers; u++) {
      const sum = Array.from(d.world.p0.subarray(u * 10, u * 10 + 10)).reduce((a, b) => a + b, 0);
      expect(Math.abs(sum - 1)).toBeLessThan(1e-12);
    }
  });
  it("quantise makes scores equal in exact arithmetic compare equal (decision D-006)", () => {
    expect(quantise(1 / Math.sqrt(1) + 1e-16)).toBe(quantise(1));
    expect(quantise(0.1 + 0.2)).toBe(quantise(0.3));
    expect(quantise(-0.3)).toBe(-0.3);
  });
});
