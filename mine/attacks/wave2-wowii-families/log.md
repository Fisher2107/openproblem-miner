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
