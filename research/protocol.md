<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# PULSE research protocol

**Status: DRAFT v0.1 (2026-11-24). Not frozen. Awaiting owner review and freeze (G-FREEZE).** No confirmatory run may start until the owner freezes a version, its SHA-256 is recorded in `research/decision_log.md` and `research/experiment_registry.csv`, and the owner's approval is recorded. Until then, every run is exploratory and labelled as such.

Feasibility audit: section 12 below.

## 1. Research question

How do ranking objectives influence exposure diversity and simulated preference reinforcement, in a synthetic population of users and items with topic embeddings, noisy interests and explicit feedback, when all rankers receive identical candidate pools?

Scope: simulation only. Results hold only within the stated generative assumptions. No claim is made about any real platform, about real users or about addiction (master prompt section 10, claims boundary).

## 2. Formal model (draft)

Notation. K topics; d = K embedding dimensions; N items; U users; T steps; slate size k; candidate pool size C.

- **Items.** Item i has a primary topic z_i drawn from a pool topic distribution pi (uniform in the default, skewed in sensitivity analyses). Embedding e_i = normalise(a * onehot(z_i) + epsilon_i), epsilon_i ~ N(0, sigma_item^2 I_d). Defaults: K = 10, N = 1000, a = 1, sigma_item = 0.3.
- **Users.** True preference p_u(t) on the K-simplex. Initial p_u(0) ~ Dirichlet(alpha_0 * 1_K). alpha_0 controls initial concentration (alpha_0 = 1.0 diffuse; alpha_0 = 0.1 concentrated). True utility r_ui(t) = sum_z p_uz(t) * max(e_iz, 0) normalised by the item's positive mass, in [0, 1].
- **Interaction loop.** At each step every user receives a candidate pool of C = 50 items sampled uniformly without replacement from the catalog. The pool for (seed, user, step) is identical across ranking arms (common random numbers). The ranker returns an ordered slate of k = 10 items. The user examines position j with probability beta^(j-1) (beta = 0.85), and gives explicit feedback on each examined item: like with probability sigmoid((r_ui - 0.5) / tau), tau = 0.1, else dislike. Observed feedback is flipped with probability eta (feedback noise).
- **Preference models (separate assumptions, never pooled).**
  - Static: p_u(t) = p_u(0).
  - Drifting (reinforcement): after each like on item i, p_u <- normalise((1 - gamma) * p_u + gamma * onehot(z_i)); dislikes leave p_u unchanged. gamma is the drift rate.
- **Rankers (identical candidate pool, slate size and information).**
  1. Random (primary comparator): uniform random permutation of the pool from an arm-specific seeded stream.
  2. Popularity: items ordered by global like count to date across all users of the run; ties broken by a seeded random permutation.
  3. Content similarity: user profile v_u = sum of embeddings of liked items minus sum of disliked items (observed feedback only); score = cosine(v_u, e_i); zero profile gives all-equal scores and falls back to the seeded tie-break.
  4. Bandit: per-user LinUCB (Li et al. 2010) on item embeddings with exploration parameter alpha_ucb and ridge lambda = 1, reward = observed like.
  5. Diversity-aware: maximal marginal relevance re-ranking (Carbonell and Goldstein 1998) of the content-similarity score, lambda_mmr = 0.5, item-item similarity = cosine of embeddings.
  Ties in every ranker are broken by the same documented, seeded rule (tested in M2).

## 3. Hypotheses (draft)

Primary (EXP-001, static preferences):

- **H0:** the mean, over independent seeds, of the paired difference in final-window normalised exposure topic entropy between the content-similarity ranker and the random ranker is zero.
- **H1 (directional):** the content-similarity ranker yields lower final-window normalised exposure topic entropy than the random ranker (mean paired difference < 0).
- **Contradiction:** the upper bound of the 95% interval of the mean paired difference is at or above 0, or the estimated reduction is smaller than the smallest effect of interest (0.05 normalised entropy units). The second case is reported as "no practically relevant reduction", not as equivalence.

The primary contrast is expected to favour H1 by construction of a similarity ranker; its value is in the size of the effect and in the trade-offs measured by the secondary contrasts. This is stated in advance so that the result is not presented as surprising.

Secondary contrasts (all arms against random, plus diversity-aware against content similarity) are reported with Holm adjustment over the family of five contrasts per metric. EXP-002 and EXP-003 carry their own registered hypotheses (see their protocol files).

## 4. Baseline and primary metric

