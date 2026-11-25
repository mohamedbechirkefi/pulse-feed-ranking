// SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
// TypeScript port of the PULSE interaction loop (src/pulse/simulate.py), rankers (src/pulse/rankers.py)
// and metrics (src/pulse/metrics.py). Given the same random inputs it reproduces the Python engine:
// engine.test.ts replays draws recorded from the research engine (scripts/export_sandbox_fixture.py)
// and compares slates exactly and metrics within 1e-9. In the browser the random inputs come from a
// different generator (mulberry32 streams below, not numpy's PCG64), at a reduced size, so a sandbox
// run never reproduces a research run: it is illustrative, not the research engine.

export type RankerId = "random" | "popularity" | "similarity" | "linucb" | "mmr";
export const RANKERS: RankerId[] = ["random", "popularity", "similarity", "linucb", "mmr"];

export interface SimSettings {
  nUsers: number;
  nItems: number;
  nTopics: number;
  poolSize: number;
  slateSize: number;
  nSteps: number;
  window: number;
  beta: number;
  tau: number;
  likeMidpoint: number;
  eta: number;
  preferenceModel: "static" | "drifting";
  gamma: number;
  alphaUcb: number;
  ridgeLambda: number;
  lambdaMmr: number;
  calibAlpha: number;
}

/** Catalog and initial preferences, flattened row-major. */
export interface World {
  topics: Int32Array; // (N)
  emb: Float64Array; // (N, K)
  posShare: Float64Array; // (N, K)
  p0: Float64Array; // (U, K)
}

/** Random inputs of one step, shared by every arm (common random numbers, as in the research engine). */
export interface StepDraws {
  pool: Int32Array; // (U, C), ascending per user
  tie: Float64Array; // (U, C)
  exam: Float64Array; // (U, k)
  like: Float64Array; // (U, k)
  flip: Float64Array; // (U, k)
}

export interface Metrics {
  h_exp: number;
  gini_exposure: number;
  relevance: number | null;
  miscalibration_kl: number;
  user_control: number | null;
  like_rate: number | null;
  delta_h_pref: number | null;
}

/** np.round(x, 12): scale, round half to even, unscale (rankers.quantise, decision D-006). */
export function quantise(x: number): number {
  const y = x * 1e12;
  let r = Math.round(y);
  if (Math.abs(y % 1) === 0.5 && r % 2 !== 0) r -= 1;
  return r / 1e12;
}

function normEntropy(row: ArrayLike<number>, off: number, K: number): number {
  let s = 0;
  for (let z = 0; z < K; z++) s += row[off + z];
  if (!(s > 0)) throw new Error("entropy of an empty distribution");
  let h = 0;
  for (let z = 0; z < K; z++) {
    const q = row[off + z] / s;
    if (q > 0) h -= q * Math.log(q);
  }
  return h / Math.log(K);
}

export function gini(counts: ArrayLike<number>): number {
  const s = Array.from(counts).sort((a, b) => a - b);
  const n = s.length;
  let total = 0;
  for (const c of s) total += c;
  if (total === 0) throw new Error("gini of all-zero counts");
  let acc = 0;
  for (let i = 1; i <= n; i++) acc += (2 * i - n - 1) * s[i - 1];
  return acc / (n * total);
}

/** Pool indices of the top k: quantised score descending, then tie key ascending, then pool position. */
function orderByScore(scores: Float64Array, tie: Float64Array, off: number, C: number, k: number): number[] {
  const idx = Array.from({ length: C }, (_, i) => i);
  const q = idx.map((i) => quantise(scores[off + i]));
  for (const v of q) if (!Number.isFinite(v)) throw new Error("non-finite ranking score");
  idx.sort((a, b) => q[b] - q[a] || tie[off + a] - tie[off + b] || a - b);
  return idx.slice(0, k);
}

interface Ranker {
  rank(d: StepDraws, poolEmb: Float64Array): Int32Array; // (U, k) pool positions
  update(slate: Int32Array, examined: Uint8Array, observed: Uint8Array): void;
}

