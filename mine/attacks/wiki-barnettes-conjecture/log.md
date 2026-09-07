# wiki-barnettes-conjecture — 3-connected cubic bipartite planar graphs are Hamiltonian

**Statement.** Barnette's conjecture: every 3-connected cubic bipartite planar graph has a
Hamiltonian cycle. Corpus id `wiki-barnettes-conjecture` (cluster H3).

**No frozen checker exists for this problem**, so nothing here could ship.

**Why it was worth an arm.** The hypothesis class is *extraordinarily* small — being cubic,
bipartite, planar and 3-connected simultaneously is very restrictive — so exhaustive
enumeration of the whole class reaches far higher orders than any general graph sweep. At
n = 22 there are 4,132 connected cubic bipartite graphs and only **8** of them are 3-connected
and planar.

**Attack.** `nauty-geng -qc -d3 -D3 -b n` for the cubic bipartite graphs, `networkx`
planarity and 3-connectivity filters, then a backtracking Hamiltonian-cycle search.

| n | cubic bipartite | in class (3-connected + planar) | non-Hamiltonian |
|---|---|---|---|
| 8 | 1 | 1 | 0 |
| 10 | 2 | 0 | 0 |
| 12 | 5 | 1 | 0 |
| 14 | 13 | 1 | 0 |
| 16 | 38 | 2 | 0 |
| 18 | 149 | 2 | 0 |
| 20 | 703 | 8 | 0 |
| 22 | 4,132 | 8 | 0 |

**Verdict.** The conjecture holds for every member of its class on at most 22 vertices.
Barnette's conjecture has been verified far beyond this in the literature (into the sixties
of vertices), so again this reproduces known ground.

**The transferable lesson.** The binding constraint on every arm in this run was *reach*,
and reach is bought by hypothesis restrictiveness, not by cores. The two arms that got
furthest — this one and WOWII 141 — both got there by enumerating a class the conjecture's
own hypotheses cut down, rather than by enumerating graphs and filtering afterwards. That
should be the default attack shape in run 2.

**Reproduce.** `python3 mine/attacks/wiki-barnettes-conjecture/attack.py 8 22`
