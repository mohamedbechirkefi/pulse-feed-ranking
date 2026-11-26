// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
import { useEffect, useState } from "react";
import { fmtEstimate, fmtInterval, loadResults, ResultsError, type Experiment, type Results } from "./results";
import { Sandbox } from "./Sandbox";
import { axisFor, ExposureMeters, IntervalGlyph, LikeRateChart, MeasuredHeatmap } from "./charts";
import { Hero } from "./Hero";

const REPO = "https://github.com/mohamedbechirkefi/pulse-feed-ranking";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

/** Label kind from the exported status: measured confirmatory, measured exploratory, or registered and not run. */
function kind(e: Experiment): { cls: string; text: string } {
  if (e.status.startsWith("confirmatory")) return { cls: "lab-conf", text: "Measured, confirmatory" };
  if (e.status.startsWith("exploratory")) return { cls: "lab-expl", text: "Measured, exploratory" };
  return { cls: "lab-reg", text: "Registered, not run" };
}

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="topbar">
        <div className="topbar-in">
          <a className="brand" href="#top" aria-label="Pulse, back to the top">
            <img src="./brand/pulse-lockup.svg" alt="" width="70" height="21" />
          </a>
          <nav aria-label="Sections">
            <a href="#overview">Overview</a>
            <a href="#results">Results</a>
            <a href="#figures">Figures</a>
            <a href="#sandbox">Sandbox</a>
            <a href="#method">Limitations</a>
            <a href="#reproduce">Reproduce</a>
          </nav>
        </div>
      </header>
      <div className="hero" id="top">
        <div className="wrap hero-in">
          <div className="hero-copy">
            <p className="kicker">PULSE, a recommender simulation study</p>
            <h1>What happens to exposure when a feed learns what you like?</h1>
            <p className="answer">
              Within this simulation, ranking by content similarity narrowed the topics simulated users were shown,
              compared with random ranking, in every confirmatory exposure test. That result is conditional: it holds at
              the calibrated like rate.
            </p>
            <p className="dek">
              Five ranking objectives, identical candidate pools, simulated users only. Nothing on this page describes a
              real platform or real people.
            </p>
          </div>
          <Hero />
        </div>
      </div>
      <main id="main">
        {state.kind === "loading" && <p role="status" className="wrap">Loading the published results.</p>}
        {state.kind === "error" && (
          <div role="alert" className="wrap panel error">
            <h2>Results unavailable</h2>
            <p>The published results file failed validation, so no numbers are shown.</p>
            <p><code>{state.message}</code></p>
          </div>
        )}
        {state.kind === "ready" && <Published r={state.results} />}
        <div className="wrap"><Sandbox /></div>
        {state.kind === "ready" && <Method r={state.results} />}
        <section id="reproduce" aria-labelledby="h-reproduce" className="wrap">
          <h2 id="h-reproduce">Reproduce</h2>
          <p>
            Every number above is exported from committed results by <code>scripts/export_demo_data.py</code> and checked
            against the manuscript by the repository's tests. From a clone of the repository:
          </p>
          <pre className="cmd" tabIndex={0} role="region" aria-label="Reproduction commands"><code>{`uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-001
PYTHONPATH=src .venv/bin/python scripts/analyse_experiment.py EXP-001
cd demo && npm ci && npm run build && npm run preview`}</code></pre>
          <p className="note">
            A run is refused unless its config matches the owner's freeze record. EXP-004 also needs the MovieLens 1M
            files, which are not redistributed; the repository README explains how to fetch and check them.
          </p>
        </section>
      </main>
      <footer className="site">
        <div className="wrap foot">
          <p>By Mohamed Bechir Kefi, independent researcher.</p>
          <ul className="foot-links">
            <li><a href={REPO}>Source repository on GitHub</a></li>
            <li><a href={`${REPO}/blob/main/research/paper/manuscript.md`}>Manuscript (preprint draft, not peer-reviewed)</a></li>
            <li><a href="https://labs.kefimohamedbechir.workers.dev">All studies in the labs index</a></li>
          </ul>
          <p>
            Runs offline after the first load. No data about visitors is collected, stored or sent anywhere; there are no
            cookies, analytics or external requests. Source-available under the PULSE Non-Commercial Research License
            (see <code>LICENSE</code>). Page address: pulse-feed-ranking.kefimohamedbechir.workers.dev.
          </p>
          <p>An AI system was used as a research and development assistant and is not an author.</p>
          <p>
            Type: Unbounded and Figtree, both under the SIL Open Font License, self-hosted from the Fontsource
            packages.
          </p>
        </div>
      </footer>
    </>
  );
}

