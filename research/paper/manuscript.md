<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Content-similarity ranking and topic exposure in a matched-pool recommender simulation: confirmatory effects and a like-rate boundary

**Status: independent research manuscript / preprint draft, not peer-reviewed.** Version 0.2 (M4 synthesis, 2026-11-25, revised after the second review pass, `research/publication/review_pass_2.md`). Markdown is the canonical source; `manuscript.tex` and `manuscript.pdf` are generated from it by `scripts/build_pdfs.py` (M6 release candidate, 2026-11-25).

**Author.** Mohamed Bechir Kefi (no affiliation). Authorship approved by the owner (decision C3, 2026-11-24). An AI system was used as a research and development assistant and is not an author (section 11).

**Data acknowledgement (required by the GroupLens licence).** This work uses the MovieLens 1M dataset (Harper and Konstan 2015). No endorsement by the University of Minnesota or GroupLens is stated or implied. The data is not redistributed.

## Abstract

Simulation studies report that recommender feedback loops can homogenise what users are shown. We ask how five ranking objectives (random, popularity, content similarity, a LinUCB bandit and maximal marginal relevance re-ranking) change exposure diversity and simulated preference concentration when every ranker receives identical candidate pools, users and noisy explicit feedback. Four confirmatory experiments (1,260 runs, 20 paired seeds per cell, protocol frozen before execution) compare each ranker with random ranking. With static synthetic preferences, content similarity lowered final-window exposure topic entropy by 0.4000 normalised units (95% paired t-interval [-0.4028, -0.3972]); with MovieLens-derived preferences and catalog weights the reduction was 0.4095 ([-0.4210, -0.3980]). Under a drifting-preference assumption, similarity concentrated preferences by 0.4350 ([-0.4387, -0.4313]) relative to random, under which preferences spread. A Zipf-skewed catalog enlarged the reduction instead of removing it. Diversity-aware re-ranking recovered between 45% and 79% of the exposure-entropy loss across cells (supplementary Table S3), at a small cost in relevance. All of these results hold at one calibration of the choice curve, fitted to a like rate of 0.577 and chosen after a pre-freeze exploratory run had shown a near-zero effect at a like rate of about 0.02. An exploratory check made after the confirmatory results (5 seeds) found the similarity effect near zero when simulated users like 2% to 5% of what they see, and a reversed sign under the skewed catalog. The narrowing is therefore a conditional property of this simulation, not a general law of similarity ranking, and nothing here describes real platforms or people.

**Keywords:** recommender systems; feedback loops; exposure diversity; simulation; preregistration; maximal marginal relevance.

## 1. Introduction

Recommender systems decide which items a user sees, and what the user sees shapes the feedback the system learns from. Simulation studies have argued that this loop can homogenise behaviour (Chaney et al. 2018), amplify popularity bias (Mansoury et al. 2020) and degenerate user interest (Jiang et al. 2019), and models of preference drift show conditions under which recommendations amplify preferences (Kalimeris et al. 2021). These results come from different simulators, rankers and assumptions, which makes it hard to say how much of an effect belongs to the ranking objective itself.

This study isolates the ranking objective. Five rankers receive the same catalog, the same simulated users, the same candidate pool at every step and the same noisy explicit feedback (common random numbers), so a difference in exposure is attributable to the ranker within the model. The questions, hypotheses, metrics, seeds, decision rules and one sensitivity analysis able to restrict the interpretation were frozen before any confirmatory run (protocol v1.0, 2026-11-24).

**Research question.** How do ranking objectives influence exposure diversity and simulated preference reinforcement when all rankers receive identical candidate pools?

**Hypotheses.** H1 (EXP-001): with static preferences, content similarity yields lower final-window exposure topic entropy than random ranking, by at least the smallest effect of interest of 0.05. H1 (EXP-002): with drifting preferences, similarity yields a larger decrease in preference entropy than random. EXP-003 tests whether the EXP-001 result survives a skewed catalog and a flatter choice curve; EXP-004 repeats EXP-001 with MovieLens-derived inputs.

**Contributions.** (1) A matched-pool effect size for five standard ranking objectives under static and drifting preference assumptions kept strictly separate. (2) A preregistered sensitivity analysis and a second test on real-data-derived inputs, both reported with their frozen verdicts. (3) A disclosed, post hoc exploratory finding that the main effect depends on how often simulated users like what they see, which bounds the interpretation of every confirmatory result. (4) A reproducible artifact: configs, raw run files, checksums, analysis code committed before the data and an evidence manifest. No new phenomenon is claimed; the direction of the primary effect was expected by construction (protocol section 3).

## 2. Related work