function makeRanker(id: RankerId, s: SimSettings, w: World): Ranker {
  const { nUsers: U, nTopics: K, poolSize: C, slateSize: k } = s;
  const byScore = (scores: Float64Array, d: StepDraws) => {
    const out = new Int32Array(U * k);
    for (let u = 0; u < U; u++) out.set(orderByScore(scores, d.tie, u * C, C, k), u * k);
    return out;
  };

  if (id === "random") {
    return { rank: (d) => byScore(new Float64Array(U * C), d), update: () => {} };
  }

  if (id === "popularity") {
    const likes = new Float64Array(s.nItems);
    return {
      rank: (d) => {
        const sc = new Float64Array(U * C);
        for (let i = 0; i < U * C; i++) sc[i] = likes[d.pool[i]];
        return byScore(sc, d);
      },
      update: (slate, ex, ob) => {
        for (let i = 0; i < U * k; i++) if (ex[i] && ob[i]) likes[slate[i]] += 1;
      },
    };
  }

  if (id === "similarity" || id === "mmr") {
    const profile = new Float64Array(U * K);
    const cosine = (poolEmb: Float64Array) => {
      const out = new Float64Array(U * C);
      for (let u = 0; u < U; u++) {
        let n2 = 0;
        for (let z = 0; z < K; z++) n2 += profile[u * K + z] ** 2;
        const norm = Math.sqrt(n2);
        if (norm === 0) continue;
        for (let c = 0; c < C; c++) {
          let dot = 0;
          for (let z = 0; z < K; z++) dot += profile[u * K + z] * poolEmb[(u * C + c) * K + z];
          out[u * C + c] = dot / norm;
        }
      }
      return out;
    };
    const update = (slate: Int32Array, ex: Uint8Array, ob: Uint8Array) => {
      for (let u = 0; u < U; u++) {
        for (let z = 0; z < K; z++) {
          let acc = 0;
          for (let j = 0; j < k; j++) {
            const sign = ex[u * k + j] ? (ob[u * k + j] ? 1 : -1) : 0;
            acc += sign * w.emb[slate[u * k + j] * K + z];
          }
          profile[u * K + z] += acc;
        }
      }
    };
    if (id === "similarity") return { rank: (d, pe) => byScore(cosine(pe), d), update };
    const lam = s.lambdaMmr;
    return {
      update,
      rank: (d, pe) => {
        const rel = cosine(pe);
        const out = new Int32Array(U * k);
        for (let u = 0; u < U; u++) {
          const sim = new Float64Array(C * C);
          for (let a = 0; a < C; a++)
            for (let b = 0; b < C; b++) {
              let dot = 0;
              for (let z = 0; z < K; z++) dot += pe[(u * C + a) * K + z] * pe[(u * C + b) * K + z];
              sim[a * C + b] = dot;
            }
          const chosen = new Uint8Array(C);
          const maxSim = new Float64Array(C);
          for (let j = 0; j < k; j++) {
            let best = -Infinity;
            const score = new Float64Array(C);
            for (let c = 0; c < C; c++) {
              const raw = j > 0 ? lam * rel[u * C + c] - (1 - lam) * maxSim[c] : lam * rel[u * C + c];
              score[c] = chosen[c] ? -Infinity : quantise(raw);
              if (score[c] > best) best = score[c];
            }
            let pick = -1;
            for (let c = 0; c < C; c++) {
              if (chosen[c] || score[c] !== best) continue;
              if (pick < 0 || d.tie[u * C + c] < d.tie[u * C + pick]) pick = c;
            }
            out[u * k + j] = pick;
            chosen[pick] = 1;
            for (let c = 0; c < C; c++) maxSim[c] = j > 0 ? Math.max(maxSim[c], sim[pick * C + c]) : sim[pick * C + c];
          }
        }
        return out;
      },
    };
  }

  // LinUCB (Li et al. 2010), Sherman-Morrison updates of A^-1.
  const Ainv = new Float64Array(U * K * K);
  const b = new Float64Array(U * K);
  for (let u = 0; u < U; u++) for (let z = 0; z < K; z++) Ainv[u * K * K + z * K + z] = 1 / s.ridgeLambda;
  return {
    rank: (d, pe) => {
      const sc = new Float64Array(U * C);
      for (let u = 0; u < U; u++) {
        const A = u * K * K;
        const theta = new Float64Array(K);
        for (let r = 0; r < K; r++) {
          let acc = 0;
          for (let e = 0; e < K; e++) acc += Ainv[A + r * K + e] * b[u * K + e];
          theta[r] = acc;
        }
        for (let c = 0; c < C; c++) {
          const x = (u * C + c) * K;
          let mean = 0;
          let v = 0;
          for (let r = 0; r < K; r++) {
            mean += pe[x + r] * theta[r];
            let row = 0;
            for (let e = 0; e < K; e++) row += Ainv[A + r * K + e] * pe[x + e];
            v += pe[x + r] * row;
          }
          sc[u * C + c] = mean + s.alphaUcb * Math.sqrt(Math.max(v, 0));
        }
      }
      return byScore(sc, d);
    },
    update: (slate, ex, ob) => {
      for (let j = 0; j < k; j++) {
        for (let u = 0; u < U; u++) {
          if (!ex[u * k + j]) continue;
          const A = u * K * K;
          const x = w.emb.subarray(slate[u * k + j] * K, slate[u * k + j] * K + K);
          const Ax = new Float64Array(K);
          for (let r = 0; r < K; r++) {
            let acc = 0;
            for (let e = 0; e < K; e++) acc += Ainv[A + r * K + e] * x[e];
            Ax[r] = acc;
          }
          let denom = 1;
          for (let r = 0; r < K; r++) denom += x[r] * Ax[r];
          for (let r = 0; r < K; r++) for (let e = 0; e < K; e++) Ainv[A + r * K + e] -= (Ax[r] * Ax[e]) / denom;
          if (ob[u * k + j]) for (let r = 0; r < K; r++) b[u * K + r] += x[r];
        }
      }
    },
  };
}

