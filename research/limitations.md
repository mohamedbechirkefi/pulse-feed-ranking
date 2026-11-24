<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# Limitations (living document; updated at the freeze, 2026-11-24, before any confirmatory result)

1. **Simulation only.** Users and items are synthetic. Results hold only within the generative assumptions of `research/protocol.md`. They are not evidence about real people or any real platform.
2. **No claims about commercial systems.** PULSE does not claim that any platform uses these rankers or produces these effects.
3. **No measurement of addiction or wellbeing.** Attention is represented only by a position-based examination probability. Nothing here measures compulsive use.
4. **Drift is an assumption.** The drifting preference model encodes reinforcement by construction; EXP-002 measures how rankers interact with that assumption, not whether people drift.
5. **Narrow operationalisations.** "User control" is responsiveness of slates to explicit dislikes; it is not human agency. "Calibration" follows a KL definition between latent preference and exposure.
6. **Simple rankers.** No learned embedding model, no deep or RL ranker beyond LinUCB.
7. **Expected primary direction.** The primary contrast is expected by construction; the informative parts are effect size, trade-offs and the sensitivity analysis.
8. **Licence.** The repository is source-available under a non-commercial licence (D-001), not open source; reuse is restricted accordingly.
9. **MovieLens selection (round-2 data).** The target like rate L* comes from ratings of movies that users chose to watch, so it is a selected-exposure like rate. It is used as a stated calibration target, not as a measured like rate under random exposure (protocol section 15.4).
10. **Constructed preferences in EXP-004.** Preference vectors are derived from like counts by add-one smoothing and division by the catalog share of each genre; genres are reduced to one primary topic per movie. EXP-004 tests the simulation on these inputs, not on MovieLens users' behaviour. MovieLens users are not participants.
11. **One midpoint per tau.** The fitted midpoint is held fixed across alpha_0, eta, pool skew and drift, so like rates differ by cell.