The sources below were first opened on 2026-11-24 as listed in `research/literature_review.md`. On 2026-11-25 (M6) the full text of nine of the ten primary sources was opened from free, legal copies (arXiv, author or institutional pages) and each statement made here was checked against it; the location checked is given for each source in `research/publication/evidence_audit.md` (finding F-5). The full text of Steck (2018) could not be opened legally at no cost and is marked. This is a targeted scan, not a systematic review.

- **Feedback-loop homogenisation.** Chaney et al. (2018) simulate recommenders trained on data confounded by their own recommendations and report increased homogeneity of user behaviour without a gain in utility (full text; sections 2 and 5.2). Mansoury et al. (2020) report in offline simulation that feedback loops amplify popularity bias and reduce aggregate diversity (full text; section 4.3). The present study differs by fixing candidate pools across rankers and by measuring topic-level exposure rather than item-level behaviour.
- **Degeneracy and drift.** Jiang et al. (2019) formalise degenerate feedback loops, distinguish echo chambers from filter bubbles and study exploration with bandit simulations (full text; introduction and simulation experiments). Kalimeris et al. (2021) model users drifting toward recommended content and give conditions for preference amplification (full text of the author PDF; sections 2.1 and 3). EXP-002 adopts one explicit drift rule of this kind as an assumption; it does not test whether people drift.
- **Simulation as configurable assumptions.** RecSim (Ie et al. 2019) and T-RECS (Lucherini et al. 2021) present recommender simulation as a set of configurable assumptions about users and choice (full texts; RecSim section 3.1, T-RECS sections 4.1 and 4.2). Our sensitivity analysis and the M4 exploratory check follow that view: they vary the assumptions most likely to drive the result.
- **Rankers and metrics.** LinUCB (Li et al. 2010; full text, section 3.1 and Algorithm 1) is the bandit arm. Maximal marginal relevance (Carbonell and Goldstein 1998; full text of the two-page author PDF, section 2) is the diversity-aware arm. The miscalibration metric follows the KL definition attributed to Steck (2018), KL(p || (1 - alpha) q + alpha p) with alpha 0.01. Only bibliographic metadata of Steck (2018) was accessed; the formula and the value of alpha were checked against a secondary source that restates them (da Silva and Jannach 2025, sections 3.1.4 and 3.1.5), not against Steck's own text (evidence audit, finding F-5).
- **Data.** MovieLens (Harper and Konstan 2015) is cited as the GroupLens licence requires. The author preprint on the GroupLens site was opened at M6; it lists MovieLens 1M as 6,040 users, 3,706 movies and 1,000,209 ratings on a 1 to 5 star scale (section 3). The volume, issue and DOI are taken from the dataset README.

Relative to this work, PULSE is a small replication-style extension: it reproduces the qualitative homogenisation result under tightly matched conditions and adds effect sizes, trade-offs and a measured boundary condition.

## 3. Formal model

**Items.** K = 10 topics, N = 1,000 items. Item i has primary topic z_i drawn from a catalog distribution pi (uniform, Zipf with exponent 1, or the MovieLens shares pi_ML) and embedding e_i = normalise(onehot(z_i) + epsilon_i), epsilon_i ~ N(0, 0.3^2 I_K).

**Users.** U = 200 users with preference vectors p_u on the K-simplex, either Dirichlet(alpha_0 1_K) with alpha_0 in {1.0, 0.1} or MovieLens-derived (section 4.3). True utility r_ui = sum_z p_uz max(e_iz, 0) / sum_z max(e_iz, 0), in [0, 1].

**Interaction loop.** For T = 200 steps, each user receives a candidate pool of C = 50 items drawn uniformly without replacement; the pool is identical across rankers for a given seed, user and step. The ranker returns a slate of k = 10. The user examines position j with probability 0.85^(j-1) and likes an examined item with probability sigmoid((r_ui - c) / tau). Observed feedback is flipped with probability eta.

**Preference models.** Static: p_u(t) = p_u(0). Drifting: after each like of an item of topic z, p_u <- normalise((1 - gamma) p_u + gamma onehot(z)). The two are separate assumptions and are never pooled.

**Rankers.** (1) Random: a seeded uniform permutation of the pool. (2) Popularity: global like count so far. (3) Content similarity: cosine between the item embedding and the profile v_u = (sum of liked embeddings) - (sum of disliked embeddings), from observed feedback. (4) LinUCB per user, ridge 1, exploration alpha_ucb 1.0 (0.1 as a nested level). (5) MMR re-ranking of the similarity score with lambda 0.5. All rankers break ties with the same seeded rule.

