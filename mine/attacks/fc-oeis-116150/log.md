# fc-oeis-116150 — attack log (agent A6)

**No frozen checker exists for this target. Nothing below can ship into
`mine/results/` this run.** Measured-frontier / run-2-recommendation log only.

Selection rationale for all five A6 targets is recorded in
`mine/attacks/fc-greensopenproblems-16-a/log.md`.

## Statement (pinned from Lean)

Source: `mine/cache/formal-conjectures/FormalConjectures/OEIS/116150.lean`
(namespace `OeisA116150`; OEIS [A116150](https://oeis.org/A116150), egress-blocked so
not fetched directly this session — worked entirely from the cited Lean file).

```
def a (n : ℕ) : ℕ := (∑ j ∈ Finset.Icc 1 n, ((3:ℤ)^j + ((-2):ℤ)^j)).toNat

theorem conjecture :
    answer(sorry) = a (sInf {n : ℕ | 431 < n ∧ (a n).Prime}) := by sorry
```

In plain terms: `a(n) = sum_{j=1}^{n} (3^j + (-2)^j)`, computed in `ℤ` then cast to
`ℕ` (the sum is always non-negative for `n≥1`, verified below). The open question,
pinned exactly by the Lean `sInf`, is: what is `a(n)` for the **smallest** `n > 431`
such that `a(n)` is prime. Every symbol is defined above; there is no free parameter
left unpinned (the "431" is a literal constant in the theorem statement, taken from
the known primes already found by the corpus/OEIS: `a(11), a(17), a(71), a(91),
a(431)`).

The Lean file's own `test`-category theorems pin the small values exactly:
`a(1)=1, a(2)=14, a(3)=33, a(4)=130, a(5)=341` — these were checked (see script) and
matched exactly, so the recurrence used here is confirmed correct against the formal
statement, not just against the informal comment.

## Published frontier

Per the Lean file's docstring (attributed to OEIS A116150): known primes in the
sequence are `a(11)=264353`, `a(17)=193622861`, and (unstated exact values, only
indices given) `a(71)`, `a(91)`, `a(431)`. No prime beyond `a(431)` is recorded
anywhere in the cited file or in `mine/corpus/problems.jsonl`
(`current_bounds: {lower: null, upper: null}`), so "next prime after n=431" is
genuinely open as far as this repo's sources go.

## Computation actually run

Code: `mine/attacks/fc-oeis-116150/search.py`. Exact Python bignum integer arithmetic
throughout (no floats); `a(n)` computed via the linear recurrence
`a(n) = a(n-1) + 3^n + (-2)^n` (O(n) bignum additions instead of the O(n^2) direct
double sum, values identical — this is just an efficiency rewrite of the same
definition, not a different function); primality tested with `sympy.isprime`
(BPSW + Miller-Rabin — an industry-standard, extremely reliable but not a
formally-certified deterministic proof for arbitrary-size integers; flagged since T2/T3
would require an independently-checkable witness, which this is not).

Reproduce: `python3 mine/attacks/fc-oeis-116150/search.py 1500`

Result of that run (full output captured, wall time 0.21s):

```
n=   11  digits=    6  isprime=True
n=   17  digits=    9  isprime=True
n=   71  digits=   35  isprime=True
n=   91  digits=   44  isprime=True
n=  431  digits=  206  isprime=True
--- searching n=432.. for next prime ---
No prime found for 431 < n <= 1500. Elapsed 0.2s
```

All 5 previously-known primes independently reconfirmed exactly. **No prime found for
432 <= n <= 1500** (isprime tested exhaustively over that whole range).

A follow-up run to `n=20000` was launched in the background
(`timeout 300 python3 mine/attacks/fc-oeis-116150/search.py 20000`) to push the
frontier further, but was piped through `tail -60`, which fully buffers non-tty
stdout — no incremental progress lines were flushed before the process was killed at
the 300s timeout, and the coordinator's "stop searching, write up now" instruction
arrived before it could be re-run cleanly. **That run is discarded as inconclusive**
(exit code 143 / killed, "Terminated" is the only captured output) rather than
reported as a data point — per CLAUDE.md's "no unexecuted claims" rule, only the
`n<=1500` result above (whose full output was captured) is claimed.

Total wall time actually charged to this target: 0.21s of confirmed compute time
(the `n<=1500` run), plus ~5 minutes of harness/log time. The `n=20000` attempt does
not count as evidence either way.

## Verdict

**Open beyond n=431. Confirmed clean (no prime) for 432 <= n <= 1500 with exact
bignum arithmetic + probabilistic-primality screening.** No frozen checker exists for
`OeisA116150.a`/`.Prime`, so this cannot ship regardless.

## Run-2 recommendation

This is the cheapest of the five A6 targets to push much further — `a(1500)` is only
~700 digits and `isprime` took a fraction of a second per candidate at that size, so
`n` up to at least 20000-50000 (several-thousand-digit numbers) should be reachable in
single-digit minutes of *actual, uninterrupted, unbuffered* compute; use
`python3 -u` (unbuffered) or write JSON-lines progress to a file instead of piping
through `tail`. If a candidate prime is found, do **not** report it as proved without
a second, independent primality certificate (e.g. a BPSW + trial-division-to-10^6
cross-check, or `sympy.isprime` cross-checked against a second library) given that
`isprime` here is probabilistic for large inputs.
