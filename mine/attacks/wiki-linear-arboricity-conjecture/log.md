# Attack log — wiki-linear-arboricity-conjecture (agent A4)

## Statement attacked
Linear arboricity conjecture: every graph `G` with maximum degree `Delta`
decomposes into `la(G) = ceil((Delta+1)/2)` edge-disjoint linear forests
(forests whose components are all paths).

**No frozen checker exists for this problem** (`mine/verify/checkers/` has
no `check_linear_arboricity*` / `check_la*`, confirmed via
`bash scripts/check-freeze.sh` — freeze intact, 40 files, no drift).
Nothing found here can ship as a result in this run.

## Published verification frontier
- Proved for `Delta = 3,4,5,6` (Akiyama, Exoo, Harary — original 1981
  papers and follow-ups), and separately for `Delta = 8` and `Delta = 10`
  (later discharging-method papers by Wu and others).
- `Delta = 7` and `Delta = 9` are the smallest **open** general cases
  (i.e. the conjecture is proved for 3,4,5,6,8,10 but the gaps at 7 and 9,
  and all `Delta>=11`, remain open in general).
- Asymptotically, Alon (1988) proved `la(G) = Delta/2 + o(Delta)`; later
  papers improve the error term but the *exact* conjectured value is only
  known at the specific `Delta` values above.
- Cubic graphs (`Delta=3`) specifically settled early (Akiyama, Exoo,
  Harary; shorter proof by Akiyama & Chvátal 1981) — already covered by
  the `Delta<=6` general result above.
- Source: WebSearch summary citing arXiv:2512.11240 ("The Linear
  Arboricity Conjecture for Graphs with Large Girth") and Wikipedia's
  "Linear arboricity" article (per WebSearch snippet; direct fetch
  egress-blocked in this sandbox).
- I found **no record of an exhaustive small-graph SAT/ILP counterexample
  search** for `Delta=7` or `Delta=9` in the literature — all prior work
  found is proof-theoretic (discharging), not computational search. This
  makes `Delta=7` (the smallest open case) the natural compute target.

## Class enumerated and why
`Delta=7` is the smallest open general case, so it's the best place to
look for a small counterexample (`Delta<=6` is already a theorem — testing
it would waste budget). Enumerated: **all connected graphs with max degree
exactly 7**, via `nauty-geng -qc -D7 <n>` filtered in Python to
`Delta(G)==7` (nauty has no exact-degree filter). Minimum `n` for
`Delta=7` is 8 vertices.

## Frontier reached
- **Exhaustive at n=8** (1,044 graphs with `Delta=7`, out of 11,117 total
  with `Delta<=7`) and **n=9** (63,411 graphs with `Delta=7`, out of
  248,734 total with `Delta<=7` — full sweep completed, not partial; see
  `n9_la.log`, ends "DONE checked=63411 skipped=185323 time=132.1s").
  Zero counterexamples at either `n`.
- `n=10` (9,532,717 total `Delta<=7` graphs from `nauty-geng`) was
  estimated but **not attempted** — out of budget; would need roughly
  40x the n=9 wall time on the current single-threaded encoding, i.e.
  tens of minutes to hours, not the remaining slice of a 45-minute
  four-target budget.
- Compared to published frontier: as with total coloring, I found no
  prior small-graph computational sweep for this exact open case, so
  n=8-9 exhaustive is a new frontier rather than an improvement on a
  cited number.

## Method
CEGAR loop in `linear_arb_sat.py` (python-sat, Glucose3): SAT variables
`y_{e,c}` (edge `e` gets forest-color `c`) for `k = ceil((Delta+1)/2)`
colors, `Delta=7` -> `k=4`. Hard constraints: each edge exactly one color;
each vertex has degree <=2 within each color class (necessary condition
for a linear forest — encoded as "no 3 same-colored edges share a
vertex", pairwise-at-most-2 via forbidding every 3-subset). Acyclicity
(the missing necessary-and-sufficient piece — max-degree-2 alone allows
disjoint cycles, which are *not* linear forests) is enforced by
counterexample-guided refinement: solve, check each color class for a
cycle with `networkx.find_cycle`, and if found, add a blocking clause
forbidding that exact edge set from being monochromatic, then re-solve.
UNSAT (even before any cycle-blocking) is reported as a genuine
counterexample candidate.

**Sanity-tested against known cases**: Petersen graph (`Delta=3`, known
`la=2`) — SAT at `k=2`, correctly **UNSAT at `k=1`**. `K5` (`Delta=4`,
conjecture holds since `Delta<=6` is proved) — SAT at `k=3`
(`ceil(5/2)=3`), correctly **UNSAT at `k=2`**. Both match known values.

## Wall time
- n=8: 5.1s. n=9: 132.1s. Sanity checks + encoding: ~3 min.
- Total compute for this target: ~3 min.

## Verdict
**No violation found.** Both n=8 and n=9 are fully exhaustive (not
partial) over all `Delta=7` connected graphs — zero counterexamples to
`la(G) <= 4` at this degree.

**No frozen checker exists for this problem, so this cannot ship as a
result even though nothing suspicious turned up.**

## Run-2 recommendation
**Tractability: 5/10.** Encoding works and is validated, the class is
correctly targeted (smallest open `Delta`), but CEGAR-over-SAT scales
worse than the pure-coloring encoding used for total coloring (132s for
63K graphs at n=9 vs. total coloring's similar graph count in a fraction
of that time), so pushing to n=10 (9.5M candidate graphs) needs either
much more wall-clock or a smarter encoding (e.g. a native
acyclicity-via-ordering SAT encoding instead of CEGAR, or restrict to
7-regular graphs the way the total-coloring arm restricted to 6-regular,
which would shrink the count sharply and let the sweep reach further
before the graph count explodes). Recommend run 2 try the 7-regular
subclass first, then `Delta=9` (the other open gap) with the same method.
