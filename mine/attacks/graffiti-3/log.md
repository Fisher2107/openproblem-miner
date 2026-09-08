# graffiti-3 — alpha(G) >= rad(G) for connected graphs

**Statement.** For every finite simple connected graph G, the independence number is at
least the radius: `alpha(G) >= rad(G)`. Source: Fajtlowicz's Graffiti, as reproduced in
the TxGraffiti2 documentation (`clone:RandyRDavila/TxGraffiti2`).

**No frozen checker exists for this problem** — it was not in the attack set on freeze day —
so nothing found here could have shipped as a result. The freeze was not reopened.

**Attack.** Exhaustive: every connected graph on n <= 10 vertices, screened by
`mine/tools/wowscan --only 900`, which computes alpha by branch-and-bound and rad by BFS.
Both invariants are cross-checked against the frozen exact library
(`python3 mine/tools/crosscheck_invariants.py`), so the screening arithmetic is the same
arithmetic the verifier would use.

| n | connected graphs | violations |
|---|---|---|
| 3..9 | 273,191 | 0 |
| 10 | 11,716,571 | 0 |
| **total** | **11,989,762** | **0** |

**Verdict.** No counterexample at n <= 10. This is very likely a known theorem rather than
an open problem — the harvest entry itself carries a caution that several Graffiti
inequalities of this shape were proved long ago — so the honest reading is that this arm
tested the pipeline more than it tested mathematics.

**Reproduce.** `for n in $(seq 3 10); do nauty-geng -qc $n | ./mine/tools/wowscan --only 900; done`
