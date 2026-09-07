# Wave 2 — beyond exhaustion: annealing and generator programs

Wave 1 exhausted n <= 10 with no candidates. The three WOWII conjectures that *are* known
to be false have counterexamples at n = 11, 13 and 18, so the interesting range starts
exactly where exhaustive enumeration stops. Wave 2 is about getting there.

## The positive control, and why it mattered

Before believing any "flat" result from a heuristic search, the search has to be shown
capable of finding something. Two already-refuted conjectures from the same family were
used as positive controls: **194** (published 18-vertex counterexample) and **200**
(published 11-vertex counterexample `J??FFBRq}N_`). Their objectives were implemented in
the same searcher as the ten open ones.

### Attempt 1 — simulated annealing over arbitrary graphs: FAILED the control

`mine/tools/wowclimb.c`, hill-climbing on `lhs - rhs` with single-edge-flip moves, found
neither control at n = 11 or n = 13, across restarts totalling ~360k steps.

The diagnosis is worth recording because it is the exact class of bug that turns a tooling
failure into a false "the conjecture looks true": the initialiser seeded each restart from
a **random spanning path**, which by construction gives the graph a Hamiltonian path — and
both controls are non-traceable graphs. The counterexamples were unreachable *by
construction*, and the search would have reported "flat" forever.

Fixed by seeding from a random attachment **tree** instead. Logged to
`mine/memory/negative.jsonl`.

### Attempt 2 — generator programs: PASSED the control

Rather than search the space of objects, enumerate a parameterised family of *constructions*
(`mine/tools/genfamilies.py`) — the "evolve generator programs, not objects" rung of the
ladder, done exhaustively over a small parameter grid. The shape is taken from how the
published counterexamples are actually built: a dense core (K_q, K_q minus an edge, K_q
minus a perfect matching, a cycle, a path), plus apex vertices joined to the whole core,
plus an optional vertex joined to two core vertices, plus pendant vertices.

Over 13,448 distinct graphs with n <= 18, this generator **rediscovered counterexamples to
both controls** — 20 members violating conjecture 200 and 1 violating conjecture 194.
One of them was handed to the frozen checker:

```
$ bash scripts/check-freeze.sh
VERIFIER INTACT (40 files)
$ python3 mine/verify/checkers/check_wow2_200.py /tmp/ctrl200.json     # graph6 J^~~u?_C?O?
{"ceil_1_plus_l_avg": "4", "has_hamiltonian_path": "False", "hypothesis_holds": "True",
 "l_avg": "24/11", "n": "11", "tree": "4"}
ACCEPT: the conjecture's conclusion FAILS on this witness while its hypotheses HOLD
exit=0
```

The recomputed invariants (`l_avg = 24/11`, `tree = 4`) match the values published in the
`GraphConjecture200.lean` module docstring exactly. **This is not a new result** —
conjecture 200 was already refuted — it is the end-to-end demonstration that the
generator, the frozen checker, and the tiering actually work on a case whose answer is
independently known.

## Results against the ten OPEN conjectures — negative

| search | scope | candidates |
|---|---|---|
| structured generator families | 13,448 graphs, n <= 18, 5 core shapes x apexes x pendants | 0 |
| simulated annealing (post-fix) | n = 10..13, all ten objectives | 0 |

## Reproduction

```
python3 mine/tools/genfamilies.py 18 | grep '^[A-Za-z~]' > /tmp/fam.g6
./mine/tools/wowscan < /tmp/fam.g6                       # 0 candidates for the ten open
./mine/tools/wowclimb --eval 200 'J^~~u?_C?O?'           # objective 1 = control found
```

## Honest reading

The generator finds the *known* counterexamples of this shape and finds nothing for the ten
open conjectures within n <= 18. That is a real, if narrow, negative: it says the open ten
have no counterexample of the "dense core + apexes + pendants" shape at that size. It says
nothing about other shapes, and the parameter grid is small — 13,448 graphs is a rounding
error next to the space of graphs on 18 vertices.

## A second generator family — and why its negative is worth less

