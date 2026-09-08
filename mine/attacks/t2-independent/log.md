# Tier 2 — blind independent reimplementation

**What T2 is for.** It catches the case where the constructor and the checker share the
same misreading of a statement. So the agent that performs it must be given the statement
and the witness and **nothing else** — no access to the search code, the frozen checker, or
any of the reasoning that produced the object.

**How it was run.** A fresh agent was given: the natural-language statement of WOWII
conjecture 200 (with l(v), l_avg, tree(G) and "Hamiltonian path" defined in words), the
graph6 string `J^~~u?_C?O?`, and an explicit instruction not to read anything under
`mine/verify/`, `mine/tools/`, `mine/attacks/` or `mine/logs/`. It was told that a
disagreement with the claim would be a valuable finding, not a failure, and that it must
not adjust its checker to make the claim come out true.

**What it did.** Wrote its own graph6 decoder and its own exhaustive checkers in exact
arithmetic (`fractions.Fraction`, no floats), and cross-checked its decoder against
`nauty-listg -a` independently.

**What it found.** Agreement on every value:

| quantity | independent T2 result | frozen checker (T1) |
|---|---|---|
| n | 11 | 11 |
| l(v) multiset | 3,3,3,3,3,2,2,2,1,1,1 (sum 24) | sum 24 |
| l_avg | 24/11 exactly | 24/11 |
| ceil(1 + l_avg) | 4 | 4 |
| tree(G) | 4 | 4 |
| Hamiltonian path | does not exist | does not exist |
| connected | yes | yes |

It also produced the structural argument independently: vertices 8, 9 and 10 are degree-1
leaves attached to three *different* vertices, a Hamiltonian path has only two endpoints,
and every degree-1 vertex must be an endpoint — so no Hamiltonian path can exist. That
argument was not supplied to it.

**Reproduce.** `cd mine/attacks/t2-independent && python3 checker.py`

**Standing caveat.** The object verified here is a counterexample to a conjecture that was
**already refuted in the literature**. T2 passing means the tier works, not that anything
was discovered. Nothing from this directory is in `mine/results/`.