/** What one step showed, for the page: the focal user's slate and population-level exposure. */
export interface StepView {
  focalItems: number[];
  focalTopics: number[];
  focalExamined: boolean[];
  focalLiked: boolean[];
  topicShare: number[]; // position-weighted exposure share of each topic over all users, this step
  meanSlateEntropy: number; // mean over users of the normalised entropy of this step's slate
  meanPrefEntropy: number; // mean normalised preference entropy after this step
  focalPref: number[];
}

/** One arm of the loop, advanced one step at a time so that a worker can cancel between steps. */
export class Simulation {
  readonly s: SimSettings;
  private w: World;
  private ranker: Ranker;
  private pref: Float64Array;
  private posW: Float64Array;
  private t = 0;
  private topicW: Float64Array;
  private exposure: Float64Array;
  private relSum = 0;
  private nExam = 0;
  private nLike = 0;
  private ctrlSum = 0;
  private ctrlEvents = 0;
  private prevShare: Float64Array | null = null;
  private prevDislike: Float64Array | null = null;
  readonly slates: Int32Array[] = [];

  constructor(id: RankerId, s: SimSettings, w: World) {
    this.s = s;
    this.w = w;
    this.ranker = makeRanker(id, s, w);
    this.pref = Float64Array.from(w.p0);
    this.posW = Float64Array.from({ length: s.slateSize }, (_, j) => s.beta ** j);
    this.topicW = new Float64Array(s.nUsers * s.nTopics);
    this.exposure = new Float64Array(s.nItems);
  }

