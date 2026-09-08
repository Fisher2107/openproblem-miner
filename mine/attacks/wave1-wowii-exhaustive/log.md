# Wave 1 — exhaustive attack on the ten open WOWII / Graffiti.pc conjectures

**Targets.** The ten statements tagged `@[category research open]` in
`FormalConjectures/WrittenOnTheWallII/` at commit `8323e878`:
19, 40, 61, 100, 133, 141, 160, 198a, 291, 314. All Class A: universally quantified over
finite simple connected graphs, so a single small graph refutes any of them, and all the
invariants involved are exactly computable by exhaustive enumeration.

**Why this seam was priced high.** These are machine-generated conjectures (Graffiti.pc)
over a class with cheap exhaustive verification — structurally the easiest ore available.
The triage rubric gave them `machine-generated-graph-conjecture +1.5` and
`has-lean-statement +1.5`.

## Tooling

| piece | role | validation |
|---|---|---|
| `mine/tools/wowscan.c` | fast C screener; emits candidates | every gate is a provable necessary condition (below); all 22 invariants cross-checked against the frozen exact library on 850 graphs at n=8,9,10 with zero mismatches (`mine/tools/crosscheck_invariants.py`) |
| `mine/verify/checkers/check_wow2_*.py` | the frozen verifier; decides | 71 passing checks, both directions, before the freeze |

The screener may over-report; it must never under-report. Each gate below is a proved
necessary condition for a violation, so nothing can slip past it:

- **141**: `tree(G) >= max_v l(v) + 1` always (a vertex plus a maximum independent subset of
  its neighbourhood induces a star, which is a tree), so a violation forces
  `floor(girth/2) - 1 + maxL > maxL + 1`, i.e. **girth >= 6**.
- **133**: a shortest path between two vertices at distance `diam` is induced, so
  `path(G) >= diam + 1`; a violation forces `rad + floor(l_avg)^cC4 > diam + 1`.
- **19, 61**: `b(G) >= alpha(G)` and `f(G) >= alpha(G)` (an independent set is both
  bipartite and a forest), so a violation forces `lhs > alpha`.
- **160**: `Ls(G) <= n - 1` for `n >= 3`, so a violation forces `maxL + maxT*cC4 >= n`.
- **198a**: `b(G) >= alpha(G)`, so the hypothesis forces `alpha*n <= 2n + sum_v ecc(v)`.
- **314**: the hypothesis is triangle-freeness plus `path(G) <= 4`, and `path >= diam + 1`,
  so `diam <= 3`.
- **100, 291, 40**: no cheap necessary condition exists, so these are computed exactly.

## Results — all negative

| range | graphs scanned | candidates |
|---|---|---|
| all connected graphs, n = 3..9 | 273,191 | 0 |
| all connected graphs, n = 10 | 11,716,571 | 0 |
| **all connected graphs, n <= 10 (total)** | **11,989,762** | **0** |
| conjecture 141 only: all graphs of girth >= 5, n = 11..15 | 2,374,364 | 0 |
| conjecture 141 only: all graphs of girth >= 5, n = 16 | 17,772,647 | 0 |

Because a violation of 141 requires girth >= 6, enumerating every girth >= 5 graph is
*exhaustive for that conjecture*. So:

> **Conjecture 141 holds for every finite simple connected graph on at most 16 vertices.**
> The other nine hold for every one on at most 10 vertices.

## Reproduction

```
gcc -O3 -o mine/tools/wowscan mine/tools/wowscan.c
for n in 3 4 5 6 7 8 9 10; do nauty-geng -qc $n | ./mine/tools/wowscan; done
for n in 11 12 13 14 15 16; do nauty-geng -qc -tf $n | ./mine/tools/wowscan --only 141; done
python3 mine/tools/crosscheck_invariants.py 10 250     # screener vs frozen library
bash mine/verify/run-tests.sh                          # 71 checks on the frozen verifier
```

## Honest reading of this negative

n <= 10 was *already* covered in the literature for at least one WOWII conjecture: the
module docstring of `GraphConjecture200.lean` records an exhaustive geng search over all
11,989,760 connected graphs on 4..10 vertices. Our n <= 10 sweep therefore mostly
**reproduces known ground** — its value is that it covers all ten open conjectures at once
and that it validated the screener. The genuinely new coverage is conjecture 141 out to
n = 16, which the girth argument made cheap.

The counterexamples that *are* known for this family (conjectures 103, 194, 200) live at
n = 11, 13 and 18. So n <= 10 was always the wrong place to look, and the sweep's real
contribution is to say so with a measurement instead of a guess.

## The negative, re-checked by the frozen verifier rather than the screener

A "0 candidates" line from `wowscan` is a claim about `wowscan`. Two follow-up runs put the
frozen checkers behind it:

```
$ python3 mine/tools/verify_n10_sample.py        # -> verify_n10_sample.log
VERIFIER INTACT (40 files)
n=9:  sampled 60 graphs,  600 checker runs so far, 0 ACCEPTs
n=10: sampled 240 graphs, 3000 checker runs so far, 0 ACCEPTs
TOTAL frozen-checker runs: 3000, REFUSEs: 0, ACCEPTs: 0
CONFIRMED: the frozen checkers agree with the screener on every sampled graph.
```

and, for conjecture 141, an exhaustive rather than sampled re-check of the only class where
a violation is possible (girth >= 6), via `python3 mine/tools/verify_141_full.py 3 14`:

```
n=14  girth>=6 graphs checked by the FROZEN checker: 21215   ACCEPTs so far: 0
TOTAL 27911 graphs, 0 ACCEPTs
CONFIRMED BY THE FROZEN VERIFIER: conjecture 141 has no counterexample of girth >= 6
on at most 14 vertices, and a counterexample must have girth >= 6.
```

A single ACCEPT in either run would have meant the screener under-reported and this whole
sweep was worthless. Neither produced one.
