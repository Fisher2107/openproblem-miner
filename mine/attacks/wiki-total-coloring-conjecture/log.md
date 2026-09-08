# Attack log — wiki-total-coloring-conjecture (agent A4)

## Statement attacked
Total coloring conjecture (Behzad–Vizing): every graph `G` has total
chromatic number `chi''(G) <= Delta(G) + 2`.

**No frozen checker exists for this problem** (`mine/verify/checkers/` has
no `check_total_coloring*`, confirmed via `bash scripts/check-freeze.sh` —
freeze intact, 40 files, no drift). Nothing found here can ship as a
result in this run.

## Published verification frontier
- Proved for `Delta<=5` in general graphs: Rosenfeld and Vijayaditya
  independently for `Delta=3`; Kostochka for `Delta=4,5`.
- Proved for planar graphs with `Delta=7,8` and `Delta>=9`.
- `Delta=6` is the smallest **open** case, and it is open even for planar
  graphs except under extra sparsity conditions — most recent work (2025)
  narrows the planar `Delta=6` gap further (no adjacent 4-fans/mushrooms/
  tents/cones), but the fully general `Delta=6` case (planar or not) is
  still open.
  Source: WebSearch summary of arXiv:2507.12737 ("The Total Coloring
  Conjecture holds for planar graphs without three special subgraphs") and
  TheoremDB's total-coloring-conjecture entry (fetch of theoremdb.org
  itself is egress-blocked in this sandbox; relayed via WebSearch snippet,
  "TCC remains OPEN as checked on 2026-08-01").
- A 2020 arXiv preprint (Murthy, arXiv:2003.09658) claims a full proof via
  Combinatorial Nullstellensatz over `Z_p`; **not accepted by the
  community** — later 2025-2026 papers (including the one above) continue
  to treat the general conjecture as open, and I found no journal
  acceptance record. Treated as unresolved / likely flawed, not prior art
  that settles the target.
- I found **no record of an exhaustive nauty+SAT sweep specifically over
  Delta=6 graphs** in the literature (searches for "total chromatic number
  SAT solver exhaustive Delta=6" returned only general remarks that
  SAT+nauty *can* be combined for chromatic-number questions, no concrete
  prior sweep for this conjecture). This makes Delta=6 the best-motivated
  compute target of my four.

## Class enumerated and why
`Delta=6` is the smallest degree bound left open in general (non-planar)
graphs, so it's the correct place to look for a small counterexample —
anything with `Delta<=5` is already a theorem and would be wasted compute.
Two tracks:
1. **All connected graphs with max degree exactly 6**, generated with
   `nauty-geng -qc -D6 <n>` and filtered in Python to `Delta(G)==6`
   (nauty has no "exact degree" filter, only min/max bounds).
2. **All connected 6-regular graphs** (`nauty-geng -qc -d6 -D6 <n>`) up to
   a larger `n`, since regular graphs are smaller in count at fixed `n`
   and are the more common extremal/tight family for coloring
   conjectures — lets the sweep reach further before the graph count
   explodes.

## Frontier reached
- Track 1 (general Delta=6 graphs): **exhaustive at n=7 (156 graphs) and
  n=8 (3,687 graphs)**; **partial at n=9** — 55,000 of 109,623 graphs with
  Delta=6 checked before a 240s time budget cutoff (see
  `n9_total_partial.log`, ends mid-sweep at "checked 55000, 238.1s",
  process exit code 124 = timeout). Zero counterexamples in the completed
  portion.
- Track 2 (6-regular): **exhaustive n=7..12** (1, 1, 4, 21, 266, 7,849
  graphs respectively). Zero counterexamples.
- Compared to published frontier: I found no prior exhaustive computer
  sweep at all for this specific open case, so n=8 (general) / n=12
  (6-regular) is a genuine new frontier, not an improvement on a stated
  number — the comparison is "zero vs. n=8/n=12", not "n=X vs n=Y".

## Method
SAT encoding in `total_coloring_sat.py` (python-sat, Glucose3): variables
`x_{v,c}` (vertex `v` gets color `c`), `y_{e,c}` (edge `e` gets color `c`),
for `k = Delta+2` colors. Exactly-one per vertex/edge, adjacent vertices
differ, incident edges differ, a vertex and its incident edges differ.
UNSAT at `k=Delta+2` would be a counterexample.

**Sanity-tested against known cases** before the real sweep: `K7`
(`Delta=6`, known `chi''(K7)=7` since 7 is odd) — SAT at `k=7`
(`Delta+1`), correctly **UNSAT at `k=6` (`Delta`)**, SAT at `k=8`
(`Delta+2`). Matches known theory exactly.

## Wall time
- n=7: 0.3s. n=8: 10.8s. n=9 partial: 240s (timed out, 55,000/109,623
  Delta=6 graphs checked; process launched 2026-09-06 23:43, timed out
  23:47 UTC per background-task log). 6-regular n=7-12 combined: ~60s.
- Total compute for this target: ~5 min.

## Verdict
**No violation found** in any completed portion. n=9 general-Delta=6 sweep
is **incomplete** (~50%) — this is reported honestly as partial, not as a
clean "n=9 verified".

**No frozen checker exists for this problem, so this cannot ship as a
result even though nothing suspicious turned up.**

## Run-2 recommendation
**Tractability: 6/10.** This is the strongest compute target of my four:
Delta=6 is a genuinely open, well-motivated case with (as far as I could
find) no prior exhaustive small-graph sweep, the SAT encoding is clean and
validated, and the search space is enumerable and shrinks nicely under
`-d6 -D6` (regular). Recommend run 2 finish the n=9 general sweep (it's
~50% done — easy to resume by skipping already-covered graph6 lines or
just re-running with a longer time budget) and push the 6-regular track
to n=13-14 with a proper cluster/longer wall-clock budget, since regular
Delta=6 graphs are the most likely place a tight/violating example would
live if the conjecture is false in this exact case.