**Metrics.** The primary metric is final-window normalised exposure topic entropy, H_exp(u) = -sum_z q_uz ln q_uz / ln K, where q_u is the position-weighted topic distribution of the slates shown to u in the last W = 50 steps; the run value is the mean over users. Lower values mean less diverse exposure. EXP-002's primary metric is Delta H_pref = (H(p_u(T)) - H(p_u(0))) / ln K, averaged over users; negative values mean preferences concentrated. Secondary metrics are the Gini coefficient of item exposure counts, relevance (mean true utility of examined items), miscalibration KL(p_u || 0.99 q_u + 0.01 p_u) in nats, user control (mean change in the exposure share of a topic in the slate after an observed dislike of that topic, interpreted only as arm minus random) and the observed like rate.

## 4. Methods

### 4.1 Design and estimand

The experimental unit is one simulated population run (a master seed). Users inside a run share popularity counts and the catalog, so per-user values are averaged to one value per run before inference. All arms with the same master seed share catalog, users and candidate pools, so contrasts are paired by seed. The estimand is the mean over seeds of the paired difference, treatment minus random.

### 4.2 Experiments

Table 1 lists the frozen matrices. Every cell has 20 seeds (seed ranges 101001, 102001, 103001 and 104001 onward).

**Table 1. Confirmatory matrices and execution (journal CONF-EXP-001 to CONF-EXP-004).**

| Experiment | Question | Factors | Runs | Wall clock (s) | Failed |
| --- | --- | --- | --- | --- | --- |
| EXP-001 | Exposure diversity, static preferences | 5 rankers x eta {0, 0.2} x alpha_0 {1.0, 0.1}; plus bandit at alpha_ucb 0.1 | 480 | 904.6 | 0 |
| EXP-002 | Preference reinforcement, drifting preferences | 5 rankers x gamma {0.01, 0.05} x alpha_0 {1.0, 0.1}, eta 0.1; plus additive-then-clip drift check | 480 | 828.2 | 0 |
| EXP-003 | Sensitivity: catalog skew and choice sharpness | 3 rankers x catalog {uniform, Zipf} x tau {0.1, 0.3}, eta 0.1 | 240 | 252.2 | 0 |
| EXP-004 | Second test on MovieLens-derived inputs | 3 rankers, eta 0, tau 0.1 | 60 | 72.4 | 0 |

### 4.3 Data and calibration

Users and items in EXP-001 to EXP-003 are synthetic. MovieLens 1M (zip SHA-256 a6898adb...) enters in two ways, fixed before any rating was read (protocol section 15). Users with odd ids form a calibration half and users with even ids a held-out half. (a) Calibration: the target like rate L* = 0.577143 is the share of calibration-half ratings of 4 or more. The choice-curve midpoint c is fitted by bisection so that the mean like probability over the synthetic world of 20 calibration seeds equals L*, using the generators only (no ranker, no metric): c = 0.066421 for tau 0.1 and 0.005990 for tau 0.3. (b) EXP-004: preferences are p_u proportional to (n_uz + 1) / pi_ML,z, where n_uz counts a held-out user's ratings of 4 or more on movies of primary topic z; 200 of the 3,020 vectors are sampled per seed; the catalog follows pi_ML; c_ML = 0.061067 is fitted on the calibration half. The topics are the ten most frequent genres. `users.dat` is never read and no row-level data is committed.

### 4.4 Statistical analysis

For each contrast and metric: the mean paired difference over seeds, a 95% paired t-interval, a percentile bootstrap interval (10,000 resamples) as a check, the standardised effect d_z and the per-seed values. Holm adjustment is applied within each cell and metric family. The frozen decision rule supports H1 only if the upper bound of the t-interval is below 0 and the point estimate is at or below -0.05 (the smallest effect of interest). EXP-003's skew interaction uses a Welch interval because the two catalogs differ. Nonsignificance is never read as equivalence. The decision-rule code was committed before any confirmatory run (decision D-013).

### 4.5 Registration and deviations

The protocol and the four experiment protocols were frozen by the owner on 2026-11-24 (decision D-012), with SHA-256 hashes in `research/freeze.json`; a run guard refused any config that differed from the freeze record. There was no deviation from the frozen protocols during execution. Disclosed departures from an ideal record: the reproduction-command text of three protocols is outdated (freeze record); the experiment reports were written after the runs under an owner decision (D-015); and the M4 exploratory check (section 5.5) was designed after the confirmatory results were seen.

### 4.6 Exploratory work before the freeze

Before the freeze, exploratory runs on disjoint seeds used the planning midpoint c = 0.5, under which simulated users liked about 2% of what they saw. Under that calibration the EXP-001 primary contrast was -0.000688 (95% t [-0.002227, 0.000851], 10 seeds) and the Zipf cells of EXP-003 had the opposite sign (+0.102649 and +0.090614, 2 seeds). The owner approved recalibrating the choice curve to a stated target like rate with these values available (decisions D-008 and D-010). The recalibration was justified by the degenerate like rate, not by the effect size, but it was made by people who had seen the exploratory contrast. Section 5.5 measures what this choice implies.

