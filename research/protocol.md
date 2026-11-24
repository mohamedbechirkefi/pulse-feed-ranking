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

None. Any amendment after freeze is dated, justified and kept separate from the frozen analysis.
