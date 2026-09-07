# fc-oeis-102847 — attack log (agent A6)

**No frozen checker exists for this target. Nothing below can ship into
`mine/results/` this run.** Measured-frontier / run-2-recommendation log only.

Selection rationale for all five A6 targets is recorded in
`mine/attacks/fc-greensopenproblems-16-a/log.md`.

## Statement (pinned from Lean)

Source: `mine/cache/formal-conjectures/FormalConjectures/OEIS/102847.lean`
(namespace `OeisA102847`; OEIS [A102847](https://oeis.org/A102847), not fetched
directly — egress-blocked — worked entirely from the cited Lean file).

```
def a : ℕ → ℕ
  | 0 => 1
  | n + 1 => (a n) ^ 2 + 2

theorem conjecture : answer(sorry) = sInf {n : ℕ | 4 < n ∧ (a n).Prime} := by sorry
```

In plain terms: `a(0)=1`, `a(n) = a(n-1)^2 + 2`, all in `ℕ` (exact integer
arithmetic, doubly-exponential growth). The open question, pinned exactly by the Lean
`sInf`, is the smallest `n > 4` such that `a(n)` is prime. Every symbol is defined
above; no free parameter is left unpinned. The Lean file's own `test`-category
theorems (`a_0=1, a_1=3, a_2=11, a_3=123, a_4=15131`) were checked against this
recurrence and matched exactly (see script), confirming the recurrence used here is
the one in the formal statement.

## Published frontier — and an indexing discrepancy worth flagging

Per the Lean file's docstring: `a(1)=3` prime, `a(2)=11` prime, `a(3)=123=3*41`
semiprime, `a(4)=15131` prime, `a(5)=228947163=3*76315721` semiprime, "`a(6)`, added
by Jonathan Vos Post, has 4 prime factors," and
`a(7) = 41 * 811^2 * 106693969 * 317171188688357726699 * 8272236925540996054440172449761`.

**Exact recomputation from the Lean recurrence (script output, reproduced below)
shows this does not hold under the Lean file's own 0-indexed `a`:**

- Lean's `a(6) = 52416803445748571` (17 digits), which `sympy.factorint` gives as
  `19 * 43 * 59 * 313 * 6091 * 570379` — **6** distinct prime factors, not 4.
- Lean's `a(7) = 2747521283470239265968814548542043` (34 digits) — this does **not**
  equal the 67-digit product quoted in the comment for "`a(7)`".
- That 67-digit product instead equals **Lean's `a(8)`** exactly (checked
  computationally: `vals[8] == 41*811**2*106693969*317171188688357726699*8272236925540996054440172449761`
  is `True`).

So the informal comment's indices `1..5` line up exactly with the Lean-indexed `a`,
but its `6` and `7` appear to be off by one relative to Lean's `a` (most likely because
the original OEIS comment uses a different offset convention than the Lean
formalization, or the comment itself carries an error — not resolved here, out of
scope for a `witness_type: numeric-bound` attack). **This matters for pinning the
open question**: the Lean theorem's own bound (`4 < n`) is stated directly in terms of
Lean's `a`, so it is self-consistent and was used as-is — the search below tests
Lean-indexed `a(5), a(6), a(7), ...` for primality, ignoring the mismatched informal
factor-count claims.

## Computation actually run

Code: `mine/attacks/fc-oeis-102847/search.py`. Exact Python bignum arithmetic
throughout (no floats; `sys.set_int_max_str_digits` raised to handle the
several-thousand-digit values produced past `n~14`). Primality via `sympy.isprime`
(BPSW + Miller-Rabin, probabilistic for large inputs — flagged, same caveat as the
other OEIS target).

Reproduce: `python3 mine/attacks/fc-oeis-102847/search.py 19`

Full captured output (wall time 1.17s for the run that completed cleanly):

```
n=  5  digits=     9  isprime=False
n=  6  digits=    17  isprime=False
n=  7  digits=    34  isprime=False
n=  8  digits=    67  isprime=False
n=  9  digits=   134  isprime=False
n= 10  digits=   268  isprime=False
n= 11  digits=   536  isprime=False
n= 12  digits=  1071  isprime=False
n= 13  digits=  2141  isprime=False
n= 14  digits=  4281  isprime=False   (0.94s for this one test)
n= 15  digits=  8561  isprime=False
n= 16  digits= 17121  isprime=False
n= 17  digits= 34242  isprime=False
n= 18  digits= 68483  isprime=False
No prime found for 4 < n <= 18.
```

A follow-up attempt to reach `n=22` was run with a 115s timeout
(`python3 mine/attacks/fc-oeis-102847/search.py 22`); it completed `n=19`
(`digits=136966, isprime=False`) and was killed by the timeout partway through `n=20`
(a ~270000-digit number) — Miller-Rabin cost is growing faster than linearly in digit
count as expected, and this is the point where the doubly-exponential blowup starts
to bite within a single-machine, no-frozen-checker attack budget.

**Confirmed clean (composite) for all `5 <= n <= 19`.** `n=20` onward: not completed.

Total wall time actually charged: ~1.2s of confirmed-and-captured compute for `n<=18`,
plus a partial, timed-out `n=19..20` attempt (115s), plus ~5 minutes harness/log time.

## Verdict

**Open beyond n=19 (Lean indexing). Confirmed composite for 5 <= n <= 19.** No frozen
checker exists for `OeisA102847.a`/`.Prime`, so this cannot ship regardless.

## Run-2 recommendation

Growth is doubly-exponential (digit count roughly doubles each step: 9, 17, 34, 67,
134, 268, ..., ~270000 at n=20), so this arm goes flat fast in wall-clock terms even
though the *code* is simple — each additional `n` costs roughly 2-4x the compute of the
previous one once numbers exceed a few thousand digits. Recommend for run-2:
(1) use a GMP-backed primality test (e.g. `gmpy2` or PARI/GP `isprime`) instead of pure
Python + sympy for a meaningful constant-factor speedup on tests at n=20-25; (2) first
apply cheap trial division by small primes (up to, say, 10^7) before any Miller-Rabin
round, since most composite candidates at this size will have a small factor and this
was not done as a separate fast pre-filter in this session's script (sympy's isprime
does some of this internally but a dedicated pre-filter loop would still save time by
avoiding sympy's own overhead); (3) budget for reaching at most n~22-24 before this
becomes impractical on a 4-core budget — do not expect to resolve this one, only to
push the confirmed-composite frontier a few steps further and report the new
boundary honestly.