### 4.7 Reproducibility and resources

All runs used Python 3.12.1 and numpy 2.3.5 on an Apple M1 Pro (macOS 15.3.1), one process per experiment, at most two in parallel, code revision f1838f3 with a clean tree. The 1,260 confirmatory runs took about 19.5 minutes against a 4-hour budget (Table 1). Commands, checksums and raw results are listed in section 10 and in each experiment's `reproduction.md`.

## 5. Results

Numbers in this section come from `research/experiments/EXP-00N/{verdict.json, contrasts.csv, summary.csv, tables.md}` and, for section 5.5, from `results/exploratory/m4-likerate-summary.csv`. Each is mapped in `research/publication/artifact_manifest.json`. Intervals are 95% paired t-intervals over 20 seeds unless stated.

### 5.1 EXP-001: exposure diversity under static preferences

H1 was supported in the primary cell and in all three secondary cells (Table 2, EXP-001-FIG-C01). Random ranking kept exposure close to the pool's topic entropy (H_exp 0.9932); similarity ranking reduced it to 0.5932.

**Table 2. EXP-001, similarity minus random in H_exp.**

| Cell | Mean | 95% t-interval | d_z | Frozen rule |
| --- | --- | --- | --- | --- |
| eta 0.0, alpha_0 1.0 (primary) | -0.4000 | [-0.4028, -0.3972] | -67.47 | H1 supported |
| eta 0.0, alpha_0 0.1 | -0.3938 | [-0.3963, -0.3913] | -74.54 | H1 supported |
| eta 0.2, alpha_0 1.0 | -0.3959 | [-0.3991, -0.3927] | -57.30 | H1 supported |
| eta 0.2, alpha_0 0.1 | -0.3948 | [-0.3974, -0.3922] | -71.96 | H1 supported |

**Table 3. EXP-001 primary cell, other contrasts (mean paired differences; Holm-adjusted p < 0.0001 unless stated).**

| Contrast | H_exp [95% t] | Gini | Relevance | Miscal. KL | Like rate |
| --- | --- | --- | --- | --- | --- |
| popularity - random | -0.0089 [-0.0115, -0.0064] | 0.7308 | 0.0003 (p 0.0022) | 0.0188 | 0.0003 (p 0.3289) |
| similarity - random | -0.4000 [-0.4028, -0.3972] | 0.1539 | 0.0603 | 0.1823 | 0.1283 |
| bandit - random | -0.2920 [-0.2950, -0.2891] | 0.1727 | 0.0536 | 0.1452 | 0.1151 |
| mmr - random | -0.1853 [-0.1873, -0.1834] | 0.0915 | 0.0503 | -0.1874 | 0.1077 |
| mmr - similarity | 0.2147 [0.2125, 0.2169] | -0.0624 | -0.0100 | -0.3697 | -0.0207 |

Three observations follow. First, the popularity ranker barely changed topic entropy (-0.0089, below the smallest effect of interest in every cell) while it concentrated item exposure most (Gini +0.7308): topic diversity and item concentration are different outcomes. Second, similarity ranking had the highest relevance and like rate, so in this model narrowing came with higher measured relevance. Third, MMR recovered 54% of the similarity loss (0.2147 of 0.4000; 45% to 54% across the four cells, supplementary Table S3) and lowered miscalibration below random, at a relevance cost of 0.0100. Every non-random ranker was less responsive to dislikes than random by the user-control metric (similarity +0.0120, MMR +0.0399), but that metric partly measures slate volatility (limitations 13). At the nested exploration level, LinUCB with alpha_ucb 0.1 had a lower H_exp than with 1.0 in all four cells (for example 0.6803 against 0.7012 in the primary cell; descriptive only).

### 5.2 EXP-002: preference reinforcement under drifting preferences

H1 was supported in all four cells (Table 4, EXP-002-FIG-C01). In the primary cell preference entropy rose under random ranking (+0.0971) and fell under similarity (-0.3379). The arms ranked as they did for exposure: similarity, bandit (-0.2796), MMR (-0.1754), popularity (+0.0636), random. MMR recovered 37% of the similarity contrast (MMR minus similarity +0.1626).

**Table 4. EXP-002, similarity minus random in Delta H_pref, and the drift-form check.**

| Cell | Mean | 95% t-interval | Frozen rule |
| --- | --- | --- | --- |
| gamma 0.05, alpha_0 1.0 (primary) | -0.4350 | [-0.4387, -0.4313] | H1 supported |
| gamma 0.01, alpha_0 1.0 | -0.4583 | [-0.4612, -0.4554] | H1 supported |
| gamma 0.01, alpha_0 0.1 | -0.4550 | [-0.4576, -0.4524] | H1 supported |
| gamma 0.05, alpha_0 0.1 | -0.4336 | [-0.4387, -0.4285] | H1 supported |
| Drift-form check, additive-then-clip, alpha_0 1.0 | -0.4363 | [-0.4400, -0.4326] | rule not met |
| Drift-form check, additive-then-clip, alpha_0 0.1 | -0.4351 | [-0.4402, -0.4300] | rule not met |

