# erdos-0366-a — 2-full n with n+1 3-full

Agent: A3. No frozen checker exists for this target — nothing here can ship as a result.
Frontier measurement only. The corpus entry itself flags this statement as
"erdosproblems comment: ambiguous statement" — our research confirms why (see below).

## Statement attacked
Are there any n such that n is 2-full ("powerful": every prime factor exponent >= 2) and
n+1 is 3-full ("cube-full": every prime factor exponent >= 3)?
(erdosproblems.com/366, one of two directions bundled under Erdős problem #366.)

## Important disambiguation found during research
WebSearch initially surfaced "8 (3-full) and 9 (2-full)" and "12167=23^3 (3-full) and
12168=2^3·3^2·13^2 (2-full only)" as if they were relevant examples. We factored both
pairs directly (`sympy`/trial division) to check:
- 12167 = 23^3 → exponent 3 → 3-full. 12168 = 2^3·3^2·13^2 → **min exponent 2** (primes 3
  and 13) → 2-full **but not 3-full**.
- 8 = 2^3 → 3-full. 9 = 3^2 → **2-full but not 3-full**.

Both known pairs have the **larger** number LESS full (only 2-full) than the smaller —
i.e. they answer the *reverse* direction ("n is 3-full, n+1 is 2-full-but-not-3-full",
attributed by WebSearch to Erdős and Graham, with OEIS A060355 reportedly stating no
other example below 10^22 — again via WebSearch snippet, not a primary-source fetch,
network egress to oeis.org was blocked). They do **not** answer erdos-0366-a as literally
stated here (weaker n, stronger n+1) — we independently confirmed this by direct
factorization, not by trusting the WebSearch paraphrase. As stated, 0366-a appears to have
**no known example in the literature we could locate** — a genuinely different, and
apparently harder-to-populate, direction than the one the secondary sources kept
surfacing.

## Search space / witness
Sparse generation as in erdos-0364-a: powerful numbers via a^2*b^3, cube-full numbers via
a^3*b^4*c^5 (standard k-full parametrization). `kfull_gen.py` generates both sets up to N;
`run_kfull_checks.py` scans the powerful set P for any n with n+1 in the cube-full set Q.

## Published frontier
None located for this specific direction (see disambiguation above) — the reverse
direction's OEIS A060355 bound (10^22, per WebSearch, unverified against primary source)
is **not** a valid frontier for this direction and we do not use it as one.

## Our frontier
```
python3 mine/attacks/erdos-0366-a/run_kfull_checks.py 1000000000000
```
N = 10^13: 6,840,384 powerful numbers, 90,619 cube-full numbers — scanned P for n with
n+1 in Q: **none found** (34.03s total). Sanity check of the code against the *reverse*
direction (n 3-full, n+1 2-full-only) on the same generated sets reproduced exactly the
two known literature pairs and no others: `[(8, 9), (12167, 12168)]` up to 10^13,
confirming the generation/membership logic is correct.

## Ratio and verdict
No ratio computable — no published numeric frontier exists for this exact direction as
far as we could determine.

**Verdict**: negative (no example found in either direction we checked, forward or
reverse, beyond the two known reverse-direction pairs) up to our frontier.

## Wall time
~35s of compute, shared with erdos-0364-a/erdos-0366-c code; most time spent
disambiguating the statement via direct factorization rather than trusting secondary
sources.

## Recommended tractability for run 2
**1/10**, and flag for **statement clarification before re-attacking**: the corpus's own
"ambiguous statement" flag is justified — half the tractability score this problem
received was likely earned by the (wrong) direction, where two known small examples exist
and a large verified-empty range is already published. The literal direction in the
Lean statement has neither. A run-2 attacker should first resolve which direction
erdosproblems.com's discussion actually intends (fetch the primary source directly,
which this session's network policy blocked) before spending search budget.