- **Baseline:** the random ranker. It is the simplest ranker, it uses no feedback, and it fixes the exposure distribution to the candidate pool distribution, which makes it a neutral reference for both diversity and reinforcement.
- **Primary metric:** final-window normalised exposure topic entropy, H_exp. For user u, let q_u be the distribution of primary topics over the slates shown to u in the last W = 50 steps, position-weighted by examination probability beta^(j-1). H_exp(u) = -sum_z q_uz log q_uz / log K, in [0, 1]. The run-level value is the mean over users. Direction: lower means less diverse exposure.
- **Justification.** Exposure diversity is the outcome the question names first; it is defined for every arm and both preference models; it does not depend on the user model's choice probabilities as directly as relevance does; and it is bounded and interpretable.

## 5. Secondary metrics

| Metric | Definition | Unit |
| --- | --- | --- |
| Exposure concentration | Gini coefficient of item exposure counts over the catalog in the final window | [0, 1] |
| Relevance | Mean true utility r_ui of examined slate items, final window | [0, 1] |
| Calibration miscalibration | KL(p_u || q~_u) with q~_u = (1 - 0.01) q_u + 0.01 p_u (Steck 2018) | nats |
| User control | Mean change in exposure share of topic z between slate t and slate t+1 after an observed dislike of an item of topic z (negative = responsive) | share points |
| Preference reinforcement (drifting model only) | Delta H_pref = H(p_u(T)) - H(p_u(0)), normalised by log K | [-1, 1] |
| Like rate | Observed likes per examined item | ratio |

"User control" is a narrow operationalisation of responsiveness to explicit negative feedback. It is not a measure of human agency (limitations.md).

## 6. Experimental unit, seeds and pairing

- **Experimental unit:** one simulated population run (seed). Users inside a run share popularity counts and catalog, so they are not independent; per-user values are aggregated to one value per run before inference.
- **Seeds:** 10 independent master seeds per cell (at least 5 required). Each master seed derives, through `numpy.random.SeedSequence.spawn`, separate streams for catalog, users, candidate pools, feedback noise, examination and each ranker's tie-breaking. All arms with the same master seed share catalog, users and candidate pools (matched comparison).
- **Sample-size rationale:** with n = 10 paired seeds, the 95% t-interval half-width is about 0.72 times the standard deviation of paired differences (t_0.975,9 = 2.262, divided by sqrt(10)). If the exploratory smoke run estimates that standard deviation above 0.07 normalised entropy units, the half-width would exceed the smallest effect of interest (0.05); the frozen protocol then sets n = 20 before any confirmatory run. The seed count is fixed at freeze and never extended after looking at confirmatory results.

## 7. Uncertainty method

Per contrast and metric: mean paired difference across seeds with a 95% t-interval, a percentile bootstrap interval over seeds (10,000 resamples, fixed bootstrap seed) as a check, the paired standardised effect d_z, and the raw per-seed values. No test treats users or steps as independent observations. Holm adjustment for the secondary families. Non-significance is never read as equivalence.

## 8. Exclusion and stopping rules

- **Exclusion:** a run is excluded only for a documented implementation failure (exception, NaN in a metric, invariant violation detected by the built-in checks). Excluded runs are kept in raw results, listed in the report, and re-run once with the same seed after the fix is committed; the fix and rerun are recorded as a deviation.
- **Stopping:** fixed design. All cells of the frozen matrix run to completion; no early stopping on results. The compute stop rule is the budget below: if the full matrix exceeds it, the run stops, the shortfall is recorded, and the owner decides whether to reduce scope (never by dropping arms selectively after seeing results).

## 9. Matrices

- **Smoke matrix (exploratory, before freeze):** 5 rankers x static preferences x eta = 0.1 x alpha_0 = 1.0 x 2 seeds, U = 50, N = 300, T = 60, W = 20. Purpose: validate metrics, invariants and runtime; estimate the paired-difference standard deviation for section 6. Results are exploratory and never pooled with confirmatory runs.
- **Full matrices:** EXP-001, EXP-002 and EXP-003 protocols (`research/experiments/EXP-NNN/protocol.md`). Defaults: U = 200, N = 1000, K = 10, C = 50, k = 10, T = 200, W = 50.

