# erdos-0023 — making a triangle-free graph bipartite

**Statement.** Can every triangle-free graph on `5k` vertices be made bipartite by deleting
at most `k^2` edges? (Erdős Problem 23.) Equivalently, is `m(G) - maxcut(G) <= k^2` for
every triangle-free G on 5k vertices?

**No frozen checker exists for this problem**, so nothing here could ship.

**Attack.** Exhaustive over `nauty-geng -c -t n` (connected, triangle-free) for the orders
divisible by 5 that are reachable, computing max-cut by exhaustive bipartition. The max-cut
routine was validated against an independent Python brute force on 60 graphs.

| n | k | budget k^2 | triangle-free connected graphs | violations |
|---|---|---|---|---|
| 5 | 1 | 1 | 6 | 0 |
| 10 | 2 | 4 | 9,832 | 0 |

**Verdict.** No counterexample at the two reachable orders. The obstacle is stark and worth
recording precisely: the next case is n = 15, and the number of connected triangle-free
graphs on 15 vertices is far beyond exhaustive enumeration here, while max-cut itself costs
`2^n` per graph. So this arm is not "flat", it is **blocked at the second case** — the
statement's own parameterisation in steps of five vertices means brute force gets exactly
two data points before falling off a cliff. Run 2 should attack it with a max-cut SDP or a
targeted construction (blow-ups of C5 are the classical near-extremal family), not by
enumeration.

**Reproduce.** `for n in 5 10; do nauty-geng -qc -t $n | ./mine/tools/wowscan --only 902; done`