`mine/tools/genfamilies2.py` widens the program space along the axes the first generator
leaves out: attachments that are paths of length 2 rather than single pendants, two cores
joined by an edge or a path (the objectives involve radius and diameter, which a single
dense core keeps artificially small), complete-bipartite and cycle cores. 7,460 distinct
graphs with n <= 18.

Result against the ten open conjectures: **0 candidates**.

But this generator **does not pass the positive control** — neither the conjecture-194 nor
the conjecture-200 counterexample lies in its parameter grid. So unlike the first
generator, a negative from this one is only weak evidence: it shows nothing was found, not
that something findable would have been found. Recorded here rather than presented
alongside the validated negative, because the difference between "searched and found
nothing" and "searched with an instrument known to detect this kind of thing and found
nothing" is the whole difference between a measurement and a guess.

## Annealing arm-by-arm: which inequalities are tight, and which have slack

`mine/tools/wowclimb` maximises `lhs - rhs` (scaled by n, so an objective of `-11` at
n = 11 means the inequality holds with slack exactly 1). 25 restarts x 20,000 steps per
arm, seeded from random attachment trees (the post-positive-control initialiser).
Raw log: `climb_results.log`.

| conjecture | best objective, n = 11..14 | reading |
|---|---|---|
| 19 | 0, 0, 0, 0 | **tight**: equality is achieved at every order tried |
| 40 | 0, 0, 0, 0 | **tight** |
| 61 | 0, 0, 0, −14 | tight up to n = 13; at n = 14 the search only reached slack 1 |
| 133 | 0, −12, −13 | tight at n = 11, slack 1 above it |
| 100 | −11, −12, −13, −14 | **slack 1 everywhere** — never reaches equality |

This is the most useful thing the annealer produced, and it is not a "flat arm" result in
the useless sense. An objective that climbs to exactly 0 and stops says the bound is
**sharp**: extremal graphs exist, the search finds them, and it cannot get past them. An
objective that never reaches 0 (conjecture 100) says the bound is not even tight in this
range — the search is not close, and the conjecture has room to spare.

For scheduling purposes those two situations are opposite. A tight arm is the one where a
counterexample, if it exists, is most likely to sit just past the reachable order; a
slack arm is one where a counterexample would have to be structurally different from
anything the search is producing. Run 2 should spend on 19 and 40 before 100.

**The arms were killed** after n = 14 in line with the run's own bandit rule: no arm's
objective moved above 0, the tight/slack split had already been measured, and the cores
were worth more to the frozen-checker re-verification of the n <= 10 and girth >= 6 sweeps.
Three arms (141, 160, 198a, 291, 314) had not yet run when the arms were killed; their
exhaustive results already cover the same range, so nothing was lost that the exhaustive
sweeps had not already settled.

## The n = 11 exhaustive sweep — partial, and why it stopped there

n = 11 is where the first published counterexample in this family lives, so an exhaustive
sweep there was the highest-value compute left. It was run **sliced by edge count**, so
that an interrupted run still states something exact rather than nothing:

| slices | coverage | graphs | candidates |
|---|---|---|---|
| edges 10..26 (17 of 46) | every connected graph on 11 vertices with at most 26 edges | **392,385,496** | **0** |
| edges 27..55 | not run | — | — |

> **The eight conjectures scanned (19, 61, 100, 133, 141, 160, 291, 314) have no
> counterexample among the 392 million connected graphs on 11 vertices with at most 26
> edges.** The remaining slices contain the denser graphs and were not reached.

**Why it stopped.** Not a crash and not a decision about the mathematics: this container is
suspended between orchestrator turns, so a detached background job only advances while the
session is actively doing something else. Across one 54-minute wall-clock window the
`edges=27` slice accumulated roughly 3 minutes of CPU. Finishing all 46 slices
(1,006,700,565 graphs) was therefore not reachable, and continuing to idle-wait on it would
have bought coverage at roughly one part in twenty of real time.

That is worth recording as an environment fact for run 2: **long background compute in this
harness must be driven by the foreground, not detached from it.** A sweep of this size
should be split into foreground-sized chunks that each complete inside a single turn, which
is exactly what the edge-slicing already makes possible.

Numbers regenerate with `python3 mine/tools/refresh_n11_numbers.py`.
