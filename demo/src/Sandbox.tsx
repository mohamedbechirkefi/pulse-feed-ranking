// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
// Visitor sandbox: two simulated feeds side by side, computed in a Web Worker by the TypeScript port
// of the PULSE loop. Its output is labelled sandbox output and is never mixed with published results.
// Nothing here is stored or sent: settings live in memory and vanish on reload.
import { useEffect, useRef, useState } from "react";
import type { Metrics, RankerId } from "./engine";
import { MAX_SEED, SANDBOX_SIZE, type SandboxParams } from "./sandboxConfig";
import type { ArmResult, WorkerReply, WorkerRequest } from "./sandbox.worker";
import { StepHeatmap, StepLines, TOPIC_NAMES } from "./charts";

const RANKER_LABEL: Record<RankerId, string> = {
  random: "Random",
  popularity: "Popularity",
  similarity: "Content similarity",
  linucb: "Bandit (LinUCB)",
  mmr: "MMR (diversity-aware)",
};

const MIDPOINTS = [
  { value: 0.066421, label: "Frozen calibration midpoint c = 0.066421 (research like rate 0.577)" },
  { value: 0.5, label: "Planning midpoint c = 0.5 (research like rate about 0.02)" },
];

export const DEFAULTS: SandboxParams = {
  seed: 1,
  armA: "random",
  armB: "similarity",
  preferenceModel: "static",
  skew: "uniform",
  eta: 0.1,
  likeMidpoint: 0.066421,
};

type Done = Extract<WorkerReply, { type: "done" }>;

const f3 = (x: number | null) => (x === null ? "not defined" : x.toFixed(3));

const METRIC_ROWS: { key: keyof Metrics; label: string }[] = [
  { key: "h_exp", label: "H_exp, final window (exposure topic entropy)" },
  { key: "gini_exposure", label: "Gini of item exposure" },
  { key: "relevance", label: "Relevance (mean true utility of examined items)" },
  { key: "like_rate", label: "Observed like rate" },
  { key: "miscalibration_kl", label: "Miscalibration KL (nats)" },
  { key: "user_control", label: "User control (interpret only as arm minus random)" },
  { key: "delta_h_pref", label: "Delta H_pref (drifting model only)" },
];