  step(d: StepDraws, focal = 0): StepView {
    const { nUsers: U, nTopics: K, poolSize: C, slateSize: k, nSteps: T, window: W } = this.s;
    const { topics, emb, posShare } = this.w;
    const pref = this.pref;
    const poolEmb = new Float64Array(U * C * K);
    for (let i = 0; i < U * C; i++) poolEmb.set(emb.subarray(d.pool[i] * K, d.pool[i] * K + K), i * K);
    const order = this.ranker.rank(d, poolEmb);
    const slate = new Int32Array(U * k);
    for (let u = 0; u < U; u++) for (let j = 0; j < k; j++) slate[u * k + j] = d.pool[u * C + order[u * k + j]];
    for (let u = 0; u < U; u++) {
      const seen = new Set<number>();
      for (let j = 0; j < k; j++) seen.add(slate[u * k + j]);
      if (seen.size !== k) throw new Error(`duplicate item in a slate at step ${this.t}`);
    }

    const examined = new Uint8Array(U * k);
    const trueLike = new Uint8Array(U * k);
    const observed = new Uint8Array(U * k);
    const r = new Float64Array(U * k);
    for (let u = 0; u < U; u++)
      for (let j = 0; j < k; j++) {
        const i = u * k + j;
        const item = slate[i];
        let util = 0;
        for (let z = 0; z < K; z++) util += pref[u * K + z] * posShare[item * K + z];
        r[i] = util;
        examined[i] = d.exam[i] < this.posW[j] ? 1 : 0;
        const p = 1 / (1 + Math.exp(-(util - this.s.likeMidpoint) / this.s.tau));
        trueLike[i] = d.like[i] < p ? 1 : 0;
        observed[i] = trueLike[i] ^ (d.flip[i] < this.s.eta ? 1 : 0);
      }

    this.ranker.update(slate, examined, observed);

    const share = new Float64Array(U * K);
    const dislike = new Float64Array(U * K);
    for (let u = 0; u < U; u++)
      for (let j = 0; j < k; j++) {
        const z = topics[slate[u * k + j]];
        share[u * K + z] += 1 / k;
        if (examined[u * k + j] && !observed[u * k + j]) dislike[u * K + z] += 1;
      }
    if (this.prevShare && this.prevDislike) {
      for (let i = 0; i < U * K; i++) {
        this.ctrlSum += this.prevDislike[i] * (share[i] - this.prevShare[i]);
        this.ctrlEvents += this.prevDislike[i];
      }
    }
    this.prevShare = share;
    this.prevDislike = dislike;

    const stepW = new Float64Array(U * K);
    for (let u = 0; u < U; u++)
      for (let j = 0; j < k; j++) stepW[u * K + topics[slate[u * k + j]]] += this.posW[j];
    if (this.t >= T - W) {
      for (let i = 0; i < U * K; i++) this.topicW[i] += stepW[i];
      for (let i = 0; i < U * k; i++) {
        this.exposure[slate[i]] += 1;
        if (examined[i]) {
          this.relSum += r[i];
          this.nExam += 1;
          if (observed[i]) this.nLike += 1;
        }
      }
    }

    if (this.s.preferenceModel === "drifting" && this.s.gamma > 0) {
      const g = this.s.gamma;
      for (let j = 0; j < k; j++)
        for (let u = 0; u < U; u++) {
          const i = u * k + j;
          if (!(examined[i] && trueLike[i])) continue;
          const zt = topics[slate[i]];
          let sum = 0;
          const row = new Float64Array(K);
          for (let z = 0; z < K; z++) {
            row[z] = (1 - g) * pref[u * K + z] + (z === zt ? g : 0);
            sum += row[z];
          }
          for (let z = 0; z < K; z++) pref[u * K + z] = row[z] / sum;
        }
    }
    for (let u = 0; u < U; u++) {
      let sum = 0;
      for (let z = 0; z < K; z++) {
        if (pref[u * K + z] < 0) throw new Error(`preference left the simplex at step ${this.t}`);
        sum += pref[u * K + z];
      }
      if (Math.abs(sum - 1) > 1e-9) throw new Error(`preference left the simplex at step ${this.t}`);
    }

    this.slates.push(slate);
    this.t += 1;

    const topicShare = new Array<number>(K).fill(0);
    let tot = 0;
    let hs = 0;
    let hp = 0;
    for (let u = 0; u < U; u++) {
      for (let z = 0; z < K; z++) {
        topicShare[z] += stepW[u * K + z];
        tot += stepW[u * K + z];
      }
      hs += normEntropy(stepW, u * K, K);
      hp += normEntropy(pref, u * K, K);
    }
    const f = focal * k;
    return {
      focalItems: Array.from(slate.subarray(f, f + k)),
      focalTopics: Array.from(slate.subarray(f, f + k), (it) => topics[it]),
      focalExamined: Array.from(examined.subarray(f, f + k), (x) => x === 1),
      focalLiked: Array.from(observed.subarray(f, f + k), (x) => x === 1),
      topicShare: topicShare.map((x) => x / tot),
      meanSlateEntropy: hs / U,
      meanPrefEntropy: hp / U,
      focalPref: Array.from(pref.subarray(focal * K, focal * K + K)),
    };
  }

  metrics(): Metrics {
    const { nUsers: U, nTopics: K } = this.s;
    if (this.t !== this.s.nSteps) throw new Error("metrics requested before the last step");
    let h = 0;
    let kl = 0;
    let dh = 0;
    const a = this.s.calibAlpha;
    for (let u = 0; u < U; u++) {
      h += normEntropy(this.topicW, u * K, K);
      let s = 0;
      for (let z = 0; z < K; z++) s += this.topicW[u * K + z];
      for (let z = 0; z < K; z++) {
        const p = this.pref[u * K + z];
        const qt = (1 - a) * (this.topicW[u * K + z] / s) + a * p;
        if (p > 0) kl += p * Math.log(p / qt);
      }
      dh += normEntropy(this.pref, u * K, K) - normEntropy(this.w.p0, u * K, K);
    }
    return {
      h_exp: h / U,
      gini_exposure: gini(this.exposure),
      relevance: this.nExam ? this.relSum / this.nExam : null,
      miscalibration_kl: kl / U,
      user_control: this.ctrlEvents ? this.ctrlSum / this.ctrlEvents : null,
      like_rate: this.nExam ? this.nLike / this.nExam : null,
      delta_h_pref: this.s.preferenceModel === "drifting" ? dh / U : null,
    };
  }
}

// ---------------------------------------------------------------------------------------------
// Browser random inputs: seeded mulberry32 streams, one per component (catalog, users, pools,
// examination, choice, noise, tiebreak), so both arms of a sandbox run share every draw.

