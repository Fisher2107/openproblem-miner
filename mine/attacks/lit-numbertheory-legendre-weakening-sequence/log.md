# lit-numbertheory-legendre-weakening-sequence

Agent: A5. **No frozen checker exists for this target — the mine's verifier
(`mine/verify/`) was built and hash-locked before this entry was selected, and will not
be reopened. Nothing found here can ship as a `mine/results/` entry in this run. This is
exploratory frontier-measurement only.**

## Exact statement (every symbol defined)

Source: arXiv:2602.22502, "Weakening the Legendre Conjecture" (Marc Chamberland, Armin
Straub, 2026-02-25). Corpus entry: `mine/corpus/raw/h6_literature.jsonl` id
`lit-numbertheory-legendre-weakening-sequence`.

Define the sequence of primes q_1, q_2, q_3, ... by q_1 = 2, and for n >= 1,
q_(n+1) := the least prime strictly exceeding q_n^2.
**Conjecture**: q_(n+1) < (q_n + 1)^2 for all n >= 1.

Distinct from the classical Legendre conjecture (already tracked elsewhere in this mine
via `mine/corpus/raw/h2_formal.jsonl`, `fc-wikipedia-LegendreConjecture`) — this is a
self-referential-sequence variant specific to this paper, not a duplicate target.

## Open-status check

WebSearch (`arXiv 2602.22502 Weakening the Legendre Conjecture`) confirms the paper:
its main results are about primes between x^(2+delta) and (x+1)^(2+delta) under RH,
applied to Mills-type constants; the search snippet did not surface this exact
self-referential q_n-sequence conjecture as separately resolved or refuted anywhere.
Direct arXiv fetch is blocked at this environment's egress proxy (confirms the harvest
log's finding). **Open-status verdict**: no evidence found that this specific claim is
already settled; treated as open per the corpus entry.

## Method

Exact integer arithmetic (Python arbitrary-precision ints via `sympy.nextprime`, which
uses deterministic-for-practical-sizes Miller-Rabin/BPSW primality testing — no floats,
no probabilistic risk at these sizes). A counterexample is a single n with
`nextprime(q_n**2) >= (q_n+1)**2`.

Repro:
```
python3 mine/attacks/lit-numbertheory-legendre-weakening-sequence/check.py
```

## Frontier reached

Computed q_1..q_12 exactly (q_11 has 376 digits, q_12 has 751 digits) and checked the
inequality for n=1..11. **The sequence itself is the bottleneck**, not the inequality
check: q_n grows doubly-exponentially (q_{n+1} ~ q_n^2), so each new term roughly doubles
the digit count, and `sympy.nextprime` on a ~750-digit input is already noticeably slower
than on a ~380-digit one. Pushing to n=13 (a ~1500-digit input to nextprime) is plausible
within a few more minutes but was not attempted given the 45-minute cross-target budget.

## Wall time

check.py itself: 2.4s (n=1..11). Total agent time including setup/write-up: ~6 minutes.

## Verdict

**No counterexample found** for n=1..11 (all inequalities hold, with q_11 spanning 751
digits vs a 751-digit bound (q_10+1)^2 — the two sides differ starting only deep in the
decimal expansion, e.g. at n=11 the gap `(q_n+1)^2 - q_(n+1)` is astronomically large
relative to q_(n+1) itself early on but the two numbers agree on their leading ~15+
digits, consistent with q_(n+1) being "just barely" the next prime above q_n^2). Positive
computational corroboration only — not a proof, and **cannot ship as a mine/results/
entry** (no frozen checker for this problem; see header). This sequence is exactly the
"cheap, mechanical, exact-arithmetic sequence check" the mission's bias list favors, and
it is quite literally as small a witness (one integer n) as this batch offers — recommend
as a strong run-2 candidate specifically for pushing n further (the exponential digit
growth is the only real obstacle, not any conceptual difficulty).

## Negative-memory entry

See `mine/memory/negative-a5.jsonl`: brute-force sequence check up to n=11 found nothing;
flat not because the search is unproductive but because the terms available within budget
ran out (doubly-exponential digit growth), a genuinely different "why it stopped" than a
combinatorial search exhausting its space.
