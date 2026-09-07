# Attack log — wiki-conways-thrackle-conjecture (agent A4)

## Statement attacked
Conway's thrackle conjecture: a thrackle is a drawing of a graph in the
plane where every pair of edges meets exactly once, either at a shared
endpoint or at a proper crossing. Conjecture: every thrackle drawing of a
graph on `n` vertices has at most `n` edges.

**No frozen checker exists for this problem** (`mine/verify/checkers/` has
no `check_thrackle*`, confirmed via `bash scripts/check-freeze.sh` —
freeze intact, 40 files, no drift). Nothing found here can ship as a
result in this run.

## Why this one did NOT get a compute run (read this before judging the
## budget split)
The other three targets (Brouwer, total coloring, linear arboricity) are
all "does every graph in an enumerable class satisfy a numeric bound
computable from the graph alone" — a SAT/eigenvalue check per graph,
which is exactly what `nauty-geng` + SAT/numpy is built for. The thrackle
conjecture is a different shape: the question per graph is **"does a
thrackle drawing of this graph exist at all"** — an embedding-existence
question in the plane, not a property computable from the abstract graph
structure alone. There is no SAT/z3 encoding of "thrackleable" available
off the shelf here, and building one from scratch (the actual published
computational approach, Fulek & Pach 2011, arXiv:1002.3904, is a
nontrivial rotation-system / crossing-parity search, not a simple CNF) was
judged out of scope for the remaining budget in this run. Spending the
slice of the ~45-minute joint budget that would have gone to a half-built,
unvalidated geometric-drawing checker was the wrong trade against the
other three targets, which had clean, validated SAT encodings ready to go.
This is a deliberate scoping decision, not an oversight — recorded here so
run 2 can pick it up with the right tool instead of my ad hoc one.

## Published verification frontier
- Best known upper bound: approx. `1.3984n` (Fulek, Gyárfás, and others,
  improving the earlier `1.5(n-1)` / `1.428n` bounds via the Fulek–Pach
  computational approach — an algorithm that decides `t(n) <= (1+eps)n`
  for a given `eps` and searches for near-violations).
  Source: WebSearch summary of arXiv:1002.3904 ("A computational approach
  to Conway's thrackle conjecture") and arXiv:1708.08037 ("Thrackles: An
  Improved Upper Bound").
- **Key structural reduction, the most useful prior-art fact found**:
  Woodall proved that (assuming Conway's conjecture) a graph is
  thrackleable iff it has at most one odd cycle, at most one cycle per
  connected component, and no 4-cycle. Separately, **Conway's thrackle
  conjecture is known to be equivalent to a single narrow statement**:
  *every graph formed by two even cycles sharing exactly one common
  vertex is not thrackleable.* (WebSearch summary, citing the Woodall
  characterization literature and "Thrackles containing a standard
  musquash", arXiv:1601.05562 / ajc.maths.uq.edu.au v70 p168.)
  This means the **entire open conjecture reduces to a 2-parameter family**
  — pairs of even cycle lengths `(2a, 2b)` — rather than "all graphs".
  I could not confirm within budget whether this specific 2-parameter
  family has itself been exhaustively checked for small `(a,b)` in the
  literature; the sources found describe the reduction but I did not find
  an explicit "checked for a,b <= K" statement to cite a number against.
- Bipartite thrackleable graphs are known to be exactly the planar ones
  (an old Woodall-era result, cited alongside the above).

## Class NOT enumerated (recorded for run 2, not attempted this run)
The two-even-cycles-sharing-a-vertex family described above is small,
well-defined, and exactly the right target: enumerate `(a,b)` with
`2<=a<=b<=K` for some bound `K`, build each "dumbbell" graph, and decide
thrackleability with a real embedding/rotation-system search (Fulek–Pach's
algorithm, or a from-scratch SAT-style encoding of rotation systems +
crossing-parity constraints per edge pair). This is a materially smaller
and better-scoped target than generic small-graph enumeration and is my
top run-2 recommendation for this conjecture — but it needs a
purpose-built checker that does not exist in this repo or in any tool
available to me this run (no off-the-shelf thrackle-drawing decision
procedure in nauty/SAT/z3).

## Frontier reached
**None — no compute was run for this target.** This is a considered
"stop early, diagnose why" call per the mission's honest-failure rule
(MISSION.md P4 / CLAUDE.md "Honest failure"), not a flat-arm result from
an attempted search.

## Wall time
~8 minutes, all spent on prior-art search (WebSearch queries on
verification frontier, Woodall characterization, and the two-even-cycles
reduction). Zero minutes of compute.

## Verdict
**Not attacked.** No violation search was run, so there is nothing to
report as suspicious or otherwise. This is the honest outcome given the
mismatch between the conjecture's actual shape (embedding existence) and
the tooling available in this session (graph enumeration + SAT/eigenvalue
checkers).

**No frozen checker exists for this problem, so nothing found here — had
anything been found — could ship as a result in this run.**

## Run-2 recommendation
**Tractability: 3/10 as posed to me (generic small-graph sweep), but
7/10 if reframed around the two-even-cycles reduction with the right
tool.** The single most valuable next step is not "enumerate more
graphs", it's: (1) get or build a thrackle-drawing decision procedure
(port Fulek–Pach's algorithm, or design a rotation-system SAT encoding),
and (2) apply it *only* to the two-even-cycles-sharing-a-vertex family
Woodall's equivalence reduces the whole conjecture to — that family is
small, well-defined by two integers, and the correct target size for a
real search, unlike "all small graphs" which is both intractable and not
even the right class (Woodall already tells you almost every graph is
either trivially thrackleable or trivially not).