The registered drift-form check did not change the conclusion, but it is weak: for non-negative preferences, additive-then-clip followed by normalisation equals the multiplicative rule with rate gamma / (1 + gamma) unless the clip binds (limitations 12). It is close to a reparametrisation of gamma, so the result says little about other drift forms.

### 5.3 EXP-003: catalog skew and choice sharpness

Neither invalidation criterion was met and no sign reversal occurred (Table 5, EXP-003-FIG-C01). Under the Zipf catalog the random arm's entropy fell to 0.8601, but similarity fell further (0.3540 at tau 0.1), so the gap widened. A flatter choice curve (tau 0.3, refitted midpoint) changed the uniform-catalog gap only slightly.

**Table 5. EXP-003, similarity minus random in H_exp, skew interaction and MMR recovery.**

| Cell | Similarity - random [95% t] | MMR - similarity [95% t] |
| --- | --- | --- |
| tau 0.1, Zipf (primary) | -0.5060 [-0.5169, -0.4951] | 0.3669 [0.3597, 0.3741] |
| tau 0.1, uniform | -0.4001 [-0.4028, -0.3975] | 0.2150 [0.2126, 0.2174] |
| tau 0.3, uniform | -0.3861 [-0.3893, -0.3830] | 0.2306 [0.2274, 0.2338] |
| tau 0.3, Zipf | -0.5365 [-0.5469, -0.5260] | 0.4256 [0.4151, 0.4362] |
| Interaction Zipf - uniform, tau 0.1 (Welch) | -0.1059 [-0.1170, -0.0948] | |
| Interaction Zipf - uniform, tau 0.3 (Welch) | -0.1503 [-0.1611, -0.1396] | |

Under skew, MMR recovered more of the loss with no detectable relevance or like-rate cost in the tau 0.3 Zipf cell (relevance -0.0003 [-0.0015, 0.0008]), and similarity's miscalibration rose sharply (+1.1293 and +1.4988 nats). This verdict disagrees with the pre-freeze exploratory sweep (section 4.6), which section 5.5 examines.

### 5.4 EXP-004: MovieLens-derived preferences and catalog

H1 was supported (Table 6, EXP-004-FIG-C01): similarity lowered H_exp by 0.4095 relative to random, close to EXP-001's 0.4000. Seed-to-seed variation was larger (paired SD 0.0246 against 0.0059), so d_z was smaller (-16.64). MMR stayed much closer to random (-0.0864) and recovered 79% of the similarity loss (0.3230 of 0.4095) at a relevance cost of 0.0013. By the cross-experiment rule, the EXP-001 interpretation is not restricted to the synthetic preference generator.

**Table 6. EXP-004 contrasts (Holm-adjusted p < 0.0001 unless stated).**

| Metric | Similarity - random | MMR - random | MMR - similarity |
| --- | --- | --- | --- |
| H_exp | -0.4095 [-0.4210, -0.3980] | -0.0864 [-0.0911, -0.0817] | 0.3230 [0.3134, 0.3327] |
| Relevance | 0.0395 [0.0380, 0.0410] | 0.0382 [0.0370, 0.0393] | -0.0013 [-0.0019, -0.0007] (p 0.0002) |
| Miscal. KL | 0.7431 [0.6951, 0.7910] | -0.2157 [-0.2338, -0.1976] | -0.9588 [-1.0002, -0.9174] |
| Like rate | 0.0828 [0.0803, 0.0853] | 0.0812 [0.0791, 0.0833] | -0.0016 [-0.0029, -0.0003] (p 0.0221) |

### 5.5 Exploratory: dependence on the like rate (M4, post hoc, 5 seeds)

**This section is exploratory. It was designed after the confirmatory results were seen, uses 5 seeds, and never changes a frozen verdict.** It asks whether the confirmatory effects depend on the calibration choice disclosed in section 4.6. With the settings of EXP-003's tau 0.1 block (static, eta 0.1, alpha_0 1.0), the midpoint was refitted by the frozen calibration method for target true like rates from 0.05 to 0.85, plus the planning midpoint 0.5 (about 0.02), and crossed with the uniform and Zipf catalogs (160 runs, seeds 960001 to 960005, journal XPL-M4-LIKERATE).

**Table 7. Similarity minus random in H_exp by target like rate (exploratory; 95% t-interval over 5 seeds; FIG-M4-X01).**