| Experiment | Factors | Cells | Seeds | Runs |
| --- | --- | --- | --- | --- |
| EXP-001 static | 5 rankers x eta {0.0, 0.2} x alpha_0 {1.0, 0.1} | 20 | 10 | 200 |
| EXP-002 drifting | 5 rankers x gamma {0.01, 0.05} x alpha_0 {1.0, 0.1}, eta = 0.1 | 20 | 10 | 200 |
| EXP-003 sensitivity | 3 rankers (random, similarity, diversity-aware) x pool skew {uniform, Zipf s = 1} x tau {0.1, 0.3}, static, eta = 0.1, alpha_0 = 1.0 | 12 | 10 | 120 |

Exploration (LinUCB alpha_ucb) is varied inside EXP-001 as a nested secondary factor for the bandit arm only: alpha_ucb in {0.1, 1.0}, adding 2 x 2 x 10 = 40 bandit runs. The bandit arm used in the primary family is alpha_ucb = 1.0.

## 10. Sensitivity analysis that could invalidate the main interpretation

The main interpretation is "the ranking objective reduces exposure diversity". Two alternatives could produce the same pattern:

1. **Pool imbalance, not the objective.** If the catalog is skewed toward a few topics, low exposure entropy can come from the candidate pool rather than the ranker. EXP-003 repeats the primary contrast with a Zipf-skewed pool. If the similarity-minus-random gap shrinks below the smallest effect of interest under skew, or its sign changes, the main interpretation is restricted to balanced pools.
2. **Choice-model sharpness.** A steep like-probability curve (small tau) makes feedback near-deterministic and may manufacture narrowing. EXP-003 repeats with tau = 0.3. If the effect disappears, it is reported as dependent on choice-model sharpness.

A further check run inside EXP-002: the drift rule is replaced by an additive-then-clip rule at gamma = 0.05 for the similarity and random arms, to test whether reinforcement depends on the functional form of drift (2 arms x 2 alpha_0 levels x 10 seeds = 40 additional runs).

## 11. Compute budget

CPU only, single process, Apple M1 Pro. Budget for all full matrices: 4 hours wall clock in total, measured and recorded per run. Peak memory recorded per run where feasible.

## 12. Feasibility audit (2026-11-24)

| Item | Brief value | Measured by command | Result |
| --- | --- | --- | --- |
| CPU | Apple M1 Pro, 10 cores | `sysctl -n machdep.cpu.brand_string hw.ncpu` | Apple M1 Pro; 10 |
| RAM | 16 GB | `sysctl -n hw.memsize` | 17179869184 bytes (16 GiB) |
| OS | macOS 15.3.1 | `sw_vers` | macOS 15.3.1 (24D70) |
| Free disk | about 127 GB | `df -h /Users/bechir` | 129 GiB available |
| Python | 3.12.1 | `/usr/local/bin/python3 --version` | Python 3.12.1 |
| uv | 0.9.5 | `.tools/py/bin/uv --version` | uv 0.9.5 (2025-10-21) |
| typst | 0.15.0 | Python package import in `.tools/py` | typst 0.15.0 (Python package, no CLI binary) |
| pypdf, pillow | present | package metadata | pypdf 6.20.0, pillow 11.3.0 |
| pandoc | 3.6.3 | `.tools/pandoc --version` | pandoc 3.6.3 |
| Node | 22.23.3 | `node --version` (helix tools, read-only) | v22.23.3 |
| git | present | `git --version` | 2.42.1 |
| TeX | none | `which tex pdflatex xelatex` | not found |

**Toolchain decision (D-002).** No TeX distribution. Manuscript and report PDFs: pandoc Markdown to Typst, compiled by the `typst` Python package; `manuscript.tex` is generated from Markdown by pandoc but not compiled. A toolchain smoke check is recorded in `progress.md`.

**Time budget.** Five focused days: M0 and M1 (day 1), M2 (days 2 and 3), M3 and M4 (day 4), M5 and M6 (day 5). If threatened, cut the demo to a minimal static page and drop EXP-003's tau factor before cutting any control or report.

**Cost.** Zero. No paid service, API, dataset or compute. Dependencies are free and open source (numpy BSD-3-Clause, pytest MIT).

**Data.** Synthetic only. No external dataset is required for any registered experiment (data/manifest.json lists candidates considered and rejected).

**Exclusions (explicit scope).** No human participants, no real platform data, no scraping, no claims about real recommender systems, no reinforcement-learning ranker beyond LinUCB, no learned matrix-factorisation model in the primary matrix.

**Fallback.** If any part of the simulation proves infeasible, the minimal deliverable is EXP-001 alone (random versus content similarity, static preferences) with a full report.

