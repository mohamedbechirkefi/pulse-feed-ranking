// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
// Bounded, cancellable sandbox run: two rankers side by side on one simulated world, sharing every
// random draw (common random numbers). The loop is the TypeScript port in engine.ts. Output is
// sandbox output, never a research result.
import { BrowserDraws, Simulation, type Metrics, type RankerId, type SimSettings, type StepView } from "./engine";
import { MAX_SEED, settingsFor, type SandboxParams } from "./sandboxConfig";

export type WorkerRequest = { type: "run"; params: SandboxParams } | { type: "cancel" };
export type WorkerReply =
  | { type: "progress"; fraction: number }
  | { type: "done"; params: SandboxParams; settings: SimSettings; a: ArmResult; b: ArmResult }
  | { type: "cancelled" }
  | { type: "error"; message: string };

export interface ArmResult {
  ranker: RankerId;
  steps: StepView[];
  metrics: Metrics;
}

let cancelled = false;

function check(p: SandboxParams): void {
  if (!Number.isInteger(p.seed) || p.seed < 1 || p.seed > MAX_SEED) throw new Error(`seed must be an integer from 1 to ${MAX_SEED}`);
  if (!(p.eta >= 0 && p.eta <= 0.5)) throw new Error("feedback noise out of range");
}

async function run(p: SandboxParams): Promise<WorkerReply> {
  check(p);
  const s = settingsFor(p);
  const draws = new BrowserDraws(p.seed, s, { skew: p.skew, alpha0: 1, itemSignal: 1, itemNoise: 0.3 });
  const simA = new Simulation(p.armA, s, draws.world);
  const simB = new Simulation(p.armB, s, draws.world);
  const stepsA: StepView[] = [];
  const stepsB: StepView[] = [];
  for (let t = 0; t < s.nSteps; t++) {
    const d = draws.next();
    stepsA.push(simA.step(d));
    stepsB.push(simB.step(d));
    if (t % 10 === 9) {
      await new Promise((r) => setTimeout(r, 0)); // let a cancel message in
      if (cancelled) return { type: "cancelled" };
      postMessage({ type: "progress", fraction: (t + 1) / s.nSteps } satisfies WorkerReply);
    }
  }
  return {
    type: "done",
    params: p,
    settings: s,
    a: { ranker: p.armA, steps: stepsA, metrics: simA.metrics() },
    b: { ranker: p.armB, steps: stepsB, metrics: simB.metrics() },
  };
}

onmessage = async (ev: MessageEvent<WorkerRequest>) => {
  const m = ev.data;
  if (m.type === "cancel") {
    cancelled = true;
    return;
  }
  cancelled = false;
  try {
    postMessage((await run(m.params)) satisfies WorkerReply);
  } catch (e) {
    postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
  }
};
