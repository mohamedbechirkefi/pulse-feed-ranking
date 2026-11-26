<!-- SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0 -->
# PULSE demo: design plan

Owner request of 2026-11-26: a page that is recognisably its own product, with motion and a premium
finish. This file is the plan written before the build, then reviewed and revised.

## Subject, audience, job

- **Subject.** A simulation study of how five ranking objectives change the topics a feed shows. The
  finding is a narrowing: under content-similarity ranking, a slate that started with many topics ends
  with few, compared with random ranking, at one calibrated like rate.
- **Audience.** A curious technical reader, an admissions committee reading quickly, a researcher who
  wants the intervals and the limits.
- **Primary job.** Show the question and the conditional answer in one screen, then let the reader
  check every number against the evidence and try two feeds in the sandbox.

## Direction: the broadcast control room

A feed is a programme schedule. The page is the gallery of a small broadcast studio at night: a wall
of channel strips, each slot of a slate lit in its topic colour, and an operator console below. The
narrowing is shown the way a vision mixer would see it: many channel colours on the monitor wall, then
one hue taking over as similarity ranking wins the schedule.

## Colour (dark only; the control room is a dark room)

| Name | Hex | Role |
| --- | --- | --- |
| Gallery | `#0F1B2A` | page background, a deep blue slate (not near-black) |
| Rack | `#18293C` | panels, console surfaces |
| Phosphor | `#E9EEF2` | body text |
| Fader | `#A3B3C2` | secondary text, ticks, captions |
| Cue | `#7CC0FF` | feed A, links, focus ring |
| Tally | `#FF7466` | feed B, the on-air lamp, the narrowed channel |

The ten topic hues are data colours, not brand colours: a spectrum tuned for the dark gallery, used only
where a topic is shown (monitor wall, feed cards). Label kinds keep separate lamp colours and outlines
(solid, dashed, dotted) so they never rely on colour alone.

## Type

- **Archivo Variable** (wdth 62 to 125, wght 100 to 900), display and interface: condensed widths for
  headings and the wordmark, like broadcast lower thirds; normal width for controls, labels and tabular
  figures in tables.
- **Source Serif 4 Variable** (wght), long-form reading: the verdicts, captions and method prose, at
  18 px with a line height of 1.65 on the dark ground.

## Layout

Left-aligned, one reading column under 72 characters, widening only for the monitor wall, the tables
and the sandbox console.

```
+------------------------------------------------------------------+
| [mark] Pulse            Result  Evidence  Sandbox  Limits  Repro  |  sticky, compact
+------------------------------------------------------------------+
| A recommender simulation study                                    |
| What happens to exposure when a feed learns what you like?        |
| answer in one sentence (conditional)                              |
|                                                                   |
| +--------------------------------------------------------------+ |
| | MONITOR WALL: 24 steps x 10 slate slots, topic colours        | |
| | [ Random ranking | Content similarity ]   Illustration label  | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
| Key result: exposure meters, EXP-001 primary cell (measured)      |
|   Random        |=============================| 0.9932 (0.0009)   |
|   Similarity    |==================           | 0.5932 (...)      |
+------------------------------------------------------------------+
| Overview, label legend                                            |
| Published results: one console panel per experiment              |
| Figures: heatmap, like-rate boundary                              |
| Sandbox console: controls strip, two feeds side by side          |
| Assumptions / Method and limitations / Reproduce                  |
| Footer: links, licence, AI use, font credits                      |
+------------------------------------------------------------------+
```

## Motion

- **The one orchestrated moment (hero).** The monitor wall lights column by column, left to right, as a
  playhead sweeps (random topics, 35 ms stagger). A beat later the schedule switches to content
  similarity: a second sweep crossfades each column toward one hue, stronger with every step, and the
  segmented indicator slides to "Content similarity". It is labelled "Illustration, not study data" and
  shows no number. Reduced motion: the final similarity state, no sweep.
- **Motion that answers actions.** The segmented control re-runs the crossfade sweep (opacity only) and
  its indicator slides (transform). The exposure meters fill once when scrolled into view (scaleX). The
  heatmap and like-rate chart reveal once on entry (opacity, clip-path). Sandbox: a progress bar that
  scales with the worker's progress, and the new feeds settle in with a 40 ms stagger once per run. The
  step slider, which a visitor drags many times, has no animation.
- Strong ease-out `cubic-bezier(0.23, 1, 0.32, 1)`; UI motion 150 to 250 ms; hover motion only under
  `(hover: hover) and (pointer: fine)`; no `transition: all`; every animation has a reduced-motion
  variant (none or opacity only).

## The one memorable thing

The monitor wall turning from many channel colours to one: the study's finding as a picture, and the
same idea drawn in the logo (three segments, then two, then one bar).

## Review against the frontend-design tells and the other demos

- First draft used a near-black ground with a single red "on air" accent. That is the near-black plus
  one acid accent tell. Revised: the ground is a blue slate (`#0F1B2A`), and colour comes from the ten
  topic hues on the monitor wall, with cue blue and tally coral as a pair for the two feeds.
- First draft put an all-caps tracked eyebrow above every section and kept the uppercase label tags.
  Revised: sentence case everywhere; label kinds are lamp-and-outline pills in sentence case.
- First draft used a monospace face for numbers. Revised: tabular figures of Archivo; no mono.
- First draft chopped results into identical rounded cards. Revised: experiment panels are console
  modules with a lamp strip on the left whose style encodes the label kind (solid, dashed, dotted);
  radius differs by level (console 14 px, controls 10 px, lamps round).
- No fade-up per section: only the monitor wall plays on its own; everything else moves once, on entry
  or in answer to an action.
- Against the other demos: SCROLL is a stopwatch and film strip, SWARM a dusk murmuration, MARKET a
  ticker tape, ECHO a record sleeve. PULSE keeps the vision-mixer grid of topic colours and the
  lower-third condensed type, which none of them uses.

## Changes made during the build (screenshot critique)

- Pass 1 (desktop 1440 and phone 390): sections had lost their top spacing because `.wrap` padding overrode the
  section padding (selector fixed); the like-rate series reveal used `clip-path` on SVG groups and stayed hidden,
  replaced by an opacity reveal; the sandbox exposure heatmap drew larger shares brighter on the dark ground, which
  contradicted its caption ("darker cells mean a larger share"), so it now sits on a light plate with dark cells.
- Pass 2: the segmented control used a filled indicator with dark text, which the contrast check reads against the
  gallery; the indicator is now a tinted plate with a cue or tally underline and the label stays light. The
  reproduction commands no longer wrap mid-command on phones (scrollable, keyboard-focusable region). Removed one
  accessory: the repeated lockup in the footer (the logo appears once, in the top bar).
- Heatmap cells reveal from 20% opacity rather than zero, so the numbers are never fully hidden if the observer
  does not fire.
