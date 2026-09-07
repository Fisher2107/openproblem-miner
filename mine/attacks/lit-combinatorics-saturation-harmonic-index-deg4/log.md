# lit-combinatorics-saturation-harmonic-index-deg4

Agent: A5 (recent-literature finite-witness conjectures). **No frozen checker exists for
this target — the mine's verifier (`mine/verify/`) was built and hash-locked before this
entry was selected (`scripts/check-freeze.sh` confirmed VERIFIER INTACT, 40 files, at the
start of this run), and it will not be reopened. Nothing found here can ship as a
`mine/results/` entry in this run. This is exploratory frontier-measurement only.**

## Exact statement (every symbol defined)

Source: arXiv:2606.15761 (v3), "Sharp bounds between the saturation number and the
harmonic index". Corpus entry: `mine/corpus/raw/h6_literature.jsonl` id
`lit-combinatorics-saturation-harmonic-index-deg4`.

The saturation number mu*(G) is the minimum cardinality of a maximal matching (a matching
that cannot be extended by adding another disjoint edge) — equivalent, as used here, to
the minimum edge dominating set of G (a set M of edges such that every edge of G is
either in M or shares an endpoint with an edge of M; the two coincide because "M cannot be
extended by an edge f" means f already meets some edge of M). The harmonic index is
H(G) = sum_{uv in E(G)} 2/(deg(u)+deg(v)).

**Conjecture**: every connected graph G with maximum degree Delta(G) <= 4 satisfies
mu*(G) <= H(G).

## Open-status check

WebSearch (`arXiv 2606.15761 Sharp bounds saturation number harmonic index`) confirms the
paper's subject matter (saturation number vs. harmonic index) but the search snippets did
not surface independent commentary beyond the corpus entry itself. The corpus's own
`known_cases`/`prior_attempts` fields are unusually well-sourced here and are load-bearing
for the open-status call: the *unrestricted* conjecture (mu*(G) <= H(G) for every
nontrivial connected graph, originally a TxGraffiti automated-conjecturing output from
2023) is already **refuted** — Biyikoglu showed the ratio mu*(G)/H(G) can be made
arbitrarily large, and this very paper (2606.15761) exhibits the friendship graph F_4 (9
vertices, one hub of degree 8) as the smallest counterexample. The max-degree-4
restriction attacked here is the proposed fix, proved only for regular graphs so far.
**Open-status verdict**: genuinely open for the general (non-regular) max-degree-<=4 case;
not previously refuted (the known F_4 counterexample has a degree-8 hub, so it is excluded
by the Delta<=4 restriction and gives no information about this restricted conjecture).

**Sanity note on the friendship-graph counterexample**: since the unrestricted conjecture
is known false with a Delta=8 counterexample, this is a good calibration case for "how
close is the boundary" — the exhaustive search below found no violation up to Delta<=4,
n<=10, which is consistent with (but does not prove) the degree-4 cutoff being a genuine
fix rather than merely pushing the exception to a slightly larger degree.

## Method

Exhaustive generation of all *connected* graphs of maximum degree <=4 on n vertices via
`nauty-geng -c -D4 n` (nauty's native degree-bound filter, connected-only per the
conjecture's own "every connected graph" quantifier). For each graph:
- **H(G)** computed EXACTLY as a `fractions.Fraction` sum over edges (degrees are small
  integers, so this is exact rational arithmetic, zero floating point, zero rounding
  risk).
- **mu*(G)** computed EXACTLY via a MaxSAT encoding of minimum edge dominating set, solved
  with `pysat.examples.rc2.RC2` (an exact, complete MaxSAT solver — not a greedy
  heuristic, not an LP relaxation): hard clauses enforce (a) at most one selected edge per
  vertex (the matching constraint: for every vertex, every pair of its incident edges gets
  a `(-x_e OR -x_f)` clause) and (b) every edge is selected or adjacent to a selected edge
  (the maximality/domination constraint: for every edge f, a clause over f and all edges
  adjacent to f); soft unit clauses (one per edge, weight 1, preferring unselected) make
  RC2 minimize the count of selected edges.
- **Correctness self-check before the sweep**: hand-verified the solver against 4 graphs
  with known minimum-maximal-matching numbers before trusting it at scale — P_4 (mu*=1),
  C_4 (mu*=2 — note: a single C_4 edge is *not* a maximal matching, since the opposite
  edge is still addable; this is easy to get wrong by eye and the solver got it right),
  C_6 (mu*=2), and the star K_{1,4} (mu*=1). All four matched hand computation exactly
  before the full sweep was trusted.

Since both mu*(G) and H(G) are computed exactly (rational arithmetic + a complete
combinatorial solver, no floats anywhere in this target unlike the two eigenvalue-based
targets in this batch), **any observed mu*(G) > H(G) here would be a genuine
counterexample with no tolerance/precision caveat** — this is the cleanest exactness
story in the whole batch.

Repro:
```
python3 mine/attacks/lit-combinatorics-saturation-harmonic-index-deg4/check.py
```

## Frontier reached

**Every connected graph of maximum degree <=4 on 2 to 10 vertices: 103,999 graphs, zero
violations.** Breakdown:
- n=2..9: 14,597 graphs, 7.8s.
- n=10 alone: 89,402 graphs, 60.2s.
- Total wall time: ~60.3s (per-graph MaxSAT solve is fast since edge counts are small,
  <=20 edges at n=10 with Delta<=4).

n=11 (739,335 connected maxdeg<=4 graphs per `nauty-geng -c -D4 11 | wc -l`, run
separately) was not attempted: extrapolating from the ~8.3x graph-count growth from n=9
to n=10 against the observed ~60s at n=10, n=11 alone would plausibly take on the order of
8-10 minutes, which was not spent given the shared 45-minute cross-target budget for this
wave.

## Wall time

Total agent time on this target, including the correctness self-check: ~11 minutes.

## Verdict

**No counterexample found among all 103,999 connected maximum-degree-<=4 graphs on <=10
vertices**, with both sides of the inequality computed exactly (no floating-point
tolerance question, unlike the eigenvalue-based targets in this same batch). Positive
computational corroboration only — not a proof, and **cannot ship as a mine/results/
entry** (no frozen checker for this problem; see header). Given the known Delta=8
counterexample to the unrestricted conjecture, and that this restricted (Delta<=4) form
survives an exhaustive n<=10 sweep, the natural run-2 recommendation is to push to n=11-13
(the per-graph MaxSAT solve is cheap; nauty-geng's own enumeration cost, not solving, is
the dominant cost at these sizes) before considering this settled either way.

## Negative-memory entry

See `mine/memory/negative-a5.jsonl`: exhaustive search up to n=10 (all Delta<=4 connected
graphs) found nothing — a genuine corroboration, not a stuck arm, complementary to the
already-known Delta=8 refutation of the unrestricted conjecture that motivated this
narrower restatement in the first place.