| True like rate (target) | Uniform catalog | Zipf catalog |
| --- | --- | --- |
| 0.02 (planning midpoint 0.5) | -0.0032 [-0.0051, -0.0013] | +0.1045 [0.0925, 0.1165] |
| 0.05 | -0.0057 [-0.0077, -0.0038] | +0.1026 [0.0898, 0.1154] |
| 0.15 | -0.0384 [-0.0432, -0.0336] | +0.0724 [0.0572, 0.0875] |
| 0.30 | -0.2396 [-0.2473, -0.2318] | -0.1258 [-0.1479, -0.1038] |
| 0.45 | -0.3960 [-0.4058, -0.3863] | -0.3722 [-0.3994, -0.3450] |
| 0.577 (frozen calibration) | -0.3961 [-0.4046, -0.3877] | -0.5021 [-0.5195, -0.4847] |
| 0.70 | -0.3910 [-0.4009, -0.3811] | -0.6340 [-0.6464, -0.6215] |
| 0.85 | -0.3937 [-0.4080, -0.3795] | -0.7106 [-0.7247, -0.6965] |

At the frozen calibration the check reproduces the confirmatory values closely (-0.3961 against -0.4001; -0.5021 against -0.5060). Away from it the picture changes. Under the uniform catalog the similarity effect is below the smallest effect of interest at like rates of 0.15 or less and reaches a plateau near -0.39 from 0.45 upward. Under the Zipf catalog the sign reverses at like rates of 0.15 or less, with similarity ranking giving more diverse exposure than random, and the reduction grows with the like rate above 0.30. The observed like rates of the random arm matched the targets after allowing for the 10% feedback flips (`m4-likerate-summary.csv`).

## 6. Discussion

### 6.1 Expected and observed

**Table 8. Prediction, observation and frozen verdict for every registered test.**

| Test | Prediction (protocol) | Observation | Verdict under the frozen rule |
| --- | --- | --- | --- |
| EXP-001 primary | Similarity lowers H_exp vs random, expected by construction | -0.4000 [-0.4028, -0.3972] | H1 supported |
| EXP-001 other cells | Same contrast in each (eta, alpha_0) cell | -0.3938 to -0.3959 | H1 supported in all |
| EXP-001 secondary arms | Reported with Holm, no directional rule | Bandit -0.2920, MMR -0.1853, popularity -0.0089 | No frozen verdict; popularity practically null |
| EXP-002 primary | Similarity concentrates preferences more than random | -0.4350 [-0.4387, -0.4313] | H1 supported |
| EXP-002 other cells | Same contrast in each (gamma, alpha_0) cell | -0.4336 to -0.4583 | H1 supported in all |
| EXP-002 drift form | Dependence if sign changes or abs(D) < 0.05 | -0.4363 and -0.4351 | Not dependent (check weak, limitations 12) |
| EXP-003 skew | Gap might shrink; restrict to balanced pools if criterion met | Gap widened: -0.5060, -0.5365 | Criterion not met; no sign reversal |
| EXP-003 sharpness | Effect might weaken at tau 0.3 | -0.3861 (uniform), -0.5365 (Zipf) | Criterion not met |
| EXP-003 interaction | Not directional | -0.1059 and -0.1503 (Welch) | Reported, no rule |
| EXP-004 primary | Contrast might shrink with heterogeneous real preferences | -0.4095 [-0.4210, -0.3980] | H1 supported; not restricted to the synthetic generator |

Two observations were not anticipated in the protocol: preferences spread under random ranking in EXP-002, and skew enlarged rather than shrank the EXP-003 gap. Both are reported as measured properties of this model.

### 6.2 Competing explanations

The protocols named competing explanations in advance. Their status after the confirmatory results and the M4 check is as follows (full table in `research/publication/interpretation_m4.md`).

- **Candidate-pool composition rather than the objective.** Addressed within a seed by common random numbers (pools identical across arms) and across catalogs by EXP-003 and EXP-004. At the frozen calibration the effect survives skew. The M4 check shows that the direction under skew depends on the like rate, so pool composition and calibration interact.
- **Feedback noise and initial concentration.** Varied as factors in EXP-001 and EXP-002 without changing any verdict (range -0.3938 to -0.4000 in EXP-001). Under drift, the like rate of the random arm was 0.5668 at gamma 0.05 at both alpha_0 levels, whereas under static preferences it differed by alpha_0 (0.5770 and 0.5482 at eta 0). This is consistent with drift overwriting most of the initial preference within 200 steps; that reading is a hypothesis, not tested here.
- **Choice-model sharpness.** EXP-003 at tau 0.3 did not remove the effect. Sharpness was varied at a matched like rate, so this test does not address the like rate itself.
- **Calibration (like rate), not named in the protocols.** This is the explanation the confirmatory design could not address, because one midpoint per tau was fixed at the freeze. The M4 check (exploratory, 5 seeds, one setting of tau, eta and alpha_0) suggests it matters more than any registered factor: under the uniform catalog the similarity effect stayed below the smallest effect of interest at like rates of 0.15 or less and was clearly present from 0.30 upward. The threshold lies somewhere between those two levels and was not located. A plausible mechanism, untested here, is that when most feedback is negative the similarity profile is dominated by subtracted embeddings and steers slates away from disliked topics rather than toward liked ones; under a skewed catalog it is pushed away from the abundant topic, which raises entropy.
- **Drift functional form.** Not addressed: the registered check is close to a reparametrisation (limitations 12).
- **Implementation artefacts.** The test suite (153 tests when the confirmatory runs were made) covers ties, feedback updates, seed determinism, topic distributions and zero-feedback behaviour; the random arm's H_exp stayed close to the pool topic entropy in every experiment (for example 0.9932 against 0.9983 in EXP-001 and 0.9088 against 0.9139 in EXP-004); the M4 audit recomputed every contrast from the raw files independently of the analysis code.

