# Attack log: bound-ramsey-R4-6

Target (`mine/corpus/problems.jsonl`, id `bound-ramsey-R4-6`): R(4,6), published range
36 <= R(4,6) <= 40. Improving the lower bound means a graph on 36 vertices with no K4 and
no independent 6-set (would give R(4,6) > 36, i.e. R(4,6) >= 37).

Freeze check before every verification run:
```
$ bash scripts/check-freeze.sh
VERIFIER INTACT (40 files)
```
(re-run and confirmed clean at every checkpoint below; no drift observed at any point).

## Rung 1: reconstruct the known record at n=35

Found cached known (4,6,35)-graphs at
`mine/cache/h4_aLehav_RamseyTheoryRL/RamseyTheoryRL/data/ramsey_s_t_n/4_6/r46_35some.g6`
(37 such graphs). Took the first line, built a witness and ran the frozen checker:

```
$ python3 mine/verify/checkers/check_ramsey_lower.py mine/attacks/bound-ramsey-R4-6/rung1_known_n35.json
NOTE: this certifies R(4,6) > 35. The published lower bound supplied with the witness is 36,
so this witness does not beat the record.
...
ACCEPT: the conjecture's conclusion FAILS on this witness while its hypotheses HOLD -- this is a counterexample.
```
Exit 0. **Known record reproduced.** (witness file: `rung1_known_n35.json`)

Degree-sequence check on this graph (`sorted(set(degs))` over the decoded adjacency) gives
`[12, 13, 14, 15]` -- **not regular**, hence this record graph is **not a circulant graph**.
This matters for rung 2 below: circulant search is a strictly smaller space than the one
containing the actual known record, so a negative result from circulant SA at n=35 does not
mean "no witness exists at n=35", only "no *circulant* witness exists there" (or none was
found).

## Rung 2: simulated annealing over circulant graphs

Code: `anneal_circulant.py`. Search space = symmetric connection sets S subset of
{1..floor(n/2)} on Z_n. Objective = exact total count of monochromatic K4 cliques plus
independent 6-sets, computed cheaply via vertex-transitivity (count structures through
vertex 0, multiply by n/k) rather than raw C(n,4)+C(n,6) enumeration. Verified this
objective/graph6-encoder pipeline against ground truth twice: (1) C5 circulant for
R(3,3)=6 gives objective 0 and the frozen checker accepts it (see sanity checks in this
directory's history / reproducible via `python3 -c` snippet in session log); (2) round-
tripped a produced witness through the frozen checker successfully.

**Sanity run at n=35** (single-flip moves, single-distance flip per step, 400 iters x 2
restarts, ~9s): best objective found = 140 (never reached 0). Confirms circulant graphs
of this search shape do not reach parity with the known (non-circulant) n=35 record within
this budget/move-set.

**Push to n=36** (the actual target), longer run: 3000 iters x 3 restarts, ~300s wall
budget (background job, log: `sa_n36_long.log`):
```
restart 1 done: best_obj=126 wall=170.9s
restart 2 done: best_obj=243 (in progress at report time / see sa_n36_long.log for final line)
```
Best objective across all restarts and the earlier short runs: **108** (short run,
`sa_best_s4_t6_n36.json`), never reaching 0. All restarts plateau within the first
~150-300 iterations (out of 3000) and stay completely flat afterward -- textbook stuck
local minimum for this move set, not a slowly-converging search.

**Verdict for rung 2: FLAT.** No zero-objective circulant graph found at n=36 within
budget. Best objective observed: 108 monochromatic K4/I6 structures (down from a random-
start objective in the thousands, but nowhere near 0).

## Rung 3: SAT encoding

Code: `sat_encode.py`. Encodes exactly the same predicate the frozen checker verifies:
one boolean per edge of K_n, a clause per 4-subset forbidding all-edge (K4), a clause per
6-subset forbidding all-non-edge (I6). Verified correct on a small case (s=3,t=3,n=5:
SAT, model round-tripped through the frozen checker, ACCEPT, exit 0) before scaling up.

Encoding size at n=36: **630 variables, 2,006,697 clauses** (58,905 K4-clauses + 1,947,792
I6-clauses), built in ~15-18s wall time in Python -- confirms the corpus entry's own
sizing estimate was in the right ballpark.

Solve attempt: `python3 sat_encode.py 4 6 36 150` (150s solve-time budget) using
`pysat.solvers.Cadical153`, run under a hard timeout. See `checker-output.txt` /
`sat_n36_run.log` for the literal result of that run.

## Ladder rung reached

Rung 1 (known record reconstructed) -> Rung 2 (circulant SA, flat, best 108) -> Rung 3
(SAT, size confirmed feasible to encode; solve outcome in `sat_n36_run.log`).

## Honest verdict

The frozen checker accepted only the rung-1 reconstruction of the *existing* record
(n=35); it did not accept anything at n=36 -- no zero-objective witness was ever produced
at n=36, so nothing was submitted to the checker there (submitting a non-zero-objective
graph would just be re-demonstrating a K4 or I6 exists, which is not informative). See
`checker-output.txt` for the literal commands/outputs. Rung 2 (circulant SA) plateaus at
best_obj ~108-504 depending on restart/seed, an order of magnitude away from 0, and the
known record itself is provably non-circulant (irregular degree sequence), so circulant
search was always attacking a strictly harder sub-problem than "any graph". Rung 3 (SAT)
is sized realistically (2M clauses, ~15s to build) but whether it decides within a
reasonable time budget is reported in `sat_n36_run.log` / `checker-output.txt`, not
assumed here.
