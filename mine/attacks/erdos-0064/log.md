# erdos-0064 — min degree 3 forces a cycle of length a power of two

**Statement.** Does every finite graph with minimum degree at least 3 contain a cycle of
length `2^k` for some `k >= 2`? (Erdős Problem 64; `mine/corpus/problems.jsonl`.)

A counterexample is a graph with `delta(G) >= 3` and **no** cycle of length 4, 8, 16, ...
That is a genuine finite witness, which is why this was worth an arm.

**No frozen checker exists for this problem**, so a find here could not have shipped.

**Attack.** Exhaustive over `nauty-geng -c -d3 n` (connected, min degree >= 3), testing
cycle lengths 4, 8, 16 by a DP over (vertex subset, endpoint) anchored at the lowest vertex
of the subset. The cycle-length routine and the max-cut routine were validated against an
independent permutation-based brute force on 60 graphs before use — that check is the only
thing standing between this arm and a silent false negative, since there is no frozen
checker to catch a mistake here.

| n | connected graphs with delta >= 3 | violations |
|---|---|---|
| 4..9 | 87,004 | 0 |
| 10 | 5,203,110 | 0 |
| **total** | **5,290,114** | **0** |

**Verdict.** No counterexample at n <= 10. The obstacle to going further is that the
witness must dodge *every* power of two simultaneously, and small graphs with min degree 3
are cycle-rich: at n <= 10 essentially every candidate already contains a 4-cycle or an
8-cycle. The interesting regime is high-girth cubic graphs at larger n, where 4-cycles are
excluded by construction and only the 8- and 16-cycle conditions bite — that is the right
place for run 2 to spend, and `geng -c -d3 -tf` makes it enumerable.

**Reproduce.** `for n in $(seq 4 10); do nauty-geng -qc -d3 $n | ./mine/tools/wowscan --only 901; done`