### 6.3 Implications

Within this model, three statements are supported. At the calibrated like rate, a ranker that personalises on topic similarity narrows topic exposure strongly (confirmatory); the exploratory check indicates this requires simulated users to like a substantial share of what they see. Item popularity and topic diversity are distinct: a popularity ranker can concentrate item exposure while leaving topic exposure almost unchanged. Diversity-aware re-ranking recovered part of the similarity loss with small relevance costs: in exposure entropy, 0.2147 of 0.4000 in EXP-001 and 0.3230 of 0.4095 in EXP-004; in preference concentration, 0.1626 of 0.4350 in EXP-002. The magnitudes are properties of this simulation: a single primary topic per item, slates of 10 from pools of 50, one examination model and one calibration per experiment. They are not estimates for any real system.

## 7. Limitations and threats to validity

The full list is `research/limitations.md` (items 1 to 18). The most consequential are:

- **Simulation only.** Users and items are synthetic or constructed from aggregates. Nothing here measures real people, real platforms, attention or addiction, and no claim is made that any platform uses these rankers.
- **Calibration dependence.** Every confirmatory result holds at one fitted midpoint per tau. An exploratory check shows the main effect near zero at low like rates and reversed in sign under skew (section 5.5). The target like rate itself comes from MovieLens ratings of movies that users chose to watch, so it is a selected-exposure like rate, not a like rate under random exposure (limitations 9, 15 to 17).
- **Expected direction.** The primary direction was expected by construction; the informative parts are the effect sizes, trade-offs and boundary conditions.
- **Construct validity.** H_exp counts only an item's primary topic. User control mixes responsiveness and slate volatility. Relevance uses a latent utility that no real system observes. The drift-form check is weak. The miscalibration formula has been checked only against a secondary source, not against Steck (2018).
- **Statistical.** Seed-level variance is small (paired SDs about 0.006 to 0.025), so large d_z values and tiny p-values follow even for practically null contrasts such as popularity; the smallest effect of interest is the relevant threshold. EXP-004's seeds resample one pool of 3,020 vectors, so inference is conditional on that population.
- **Post hoc analysis.** Section 5.5 was designed after the results and has 5 seeds per cell. Its role is to bound the confirmatory interpretation, not to establish a new finding.
- **Calibration chosen with an exploratory null in view.** The recalibration that produced a moderate like rate was approved after a pre-freeze exploratory run showed a near-zero primary contrast under the planning midpoint (section 4.6). The stated reason was the degenerate like rate (about 0.02), and the method was written before the fit, but a reader may reasonably treat the choice of calibration regime as a researcher degree of freedom. Section 5.5 makes its consequence explicit.

## 8. Ethics and responsible research

No human participants were involved and no data was collected. MovieLens 1M was used under its research licence: no redistribution, no commercial use, acknowledgement given, demographics never read, and only aggregates committed. Simulated agents are not participants and their behaviour is not evidence about people. The study does not build or evaluate an engagement-maximising system. A misuse risk is that the narrowing result is read as advice on how to narrow exposure deliberately; the results are reported with the diversity-aware alternative and its costs to reduce that risk. No ethics approval was needed or claimed.

## 9. Conclusion and future work

In a matched-pool simulation, content-similarity ranking reduced topic exposure entropy by about 0.40 normalised units relative to random ranking, with synthetic or MovieLens-derived preferences, and concentrated drifting simulated preferences by a similar amount. Diversity-aware re-ranking recovered much of the loss. These results hold at the calibrated like rate of 0.577; an exploratory check indicates that, under the settings it covered, the exposure effect falls below the smallest effect of interest at low like rates and reverses in direction under a skewed catalog. The defensible conclusion is conditional: in this model and at this calibration, similarity ranking narrows exposure; whether it does so at other like rates is an open, exploratory question.