function Published({ r }: { r: Results }) {
  return (
    <>
      <section id="key" aria-labelledby="h-key" className="wrap keyres">
        <h2 id="h-key">The key result, as exposure meters</h2>
        <p className="lede">
          How evenly each ranker spread its slates over the ten topics in the primary cell of EXP-001, with static
          preferences. Random ranking stays near the pool's own topic mix; similarity ranking is the narrowest.
        </p>
        <ExposureMeters h={r.exposure_heatmap} />
      </section>
      <section id="overview" aria-labelledby="h-overview" className="wrap">
        <h2 id="h-overview">Overview</h2>
        <p className="status-label">{r.status_label}</p>
        <p className="question">{r.question}</p>
        <p>
          Within this simulation, ranking by content similarity narrowed the topics simulated users were shown, compared
          with random ranking, in every confirmatory exposure test (EXP-001, EXP-003, EXP-004), and concentrated drifting
          simulated preferences (EXP-002). That result is conditional: it holds at the calibrated like rate, and an
          exploratory check found it near zero, or reversed in sign under a skewed catalog, when simulated users like few
          of the items they see. Diversity-aware re-ranking (MMR) recovered part of the loss.
        </p>
        <dl className="key-legend" aria-label="How values are labelled">
          <div><dt><span className="label-tag lab-conf">Measured, confirmatory</span></dt><dd>Frozen protocol, 20 paired seeds per cell, verdict under the frozen rule.</dd></div>
          <div><dt><span className="label-tag lab-expl">Measured, exploratory</span></dt><dd>Committed runs outside a frozen protocol; never changes a verdict.</dd></div>
          <div><dt><span className="label-tag lab-reg">Registered, not run</span></dt><dd>A protocol exists; no data exists.</dd></div>
          <div><dt><span className="label-tag lab-assume">Assumption</span></dt><dd>A model input chosen or fitted before the runs, not a result.</dd></div>
          <div><dt><span className="label-tag sandbox-tag">Sandbox output</span></dt><dd>Computed in your browser; illustrative, not the research engine.</dd></div>
        </dl>
      </section>

      <section id="results" aria-labelledby="h-results" className="wrap">
        <h2 id="h-results">Published results</h2>
        <p className="note">
          Numbers are copied from the committed results (analysis code revision <code>{r.code_revision.slice(0, 7)}</code>) and
          printed exactly as in the manuscript. Differences are treatment minus control, paired by seed, with 95% t-intervals
          unless stated. The glyph beside each row draws the interval on one axis per experiment, with zero marked; null,
          exploratory and not-run entries are shown in the same format as the others.
        </p>
        {r.experiments.map((e) => <ExperimentPanel key={e.id} e={e} />)}
      </section>

      <section id="figures" aria-labelledby="h-figures" className="wrap">
        <h2 id="h-figures">Figures from the exported data</h2>
        <h3><span className="label-tag lab-conf">Measured, confirmatory</span> Exposure heatmap, EXP-001</h3>
        <MeasuredHeatmap h={r.exposure_heatmap} />
        <h3><span className="label-tag lab-expl">Measured, exploratory</span> The like-rate boundary</h3>
        <LikeRateChart c={r.likerate_curve} />
      </section>

    </>
  );
}

function Method({ r }: { r: Results }) {
  return (
    <>
      <section id="assumptions" aria-labelledby="h-assumptions" className="wrap">
        <h2 id="h-assumptions"><span className="label-tag lab-assume">Assumption</span> Assumptions</h2>
        <p className="note">Model inputs fixed or fitted before the confirmatory runs. They are not results.</p>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>
                {a.value} <span className="meta">({a.source})</span>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" aria-labelledby="h-method" className="wrap">
        <h2 id="h-method">Method and limitations</h2>
        <p>
          Each run simulates 200 users for 200 steps. At every step each user receives a pool of 50 items, identical for
          every ranker, and the ranker returns a slate of 10. Simulated users examine positions with decaying probability
          and like an examined item with a probability that rises with its true utility; observed feedback is flipped
          with probability eta. The primary metric is the topic entropy of the final 50 slates. Protocols, seeds and
          decision rules were frozen by the owner before any confirmatory run; the analysis code was committed before the
          data. The full method is in <code>research/paper/manuscript.md</code>; each experiment has a standalone report.
        </p>
        <h3>Limitations (from <code>research/limitations.md</code>)</h3>
        <ul>
          {r.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
        <details>
          <summary>Source files and hashes</summary>
          <ul className="meta">
            {r.sources.map((s) => (
              <li key={s.path}>
                <code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}

function ExperimentPanel({ e }: { e: Experiment }) {
  const k = kind(e);
  const axis = axisFor(e.estimates);
  return (
    <article className={`panel ${k.cls}-panel`} aria-labelledby={`h-${e.id}`}>
      <p className={`label-tag ${k.cls}`}>{k.text}</p>
      <h3 id={`h-${e.id}`}>
        {e.id}: {e.title}
      </h3>
      <p>
        <span className="badge">{e.status}</span>
      </p>
      <p>
        <strong>Verdict:</strong> {e.verdict}
      </p>
      {e.estimates.length > 0 ? (
        <div id={`est-${e.id}`} className="table-scroll" role="region" aria-label={`${e.id} estimates`} tabIndex={0}>
          <table className="est">
            <thead>
              <tr>
                <th scope="col">Quantity</th>
                <th scope="col">Estimate</th>
                <th scope="col">95% interval</th>
                <th scope="col" className="glyph-col">
                  Interval glyph <span className="meta">(zero marked)</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {e.estimates.map((x) => (
                <tr key={x.label}>
                  <th scope="row">{x.label}</th>
                  <td className="num" data-label="Estimate">{fmtEstimate(x)}</td>
                  <td className="num" data-label="95% interval">{fmtInterval(x)}</td>
                  <td className="glyph-col"><IntervalGlyph e={x} axis={axis} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="empty">No estimate: this experiment has not been run, so there is nothing to show.</p>
      )}
      {e.notes.map((n, i) => (
        <p key={i} className="note">{n}</p>
      ))}
      <p className="meta">
        Report: <code>{e.report_path}</code>
        {e.claim_ids.length > 0 ? <> · Claims: {e.claim_ids.join(", ")}</> : <> · Claims: none</>}
      </p>
    </article>
  );
}
