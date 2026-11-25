<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
<!-- Draft for the owner. Not published. Every number is copied from research/paper/manuscript.md (version 0.2). -->

# When a simulated feed learns what you like, exposure narrows, but only under some conditions

*Draft article. By [author line to be added by the owner]. A simulation study; not peer-reviewed.*

Recommender systems decide what we see, and what we see shapes the feedback they learn from. Several simulation studies have argued that this loop can narrow what people are shown. I wanted to know how much of that narrowing belongs to the ranking objective itself, so I built a small, preregistered simulation in which five rankers face exactly the same simulated users, items and candidate pools.

Everything below is a simulation. Users and items are synthetic or built from aggregate MovieLens data; nothing here measures real people, attention or addiction, and nothing here says what any real platform does.

## The question

How do ranking objectives influence exposure diversity and simulated preference reinforcement when all rankers receive identical candidate pools?

## The set-up

Two hundred simulated users each see a slate of 10 items, chosen from a pool of 50, for 200 steps. Every item belongs mainly to one of ten topics. Users examine the top of the slate more often than the bottom and like an item with a probability that rises with how well it fits their preferences; some feedback is flipped as noise. Five rankers compete: random, popularity, content similarity, a LinUCB bandit and maximal marginal relevance (MMR), a diversity-aware re-ranker. For a given seed they all receive the same pools and the same random draws, so a difference between them comes from the ranker.

The main outcome is exposure topic entropy over the last 50 slates: 1 means a user's slates spread evenly over all ten topics, and lower values mean narrower exposure. The questions, metrics, seeds and decision rules were frozen before any confirmatory run, and the analysis code was committed before the data.

**Figure idea (caption and alt text).** *Caption:* "Exposure topic entropy by ranker in EXP-001 (simulated; mean and SD over 20 seeds)." *Alt text:* "A heatmap with five rankers as rows and four settings as columns; random ranking stays at 0.9932 in every column, while content similarity is the darkest row, between 0.5932 and 0.5994."

## What was measured

- **Static preferences (EXP-001).** Content similarity lowered exposure topic entropy by 0.4000 relative to random ranking (95% interval [-0.4028, -0.3972], 20 paired seeds). Random ranking kept exposure close to the pool's own topic mix (0.9932); similarity reduced it to 0.5932.
- **Drifting preferences (EXP-002).** When simulated preferences drift toward liked topics, similarity concentrated them by 0.4350 relative to random ([-0.4387, -0.4313]). Under random ranking preferences actually spread.
- **A skewed catalog (EXP-003).** With a Zipf-skewed catalog the gap widened instead of closing: -0.5060 ([-0.5169, -0.4951]).
- **Real-data-derived inputs (EXP-004).** With preferences and catalog weights built from MovieLens 1M aggregates, the reduction was 0.4095 ([-0.4210, -0.3980]).
- **A null result.** The popularity ranker barely changed topic entropy (-0.0089 [-0.0115, -0.0064], below the smallest effect of interest of 0.05), even though it concentrated exposure on a few items more than any other ranker. Topic diversity and item concentration are different things.
- **A partial remedy.** MMR re-ranking recovered between 45% and 79% of the exposure-entropy loss across settings, at a small cost in relevance.

## The result that changes the reading

All of those results hold at one calibration: simulated users like a little more than half of what they see (a like rate of 0.577, fitted to MovieLens ratings). After the confirmatory results, I ran an exploratory check, designed post hoc with 5 seeds, that varied this like rate. When simulated users like only 2% of what they see, the similarity effect almost vanishes under a uniform catalog (-0.0032 [-0.0051, -0.0013]) and reverses under a skewed catalog (+0.1045 [0.0925, 0.1165]), where similarity ranking gives more diverse exposure than random.

**Figure idea (caption and alt text).** *Caption:* "Similarity minus random in exposure entropy against the like rate (exploratory, 5 seeds)." *Alt text:* "Two lines against the like rate: the uniform-catalog line starts near zero and levels off near -0.39; the Zipf-catalog line starts above zero and falls to -0.7106."

So the defensible conclusion is conditional: in this model and at this calibration, similarity ranking narrows exposure strongly. Whether it does so at other like rates is an open question. A confirmatory test of it is registered as EXP-005, but it has not been frozen or run, and there are no results from it.

## Limitations

- It is a simulation; synthetic agents are not people.
- The direction of the main effect was expected by construction; the effect sizes, trade-offs and boundary conditions are the informative parts.
- The calibration was chosen after an exploratory run under another calibration had shown a near-zero effect; the exploratory check above makes the consequence of that choice visible.
- "User control" and "relevance" are narrow, model-internal measures.

## Reproduce it

Code, configs, raw run files, checksums, the manuscript and the experiment reports are in the repository: [repository link to be added by the owner on release]. An offline interactive page lets you run two simulated feeds side by side; its sandbox is illustrative, not the research engine: [demo link to be added by the owner on release].

*AI assistance: an AI system (Claude, Anthropic) acted as a research and development assistant under the owner's direction; it is not an author.*
