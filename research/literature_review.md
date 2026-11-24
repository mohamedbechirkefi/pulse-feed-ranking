<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Literature review (M0, preliminary, not systematic)

Searches: WebSearch and WebFetch on 2026-11-24. This is a targeted scan, not a systematic review. "Opened" means the arXiv abstract page, publisher metadata or author PDF was fetched on that date; only those are cited. Claims below describe what the opened page states, not a full reading of each paper.

## Sources opened

| Key | Source | Identifier | What was opened (2026-11-24) | Relevance |
| --- | --- | --- | --- | --- |
| chaney2018algorithmic | Chaney, Stewart, Engelhardt. How Algorithmic Confounding in Recommendation Systems Increases Homogeneity and Decreases Utility. RecSys 2018 | arXiv:1710.11214; doi:10.1145/3240323.3240370 | arXiv abstract page | Simulation showing training on recommendation-confounded data homogenises user behaviour without improving utility. Closest prior simulation result. |
| jiang2019degenerate | Jiang, Chiappa, Lattimore, Gyorgy, Kohli. Degenerate Feedback Loops in Recommender Systems. AIES 2019 | arXiv:1902.10730; doi:10.1145/3306618.3314288 | arXiv abstract page | Formalises degeneracy of user interest; distinguishes echo chamber and filter bubble; studies exploration, model accuracy and pool growth with bandit simulations. |
| kalimeris2021preference | Kalimeris, Bhagat, Kalyanaraman, Weinsberg. Preference Amplification in Recommender Systems. KDD 2021 | doi:10.1145/3447548.3467298 | author PDF, first page (abstract) | Users drift toward recommended content in a matrix-factorisation model; conditions for amplification; mitigation. Basis for EXP-002's drift assumption. |
| mansoury2020feedback | Mansoury, Abdollahpouri, Pechenizkiy, Mobasher, Burke. Feedback Loop and Bias Amplification in Recommender Systems | arXiv:2007.13019 | arXiv abstract page | Offline simulation: feedback loops amplify popularity bias, reduce aggregate diversity, homogenise users. Motivates the popularity arm and the Gini metric. |
| ie2019recsim | Ie et al. RecSim: A Configurable Simulation Platform for Recommender Systems | arXiv:1909.04847 | arXiv abstract page | Simulation as configurable assumptions about user state, preferences and choice. |
| lucherini2021trecs | Lucherini, Sun, Winecoff, Narayanan. T-RECS | arXiv:2107.08959 | arXiv abstract page | Open-source simulator for societal impact studies; replicates prior simulations. |
| li2010contextual | Li, Chu, Langford, Schapire. A Contextual-Bandit Approach to Personalized News Article Recommendation. WWW 2010 | arXiv:1003.0146; doi:10.1145/1772690.1772758 | arXiv abstract page | LinUCB; the bandit arm. |
| carbonell1998mmr | Carbonell, Goldstein. The Use of MMR, Diversity-Based Reranking. SIGIR 1998 | doi:10.1145/290941.291025 (DOI from search results, unverified) | author PDF (2 pages), first page | Maximal marginal relevance; the diversity-aware arm. |
| steck2018calibrated | Steck. Calibrated Recommendations. RecSys 2018, pp. 154 to 162 | doi:10.1145/3240323.3240372 | OpenAlex metadata only; full text not opened | Calibration as proportional representation of interests; KL miscalibration metric. The exact formula must be checked against the paper before M2 (open item). |

## Unverified (not cited as read)

- MIND dataset licence terms (Microsoft Research License Terms): known only from search summaries.
- Harper and Konstan 2015, MovieLens history paper: citation copied from the GroupLens README; paper not opened.

## Known work and narrow contribution (draft)

Prior simulations already show homogenisation, popularity-bias amplification and preference amplification. PULSE does not claim a new phenomenon. Its intended contribution is narrow and methodological: a small, fully reproducible, matched-candidate-pool comparison of five standard ranking objectives under static and drifting preference assumptions kept strictly separate, with pre-registered metrics (exposure entropy, concentration, relevance, calibration, responsiveness to negative feedback), seed-level uncertainty, and a pre-registered sensitivity analysis that could restrict the interpretation. Novelty is not claimed; a fuller search (for example of RecSys simulation-reproducibility work) is an M1 task.

## Open items for M1

1. Open the Steck 2018 full text and confirm the miscalibration formula.
2. Search for prior matched-pool comparisons of MMR against similarity rankers in simulation.
3. Search for critiques of recommender simulation methodology (the T-RECS group is reported to have one; not yet located).