## 13. Confounders and controls

- Candidate pool: identical across arms (common random numbers).
- Information: all rankers see only observed (noisy) feedback; none sees p_u.
- Slate size, examination model and step count identical across arms.
- Tie-breaking: one seeded rule for all rankers.
- Bandit tuning: alpha_ucb levels fixed in advance; no tuning on confirmatory runs.
- Held-out data: none in the supervised sense; no parameter is tuned on confirmatory runs. Smoke-run outputs may inform only the seed count (section 6) and invariant fixes, never hypotheses or metrics.

## 14. Amendments

Any amendment after freeze is dated, justified and kept separate from the frozen analysis.

## 15. Amendments before freeze (owner-approved 2026-11-24, round 2)

Authority: the owner's approvals of 2026-11-24 ("yes for all others" for the PULSE amendments; "Approve all" for the real-data round), recorded in decision D-010. This section was written and committed **before** any MovieLens rating was read or any parameter was fitted. Where it conflicts with sections 1 to 13, this section wins. The fitted values are added afterwards in section 15.11 and in the configs; the method below does not change after fitting.

### 15.1 Real data (replaces common decision C1 for PULSE)

- **Dataset:** MovieLens 1M (GroupLens; Harper and Konstan 2015, doi:10.1145/2827872), `https://files.grouplens.org/datasets/movielens/ml-1m.zip`, 5,917,549 bytes, SHA-256 `a6898adb50b9ca05aa231689da44c217cb524e7ebd39d264c56e2832f2c54e20`, accessed 2026-11-24.
- **Licence (README, read 2026-11-24):** any research purpose; no stated or implied endorsement; acknowledgement in publications; no redistribution without separate permission; no commercial or revenue-bearing use without permission. This matches the approval ("research use, no redistribution").
- **Handling:** downloaded by `scripts/download_movielens.py` into `data/raw/movielens-1m/` (git-ignored); derived files in `data/processed/` (git-ignored). Nothing derived at the level of a user or a rating is committed. Only aggregates (counts, rates, topic weights, fitted constants) appear in committed files. `users.dat` (demographics) is never read. User ids are the dataset's pseudonymous integers and are not carried into any output.
- **Role:** the simulation stays the controlled part of the study. The real data (a) calibrates the choice curve (15.4, 15.5) and (b) supplies user preferences and catalog topic weights for a second test, EXP-004 (15.6). It never replaces the synthetic generator in EXP-001 to EXP-003.

### 15.2 Ingestion and topics (fixed before reading the data)

- Inputs: `ml-1m/movies.dat` (`MovieID::Title::Genres`, genres separated by `|` from the 18-genre vocabulary of the README) and `ml-1m/ratings.dat` (`UserID::MovieID::Rating::Timestamp`, integer rating 1 to 5). A row that fails this schema is excluded and counted; if more than 1% of the rows of either file fail, ingestion stops and the owner is told.
- Topics: the K = 10 genres with the most movies (ties broken alphabetically). This keeps K = 10 of section 2.
- Primary topic of a movie: among its genres that are in the top 10, the one with the fewest movies (the most specific; ties alphabetical). A movie with no top-10 genre is excluded, with its ratings, and counted. Ratings of movies absent from `movies.dat` are excluded and counted.
- Like: rating >= 4.

### 15.3 Split (fixed before reading the data)

Users with an odd `UserID` form the **calibration half**; users with an even `UserID` form the **held-out half**. Every fitted quantity uses the calibration half only (or item-level data only, for topic weights). The held-out half is used only as the user population of EXP-004.

### 15.4 Target like rate

L* = share of calibration-half ratings (on included movies) with rating >= 4. It is read as the probability that an examined item is truly liked under random ranking in the primary configuration. Disclosure: MovieLens ratings are given to movies that users chose to watch, so L* is a selected-exposure like rate, not a like rate under random exposure. It is used as a stated calibration target, not as a measured fact about random exposure.

### 15.5 Choice-curve recalibration (replaces the planning midpoint 0.5)

