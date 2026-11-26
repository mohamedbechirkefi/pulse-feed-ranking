// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
// Hero illustration: a monitor wall of feed slates (columns = steps, cells = slate slots, colour = topic).
// It is a drawing, not study data: the colours come from a fixed pattern below, not from the engine
// or the results file, and no number is shown.
import { useEffect, useRef, useState } from "react";

const STEPS = 24;
const SLOTS = 10;
const TOPICS = 10;
const FAVOURITE = 4;

/** Small fixed pseudo-random sequence so the drawing is the same on every visit. */
function pattern(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function buildWall(): { mixed: number[][]; narrowed: number[][] } {
  const r = pattern(20261126);
  const mixed: number[][] = [];
  const narrowed: number[][] = [];
  for (let c = 0; c < STEPS; c++) {
    const pull = Math.min(0.94, Math.pow(c / (STEPS - 4), 1.15));
    const colM: number[] = [];
    const colN: number[] = [];
    for (let s = 0; s < SLOTS; s++) {
      const t = Math.floor(r() * TOPICS);
      colM.push(t);
      colN.push(r() < pull ? (r() < 0.82 ? FAVOURITE : (FAVOURITE + 1) % TOPICS) : t);
    }
    mixed.push(colM);
    narrowed.push(colN);
  }
  return { mixed, narrowed };
}

const WALL = buildWall();
type Mode = "random" | "similarity";

export function Hero() {
  const reduce = typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  const [mode, setMode] = useState<Mode>(reduce ? "similarity" : "random");
  const [lit, setLit] = useState<boolean>(!!reduce);
  const touched = useRef(false);

  useEffect(() => {
    if (reduce) return;
    // The one orchestrated moment: light the wall, then let similarity ranking take over the schedule.
    const t1 = window.setTimeout(() => setLit(true), 120);
    const t2 = window.setTimeout(() => {
      if (!touched.current) setMode("similarity");
    }, 1700);
    return () => {
      window.clearTimeout(t1);
      window.clearTimeout(t2);
    };
  }, [reduce]);

  const choose = (m: Mode) => {
    touched.current = true;
    setLit(true);
    setMode(m);
  };

  return (
    <figure className="monitor" aria-labelledby="monitor-cap">
      <div className="monitor-bar">
        <div className="segmented" role="group" aria-label="Ranking shown on the illustration">
          <span className={`seg-ind ${mode}`} aria-hidden="true" />
          <button type="button" aria-pressed={mode === "random"} onClick={() => choose("random")}>
            Random ranking
          </button>
          <button type="button" aria-pressed={mode === "similarity"} onClick={() => choose("similarity")}>
            Content similarity
          </button>
        </div>
        <p className="illus-tag">
          <span className="lamp" aria-hidden="true" />
          Illustration, not study data
        </p>
      </div>
      <div className={`wall ${lit ? "lit" : ""} ${mode}`} aria-hidden="true">
        {WALL.mixed.map((col, c) => (
          <div className="col" key={c} style={{ ["--c" as string]: c }}>
            {col.map((t, s) => (
              <span className="cell" key={s}>
                <span className={`lay mix tp${t}`} />
                <span className={`lay nar tp${WALL.narrowed[c][s]}`} />
              </span>
            ))}
          </div>
        ))}
        <span className="playhead" />
      </div>
      <figcaption id="monitor-cap" className="monitor-cap">
        Each column is one step of a simulated feed and each cell one of the ten slots in its slate, coloured by topic.
        Under random ranking the colours stay mixed; under content similarity one topic takes over the slate. A drawing of
        the mechanism, not a measured run.
      </figcaption>
    </figure>
  );
}