export function Sandbox() {
  const worker = useRef<Worker | null>(null);
  const [p, setP] = useState<SandboxParams>(DEFAULTS);
  const [seedText, setSeedText] = useState(String(DEFAULTS.seed));
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [out, setOut] = useState("");
  const [res, setRes] = useState<Done | null>(null);
  const [step, setStep] = useState<number>(SANDBOX_SIZE.nSteps);

  useEffect(() => {
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      if (m.type === "progress") {
        setProgress(m.fraction);
        return;
      }
      if (m.type === "done") {
        setRes(m);
        setStep(m.settings.nSteps);
        setOut(
          `Sandbox output, seed ${m.params.seed}: final-window exposure entropy ${f3(m.a.metrics.h_exp)} for ${RANKER_LABEL[m.a.ranker]} and ${f3(m.b.metrics.h_exp)} for ${RANKER_LABEL[m.b.ranker]}; observed like rate ${f3(m.a.metrics.like_rate)} and ${f3(m.b.metrics.like_rate)}.`,
        );
      }
      if (m.type === "error") setOut(`The sandbox run stopped with an error: ${m.message}`);
      if (m.type === "cancelled") setOut("Sandbox run cancelled. Nothing was kept.");
      setRunning(false);
    };
    worker.current = w;
    return () => w.terminate();
  }, []);

  const seedValid = /^\d+$/.test(seedText) && Number(seedText) >= 1 && Number(seedText) <= MAX_SEED;

  const run = () => {
    if (!seedValid) {
      setOut(`Enter a whole-number seed from 1 to ${MAX_SEED}.`);
      return;
    }
    const params = { ...p, seed: Number(seedText) };
    setP(params);
    setRunning(true);
    setProgress(0);
    setOut("");
    worker.current?.postMessage({ type: "run", params } satisfies WorkerRequest);
  };
  const cancel = () => worker.current?.postMessage({ type: "cancel" } satisfies WorkerRequest);
  const reset = () => {
    if (running) cancel();
    setP(DEFAULTS);
    setSeedText(String(DEFAULTS.seed));
    setRes(null);
    setOut("");
    setProgress(0);
    setStep(SANDBOX_SIZE.nSteps);
  };
  const exportJson = () => {
    if (!res) return;
    const blob = new Blob([JSON.stringify({ label: "PULSE sandbox output (illustrative, not the research engine)", params: res.params, settings: res.settings, metrics: { [res.a.ranker + "_A"]: res.a.metrics, [res.b.ranker + "_B"]: res.b.metrics } }, null, 1)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pulse-sandbox-seed-${res.params.seed}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const set = <K extends keyof SandboxParams>(k: K, v: SandboxParams[K]) => setP((q) => ({ ...q, [k]: v }));

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <p className="label-tag sandbox-tag">Sandbox output: illustrative, not the research engine</p>
      <h2 id="h-sandbox">Sandbox: two feeds, one simulated world</h2>
      <p>
        Pick two rankers. Both rank the same {SANDBOX_SIZE.nUsers} simulated users, {SANDBOX_SIZE.nItems} synthetic items
        and candidate pools for {SANDBOX_SIZE.nSteps} steps, with identical random draws, so any difference comes from the
        ranker. The loop, rankers and metrics are a port of the research code, checked against it on recorded random
        inputs (identical slates, metrics within 1e-9). The world is smaller and the random-number generator is not the
        research one, so a sandbox seed never reproduces a research run, and its numbers are not comparable with the
        published results above.
      </p>
      <p className="note">
        The feeds are lists of numbered synthetic items, not content. There is no autoplay, no endless feed, no score and
        no reward: each run stops after {SANDBOX_SIZE.nSteps} steps. Your settings stay in this tab and are never stored
        or sent.
      </p>

      <form className="controls" onSubmit={(e) => { e.preventDefault(); run(); }} aria-describedby="ctrl-help">
        <label>
          Seed
          <input id="sb-seed" inputMode="numeric" value={seedText} onChange={(e) => setSeedText(e.target.value.trim())} aria-invalid={!seedValid} />
        </label>
        <label>
          Feed A
          <select id="sb-arm-a" value={p.armA} onChange={(e) => set("armA", e.target.value as RankerId)}>
            {(Object.keys(RANKER_LABEL) as RankerId[]).map((r) => <option key={r} value={r}>{RANKER_LABEL[r]}</option>)}
          </select>
        </label>
        <label>
          Feed B
          <select id="sb-arm-b" value={p.armB} onChange={(e) => set("armB", e.target.value as RankerId)}>
            {(Object.keys(RANKER_LABEL) as RankerId[]).map((r) => <option key={r} value={r}>{RANKER_LABEL[r]}</option>)}
          </select>
        </label>
        <label>
          Preferences
          <select id="sb-pref" value={p.preferenceModel} onChange={(e) => set("preferenceModel", e.target.value as "static" | "drifting")}>
            <option value="static">Static</option>
            <option value="drifting">Drifting toward liked topics (gamma 0.05)</option>
          </select>
        </label>
        <label>
          Catalog
          <select id="sb-skew" value={p.skew} onChange={(e) => set("skew", e.target.value as "uniform" | "zipf")}>
            <option value="uniform">Uniform over topics</option>
            <option value="zipf">Zipf-skewed</option>
          </select>
        </label>
        <label>
          Feedback noise
          <select id="sb-eta" value={p.eta} onChange={(e) => set("eta", Number(e.target.value))}>
            <option value={0}>None (eta 0)</option>
            <option value={0.1}>10% flipped (eta 0.1)</option>
            <option value={0.2}>20% flipped (eta 0.2)</option>
          </select>
        </label>
        <label className="wide">
          Choice curve
          <select id="sb-midpoint" value={p.likeMidpoint} onChange={(e) => set("likeMidpoint", Number(e.target.value))}>
            {MIDPOINTS.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
          </select>
        </label>
        <div className="buttons">
          <button type="submit" disabled={running}>Run</button>
          <button type="button" onClick={cancel} disabled={!running}>Cancel</button>
          <button type="button" onClick={reset}>Reset</button>
        </div>
      </form>
      <p id="ctrl-help" className="note">
        Assumption values: the midpoints are the research values, but in this smaller world the like rate they produce is
        measured again and shown after each run. Reset restores the defaults and clears the output.
      </p>
      {running && (
        <p role="status" className="note">Computing: {Math.round(progress * 100)}% of the steps done.</p>
      )}
      <p aria-live="polite" className="sandbox-out">{out}</p>

      {res && <SandboxResult res={res} step={step} setStep={setStep} onExport={exportJson} />}
    </section>
  );
}

function SandboxResult({ res, step, setStep, onExport }: { res: Done; step: number; setStep: (n: number) => void; onExport: () => void }) {
  const n = res.settings.nSteps;
  const lab = (x: ArmResult, tag: string) => `Feed ${tag}: ${RANKER_LABEL[x.ranker]}`;
  return (
    <div className="sandbox-result">
      <div className="step-ctl">
        <label>
          Step shown in the feeds: {step} of {n}
          <input id="sb-step" type="range" min={1} max={n} value={step} onChange={(e) => setStep(Number(e.target.value))} />
        </label>
      </div>
      <div className="feeds">
        <Feed arm={res.a} tag="A" step={step} />
        <Feed arm={res.b} tag="B" step={step} />
      </div>

      <h3>Preference and exposure timelines</h3>
      <div className="pair">
        <StepLines
          title="Exposure entropy per step"
          desc="Mean over users of the normalised topic entropy of each step's slate (1 = all topics equally, 0 = one topic). A slate of 10 items rarely covers all 10 topics, so even random ranking stays below 1 here; the research metric pools the last 50 slates."
          a={res.a.steps.map((s) => s.meanSlateEntropy)}
          b={res.b.steps.map((s) => s.meanSlateEntropy)}
          labelA={lab(res.a, "A")}
          labelB={lab(res.b, "B")}
          marker={step - 1}
        />
        <StepLines
          title="Preference entropy per step"
          desc={
            res.params.preferenceModel === "static"
              ? "Mean normalised entropy of the simulated preferences. Under static preferences it cannot change, so both lines are flat by construction."
              : "Mean normalised entropy of the simulated preferences, which drift toward liked topics in this setting."
          }
          a={res.a.steps.map((s) => s.meanPrefEntropy)}
          b={res.b.steps.map((s) => s.meanPrefEntropy)}
          labelA={lab(res.a, "A")}
          labelB={lab(res.b, "B")}
          marker={step - 1}
        />
      </div>

      <h3>Exposure heatmaps</h3>
      <div className="pair">
        <StepHeatmap shares={res.a.steps.map((s) => s.topicShare)} label={lab(res.a, "A")} marker={step - 1} />
        <StepHeatmap shares={res.b.steps.map((s) => s.topicShare)} label={lab(res.b, "B")} marker={step - 1} />
      </div>

      <h3>Run metrics (sandbox output)</h3>
      <div id="sandbox-metrics" className="table-scroll" role="region" aria-label="Sandbox run metrics" tabIndex={0}>
        <table>
          <thead>
            <tr>
              <th scope="col">Metric, final {res.settings.window} steps</th>
              <th scope="col">{lab(res.a, "A")}</th>
              <th scope="col">{lab(res.b, "B")}</th>
            </tr>
          </thead>
          <tbody>
            {METRIC_ROWS.map((r) => (
              <tr key={r.key}>
                <th scope="row">{r.label}</th>
                <td>{f3(res.a.metrics[r.key])}</td>
                <td>{f3(res.b.metrics[r.key])}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="note">
        One seed, one reduced world, no interval: this is a single illustrative run, not evidence. The published results
        use 20 paired seeds per cell and the research engine.
      </p>
      <button type="button" onClick={onExport}>Save this sandbox output as JSON</button>
    </div>
  );
}

function Feed({ arm, tag, step }: { arm: ArmResult; tag: string; step: number }) {
  const s = arm.steps[step - 1];
  const pref = s.focalPref.map((v, z) => ({ v, z })).sort((a, b) => b.v - a.v)[0];
  return (
    <article className={`feed feed-${tag.toLowerCase()}`} aria-labelledby={`feed-${tag}`}>
      <h3 id={`feed-${tag}`}>
        Feed {tag}: {RANKER_LABEL[arm.ranker]}
      </h3>
      <p className="meta">
        Simulated user 1, step {step}. Strongest preference: {TOPIC_NAMES[pref.z]} ({Math.round(pref.v * 100)}%).
      </p>
      <ol className="cards">
        {s.focalItems.map((item, j) => {
          const z = s.focalTopics[j];
          const state = !s.focalExamined[j] ? "not examined" : s.focalLiked[j] ? "liked (observed)" : "disliked (observed)";
          return (
            <li key={j} className={`card t${z}`}>
              <span className="topic">
                <span className="dot" aria-hidden="true" />
                {TOPIC_NAMES[z]}
              </span>
              <span className="item">Item {item + 1}</span>
              <span className={`fb ${s.focalExamined[j] ? (s.focalLiked[j] ? "like" : "dislike") : "skip"}`}>{state}</span>
            </li>
          );
        })}
      </ol>
    </article>
  );
}
