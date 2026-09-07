# wiki-erdos-gyarfas-conjecture — every cubic graph has a cycle of length a power of two

**Statement.** The Erdős–Gyárfás conjecture: every cubic (3-regular) graph contains a
simple cycle whose length is a power of two. Corpus id `wiki-erdos-gyarfas-conjecture`
(harvested by cluster H3 from a GitHub mirror of the Wikipedia unsolved-problems list).
This is the 3-regular case of Erdős Problem 64, attacked separately in
`mine/attacks/erdos-0064/`.

**No frozen checker exists for this problem** — it entered the corpus after the verifier was
frozen — so nothing found here could have shipped. The freeze was not reopened.

**Why it was worth an arm.** A counterexample is a single finite graph, the class is
enumerable by `nauty-geng -c -d3 -D3`, and — crucially — **connected cubic graphs are
scarce**: 41,301 at n = 18 against 11.7 million connected graphs at n = 10. The scarcity is
what buys reach, and reach was run 1's binding constraint everywhere else.

**Attack.** Exhaustive. For each graph, test for a cycle of length 4, 8, 16, … by bounded
DFS from a canonical anchor (each cycle is discovered from its lowest-numbered vertex, with
all other vertices constrained to be larger, so each is found exactly once per direction).
The routine was cross-checked against an independent permutation-based brute force on 120
graphs before use — the only safeguard available, since no frozen checker covers this target.

| n | connected cubic graphs | counterexamples |
|---|---|---|
| 4, 6, 8, 10 | 26 | 0 |
| 12 | 85 | 0 |
| 14 | 509 | 0 |
| 16 | 4,060 | 0 |
| 18 | 41,301 | 0 |
| **total** | **45,981** | **0** |

**Verdict.** No counterexample at n <= 18. The literature is well ahead of this (the
conjecture is known for various structural classes and has been checked far further), so
this arm reproduces known ground rather than extending it — the honest value is that it
demonstrates the reach that class-scarcity buys: 18 vertices here versus 10 for general graphs.

**Where run 2 should push.** A counterexample must avoid 4-, 8- and 16-cycles at once, so it
must have girth >= 5, and `nauty-geng -c -d3 -D3 -tf` enumerates exactly that much smaller
class. That restriction is the same trick that took WOWII conjecture 141 from n = 10 to
n = 16, and it is the right way to spend the next core-hours here.

**Reproduce.**
`for n in 4 6 8 10 12 14 16 18; do nauty-geng -qc -d3 -D3 $n | ./mine/tools/wowscan --only 901; done`