export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function streamSeed(seed: number, stream: number): number {
  let h = (seed ^ 0x9e3779b9) >>> 0;
  h = Math.imul(h ^ (h >>> 16), 0x85ebca6b) >>> 0;
  h = (h + Math.imul(stream + 1, 0xc2b2ae35)) >>> 0;
  h = Math.imul(h ^ (h >>> 13), 0x27d4eb2f) >>> 0;
  return (h ^ (h >>> 16)) >>> 0;
}

function normal(rng: () => number): number {
  const u1 = 1 - rng();
  const u2 = rng();
  return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
}

function gammaDraw(rng: () => number, shape: number): number {
  if (shape < 1) return gammaDraw(rng, shape + 1) * Math.pow(1 - rng(), 1 / shape);
  const d = shape - 1 / 3;
  const c = 1 / Math.sqrt(9 * d);
  for (;;) {
    const x = normal(rng);
    const v = (1 + c * x) ** 3;
    if (v <= 0) continue;
    const u = 1 - rng();
    if (Math.log(u) < 0.5 * x * x + d - d * v + d * Math.log(v)) return d * v;
  }
}

export interface WorldOptions {
  skew: "uniform" | "zipf";
  alpha0: number;
  itemSignal: number;
  itemNoise: number;
}

export class BrowserDraws {
  private s: SimSettings;
  private pools: () => number;
  private exam: () => number;
  private like: () => number;
  private noise: () => number;
  private tieb: () => number;
  readonly world: World;

  constructor(seed: number, s: SimSettings, o: WorldOptions) {
    this.s = s;
    const r = (i: number) => mulberry32(streamSeed(seed, i));
    const catalog = r(0);
    const users = r(1);
    this.pools = r(2);
    this.exam = r(3);
    this.like = r(4);
    this.noise = r(5);
    this.tieb = r(6);
    const { nItems: N, nTopics: K, nUsers: U } = s;
    const pi = Array.from({ length: K }, (_, z) => (o.skew === "zipf" ? 1 / (z + 1) : 1));
    const piSum = pi.reduce((x, y) => x + y, 0);
    const topics = new Int32Array(N);
    const emb = new Float64Array(N * K);
    const posShare = new Float64Array(N * K);
    for (let i = 0; i < N; i++) {
      let u = catalog() * piSum;
      let z = 0;
      while (z < K - 1 && u >= pi[z]) u -= pi[z++];
      topics[i] = z;
      let n2 = 0;
      for (let q = 0; q < K; q++) {
        const v = (q === z ? o.itemSignal : 0) + o.itemNoise * normal(catalog);
        emb[i * K + q] = v;
        n2 += v * v;
      }
      const norm = Math.sqrt(n2);
      let mass = 0;
      for (let q = 0; q < K; q++) {
        emb[i * K + q] /= norm;
        mass += Math.max(emb[i * K + q], 0);
      }
      for (let q = 0; q < K; q++)
        posShare[i * K + q] = mass > 0 ? Math.max(emb[i * K + q], 0) / mass : q === z ? 1 : 0;
    }
    const p0 = new Float64Array(U * K);
    for (let u = 0; u < U; u++) {
      let sum = 0;
      for (let z = 0; z < K; z++) {
        p0[u * K + z] = gammaDraw(users, o.alpha0);
        sum += p0[u * K + z];
      }
      if (!(sum > 0)) {
        p0[u * K + Math.floor(users() * K)] = 1;
        sum = 1;
      }
      for (let z = 0; z < K; z++) p0[u * K + z] /= sum;
    }
    this.world = { topics, emb, posShare, p0 };
  }

  next(): StepDraws {
    const { nUsers: U, nItems: N, poolSize: C, slateSize: k } = this.s;
    const pool = new Int32Array(U * C);
    const idx = new Int32Array(N);
    for (let u = 0; u < U; u++) {
      for (let i = 0; i < N; i++) idx[i] = i;
      for (let i = 0; i < C; i++) {
        const j = i + Math.floor(this.pools() * (N - i));
        const t = idx[i];
        idx[i] = idx[j];
        idx[j] = t;
      }
      const chosen = Array.from(idx.subarray(0, C)).sort((a, b) => a - b);
      pool.set(chosen, u * C);
    }
    const fill = (n: number, g: () => number) => Float64Array.from({ length: n }, () => g());
    return { pool, tie: fill(U * C, this.tieb), exam: fill(U * k, this.exam), like: fill(U * k, this.like), flip: fill(U * k, this.noise) };
  }
}
