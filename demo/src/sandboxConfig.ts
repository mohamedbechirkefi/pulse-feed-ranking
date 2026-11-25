// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
// Sandbox parameters shared by the page and the worker (kept out of the worker module so that
// importing them never starts a worker body on the main thread).
import type { RankerId, SimSettings } from "./engine";

export interface SandboxParams {
  seed: number;
  armA: RankerId;
  armB: RankerId;
  preferenceModel: "static" | "drifting";
  skew: "uniform" | "zipf";
  eta: number;
  likeMidpoint: number;
}

/** Reduced world: about a quarter of the research users, a third of the items, 120 steps. */
export const SANDBOX_SIZE = { nUsers: 60, nItems: 300, nTopics: 10, poolSize: 30, slateSize: 10, nSteps: 120, window: 30 } as const;
export const MAX_SEED = 1_000_000;

export function settingsFor(p: SandboxParams): SimSettings {
  return {
    ...SANDBOX_SIZE,
    beta: 0.85,
    tau: 0.1,
    likeMidpoint: p.likeMidpoint,
    eta: p.eta,
    preferenceModel: p.preferenceModel,
    gamma: p.preferenceModel === "drifting" ? 0.05 : 0,
    alphaUcb: 1,
    ridgeLambda: 1,
    lambdaMmr: 0.5,
    calibAlpha: 0.01,
  };
}

