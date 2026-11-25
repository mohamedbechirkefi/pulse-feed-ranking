<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
<!-- Draft for the owner. Not published. Every number is copied from research/paper/manuscript.md (version 0.2). -->

Does a feed that learns what you like narrow what you see? In a simulation, yes, but only under some conditions.

I built PULSE, a small preregistered simulation in which five ranking objectives (random, popularity, content similarity, a bandit and diversity-aware MMR) rank for the same simulated users, items and candidate pools, so any difference comes from the ranker.

One defensible finding: at the calibrated like rate, content-similarity ranking lowered exposure topic entropy by 0.4000 relative to random ranking (95% interval [-0.4028, -0.3972], 20 paired seeds), and MMR re-ranking recovered between 45% and 79% of that loss across settings.

The caveat matters as much as the finding: an exploratory check found the effect near zero when simulated users like few of the items they see, and reversed under a skewed catalog. A confirmatory test of that boundary is registered but not yet run. This is a simulation; it says nothing about real people or any real platform.

Paper draft, reports and code: [repository link to be added by the owner on release]
Interactive page: [demo link to be added by the owner on release]
