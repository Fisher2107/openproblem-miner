# Attack log: bound-ramsey-R5-5

Target (`mine/corpus/problems.jsonl`, id `bound-ramsey-R5-5`): R(5,5), published range
43 <= R(5,5) <= 46. Improving the lower bound means a graph on 43 vertices with no K5 and
no independent 5-set (would give R(5,5) > 43, i.e. R(5,5) >= 44). The corpus entry flags
this as the single most heavily mined target in the whole cluster (McKay/Radziszowski/Exoo
1997 exhaustive classification of all 656 known (5,5,42)-graphs, none extendable to 43;
Angeltveit-McKay 2024 spent ~80 CPU-years of SAT search on the *upper* bound).

Freeze check before every verification run:
```
$ bash scripts/check-freeze.sh
VERIFIER INTACT (40 files)
```
(re-run and confirmed clean at every checkpoint; no drift observed).

## Rung 1: reconstruct the known record at n=42

Found cached known (5,5,42)-graphs at
`mine/cache/h4_aLehav_RamseyTheoryRL/RamseyTheoryRL/data/ramsey_s_t_n/5_5/r55_42some.g6`
(328 lines -- a subset of the 656 known graphs, or 656 counting some duplicate
representation; not re-derived here). Took the first line, built a witness, ran the
frozen checker:

```
$ python3 mine/verify/checkers/check_ramsey_lower.py mine/attacks/bound-ramsey-R5-5/rung1_known_n42.json
NOTE: this certifies R(5,5) > 42. The published lower bound supplied with the witness is 43,
so this witness does not beat the record.
...
ACCEPT: the conjecture's conclusion FAILS on this witness while its hypotheses HOLD -- this is a counterexample.
EXIT=0
```
**Known record reproduced.** (witness file: `rung1_known_n42.json`; full output in
`checker-output.txt`)

Degree-sequence check on this graph: `[19, 20, 21, 22]` -- **not regular**, hence **not a
circulant graph** (consistent with the corpus's own note that a Lovász-theta spectral
argument in the AutoRamsey repo suggests 43-vertex graphs of this exact type may not exist
at all -- a structural, not just a search, obstacle).

## Rung 2: simulated annealing over circulant graphs

Code: `anneal_circulant.py` (identical to the R4-6 arm's, parameterised s=t=5). Same
objective/encoder pipeline, already sanity-checked against a known case (C5 for R(3,3)=6)
in the R4-6 arm of this run.

**Sanity run at n=42** (the known-record size): 3000 iters x up to 3 restarts, ~300s wall
budget (log: `sa_n42_long.log`, cut off by the wall-clock timeout partway through restart
3): best objective found across all restarts = **168**, never 0. Confirms circulant graphs
do not reach parity with the known (non-circulant) n=42 record within this budget/move-set
-- consistent with the record graph's irregular degree sequence above.

**Push to n=43** (the actual target), same budget shape (log: `sa_n43_long.log`, also cut
off partway through restart 3): best objective found across all restarts = **387**
(restart 1: 516, restart 2: 430, restart 3: 387 and still falling slowly when the wall
clock ran out -- not yet flat to the same degree as the R4-6 arm, but still an order of
magnitude from 0 and with no restart coming remotely close).

Every restart plateaus within the first few hundred iterations (out of 3000) at a level
roughly 2-3x the size of the graph's edge count, then only inches down slowly under
further annealing -- the search is not oscillating near a feasible region, it is stuck in
a broad basin far from feasible.

No zero-objective witness was produced at either n=42 or n=43, so no witness JSON was
written by the script (it only serializes a witness at the end of all restarts or on
objective 0, and the wall-clock timeout cut off both runs before that point) and nothing
further was submitted to the frozen checker for rung 2.

## Rung 3: SAT

**Not attempted.** Sizing check only: n=43 gives C(43,2)=903 boolean variables and
C(43,5)+C(43,5) = 1,925,196 clauses of length C(5,2)=10 -- comparable in scale to the
R(4,6) SAT encoding attempted in the sibling arm, which itself did not return a decided
result inside its wall-clock budget. Given (a) the sibling arm's SAT attempt already
demonstrated that a ~2M-clause instance does not resolve inside a few hundred seconds on
this hardware, (b) R(5,5) is independently documented as having absorbed ~80 CPU-years of
dedicated SAT search already, and (c) under 10 minutes of budget remained when this
decision was made, launching an under-resourced SAT run here would not have produced a
decided result. Per the mission's honesty rule, this is reported as **not attempted**,
not as a negative SAT result.

## Ladder rung reached

Rung 1 (known record reconstructed, n=42) -> Rung 2 (circulant SA at n=42 and n=43, both
flat/slow, best 168 and 387 respectively, never 0) -> Rung 3 not attempted (sizing done,
solve skipped for budget reasons, honestly reported as unexecuted).

## Honest verdict

**Summary**: best n reached = 43 (target, no witness found there); published lower bound =
43 (R(5,5) > 42 already known, i.e. R(5,5) >= 43); ladder rung reached = 2 (SAT sized but
not run); the frozen checker accepted only the rung-1 reconstruction of the existing n=42
record (exit 0) -- it was never handed a candidate at n=43 because none reached objective
0. Arm stopped because circulant SA plateaus at objective 168 even at the *known* record
size n=42 (matching this record's provably non-circulant structure) and at objective ~387
at n=43, with every independent restart landing in the same broad non-feasible basin; SAT
was sized but not run given the remaining budget and the well-documented extreme difficulty
of this exact target (Angeltveit-McKay's 80 CPU-years). This matches the mission's own
expectation for this arm ("beating a Ramsey record here is extremely unlikely... the
purpose is to measure how far a 4-core hour actually gets") -- the honest conclusion is
that circulant SA alone, on the budget available, does not get anywhere near a witness for
this specific target, and SAT's feasibility at this scale remains genuinely open pending a
longer, dedicated run (priced for run 2 in the top-level report).