- The like probability becomes sigmoid((r_ui - c) / tau), with midpoint c (config field `like_midpoint`).
- c(tau) solves M(c) = L*, where M(c) is the mean of sigmoid((r_ui - c) / tau) over all U = 200 users and all N = 1000 items of the synthetic world of each of 20 calibration seeds (700001 to 700020, disjoint from every confirmatory and exploratory seed), generated by the model's own catalog and user generators with the defaults of section 2 (uniform pool, alpha_0 = 1.0, K = 10). M is decreasing in c; c is found by bisection on [-1, 2] to a bracket width below 1e-9.
- The fit uses no ranker, no interaction loop, no exposure and no metric of section 4 or 5. It cannot use the primary contrast.
- c is fitted separately for tau = 0.1 and tau = 0.3, so that EXP-003 varies choice sharpness at a matched target like rate. One c(tau) is used in every cell with that tau; alpha_0 = 0.1, eta, pool skew and drift are not re-fitted, so their like rates differ from L* as a consequence of the manipulation and are reported per cell.
- Disclosure: this recalibration was motivated by an exploratory observation (decision D-008, P1: like rate about 0.02 under the planning midpoint), made while exploratory values of the primary contrast had been seen (freeze record, C4).

### 15.6 Second test: EXP-004 (real preferences and catalog topic weights)

- Catalog: N = 1000 synthetic items whose primary topics are drawn from pi_ML, the share of included movies with each primary topic (item-level, no user data). Embeddings as in section 2.
- Preference vectors: for user u, n_uz = number of the user's ratings >= 4 on included movies with primary topic z; p_u proportional to (n_uz + 1) / pi_ML,z, normalised to the simplex (add-one smoothing; division by pi_ML removes catalog availability, since the simulation applies pi_ML again through the catalog). Users with no included rating are excluded and counted.
- Population: in each seed, U = 200 users sampled without replacement from the held-out-half vectors with the seed's "users" stream. Static preferences.
- Choice curve: c_ML for tau = 0.1 solves the equation of 15.5 with the users drawn from the calibration-half vectors (instead of the Dirichlet) and the pi_ML catalog, on the same calibration seeds.
- Design: arms random, similarity, MMR; eta = 0.0, tau = 0.1, c = c_ML, other values as section 2; 20 seeds (104001 to 104020); 60 runs.
- Hypotheses: as the EXP-001 primary (H1: E[H_exp(similarity) - H_exp(random)] < 0; contradiction rule with smallest effect of interest 0.05). Secondary: MMR minus random, MMR minus similarity, secondary metrics, Holm within each metric family.
- Interpretation: EXP-004 is a second test of the primary contrast on real-preference inputs; it is never pooled with EXP-001. If EXP-001 supports H1 and EXP-004 meets its contradiction rule, the EXP-001 interpretation is restricted to the synthetic preference generator. EXP-004's catalog is skewed, so 15.9 applies to it.

### 15.7 User control as a difference from random

User control is interpreted only as the paired difference arm minus random. For this metric the Holm family is the four arm-minus-random contrasts (MMR minus similarity is not computed). The random arm's raw value is reported as the reference level only, never interpreted as responsiveness.

### 15.8 Seeds

20 master seeds per cell in every experiment (first seeds unchanged: 101001, 102001, 103001; EXP-004 104001). Runs: EXP-001 480 (400 plus 80 bandit alpha_ucb = 0.1), EXP-002 480 (400 plus 80 drift-form), EXP-003 240, EXP-004 60. The paired-difference SD is not re-estimated under the new calibration, because that would mean computing the primary contrast; 20 seeds is the owner's choice and is fixed now. The t-interval half-width factor at n = 20 is t_0.975,19 / sqrt(20) = 2.093 / 4.472 = 0.468.

### 15.9 Pre-decided reporting of a sign reversal under a skewed catalog

Applies to the Zipf cells of EXP-003 and to EXP-004. If the 95% t-interval of Delta = H_exp(similarity) - H_exp(random) lies entirely above 0:

1. H1 is reported as not supported in that cell;
2. the EXP-003 invalidation criterion is met, so the EXP-001 interpretation is restricted to balanced pools;
3. the reversal is reported as a measured property of this simulation under a skewed catalog. The candidate mechanism (a dislike-dominated similarity profile pushed away from the abundant topic, decision D-008, P4) is stated as an untested hypothesis, never as evidence that similarity ranking diversifies exposure in general;
4. the reversal is reported with the same prominence as the primary result, including in the abstract.

If the interval includes 0, the existing invalidation rule of EXP-003 section 5 applies unchanged.

### 15.10 Compute budget

Unchanged: 4 hours wall clock for all matrices. Planning projection from the M2 sweeps: about 32 minutes at 20 seeds for EXP-001 to EXP-003, plus about 1 minute for EXP-004.