Feasible extensions, each a new experiment that would need its own frozen protocol: a confirmatory test of the like-rate dependence with more seeds and a registered threshold (registered as EXP-005 on 2026-11-25; not frozen, not run, no data); a structurally different drift rule (for example drift toward exposed rather than liked topics); multi-topic items; and the embedding noise sigma_item, which controls how sharply a similarity profile concentrates.

## 10. Data, code and artifact availability

Repository (local; public URL: [to be added by the owner on release]): configs in `experiments/`, raw run files in `results/raw/EXP-00N/runs/` with SHA-256 checksums in `research/experiments/EXP-00N/run_manifest.json`, analysis outputs and figures in `research/experiments/EXP-00N/`, exploratory outputs in `results/exploratory/`, and the evidence manifest in `research/publication/artifact_manifest.json`. Reproduction:

```
uv sync --frozen --all-groups --all-extras
PYTHONPATH=src .venv/bin/python -m pulse.cli run --experiment EXP-00N
PYTHONPATH=src .venv/bin/python scripts/analyse_experiment.py EXP-00N
PYTHONPATH=src .venv/bin/python scripts/m4_evidence_audit.py
```

An offline interactive page in `demo/` shows the same results, copied from the committed result files by `scripts/export_demo_data.py` and printed exactly as in this manuscript (checked by `tests/test_demo_export.py`), together with a labelled sandbox that is illustrative and not the research engine.

EXP-004 needs the MovieLens files, regenerated by `scripts/download_movielens.py` and `scripts/prepare_movielens.py` and checked by SHA-256. The MovieLens data is not redistributed. The code is source-available under a non-commercial licence (`LICENSE`), not open source.

## 11. Funding, competing interests and AI assistance

No funding. No competing interests. An AI system (Claude, Anthropic) acted as research and development assistant: it drafted protocols, code, analyses, reports and this manuscript under the owner's direction. The owner approved the protocols, the freeze and every recorded decision. Verification performed: a test suite of 153 tests at the time of the confirmatory runs (177 at the M6 release candidate), a run guard against the freeze record, an independent recomputation of every contrast from the raw files and a trace of every decimal number in the manuscript and reports to a committed result (`research/publication/evidence_audit.md`). This AI review is internal quality control, not external peer review.

## References

- Carbonell, J. and Goldstein, J. (1998). The use of MMR, diversity-based reranking for reordering documents and producing summaries. SIGIR 1998, pp. 335 to 336. doi:10.1145/290941.291025 (pages from the author PDF; DOI from search results, unverified).
- Chaney, A. J. B., Stewart, B. M. and Engelhardt, B. E. (2018). How algorithmic confounding in recommendation systems increases homogeneity and decreases utility. RecSys 2018. arXiv:1710.11214; doi:10.1145/3240323.3240370.
- da Silva, D. C. and Jannach, D. (2025). Calibrated recommendations: survey and future directions. arXiv:2507.02643 (secondary source, used only to check the Steck formula).
- Harper, F. M. and Konstan, J. A. (2015). The MovieLens datasets: history and context. ACM Transactions on Interactive Intelligent Systems 5(4). doi:10.1145/2827872 (author preprint opened; volume, issue and DOI from the GroupLens README).
- Ie, E. et al. (2019). RecSim: a configurable simulation platform for recommender systems. arXiv:1909.04847.
- Jiang, R., Chiappa, S., Lattimore, T., Gyorgy, A. and Kohli, P. (2019). Degenerate feedback loops in recommender systems. AIES 2019. arXiv:1902.10730; doi:10.1145/3306618.3314288.
- Kalimeris, D., Bhagat, S., Kalyanaraman, S. and Weinsberg, U. (2021). Preference amplification in recommender systems. KDD 2021. doi:10.1145/3447548.3467298.
- Li, L., Chu, W., Langford, J. and Schapire, R. E. (2010). A contextual-bandit approach to personalized news article recommendation. WWW 2010. arXiv:1003.0146; doi:10.1145/1772690.1772758.
- Lucherini, E., Sun, M., Winecoff, A. and Narayanan, A. (2021). T-RECS: a simulation tool to study the societal impact of recommender systems. arXiv:2107.08959.
- Mansoury, M., Abdollahpouri, H., Pechenizkiy, M., Mobasher, B. and Burke, R. (2020). Feedback loop and bias amplification in recommender systems. arXiv:2007.13019.
- Steck, H. (2018). Calibrated recommendations. RecSys 2018, pp. 154 to 162. doi:10.1145/3240323.3240372 (metadata only; full text not opened).

## Supplementary appendix

See `research/paper/supplementary.md`: the complete matrix, configurations and hashes, extended tables, robustness results, report links and the list of deviations and owner decisions.
