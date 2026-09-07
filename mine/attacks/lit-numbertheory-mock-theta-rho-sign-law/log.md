# lit-numbertheory-mock-theta-rho-sign-law

Agent: A5 (recent-literature finite-witness conjectures). **No frozen checker exists for
this target — the mine's verifier (`mine/verify/`) was built and hash-locked before this
entry was selected, and will not be reopened. Nothing found here can ship as a
`mine/results/` entry in this run. This is exploratory frontier-measurement only.**

## Exact statement (every symbol defined)

Source: arXiv:2606.27902, "Sign law for Ramanujan's third order mock theta function
rho(q)" (Manosij Ghosh Dastidar, submitted 2026-06-26). Corpus entry:
`mine/corpus/raw/h6_literature.jsonl` id `lit-numbertheory-mock-theta-rho-sign-law`.

Define
```
rho(q) = sum_{m>=0}  q^(2m(m+1)) / [ prod_{j=0}^{m} (1 + q^(2j+1) + q^(4j+2)) ]
       = sum_{n>=0}  r(n) q^n
```
(this fixes the integer coefficients r(n) — a formal power series identity, all
coefficients are integers since numerator and each denominator factor are).

**Conjecture**: r(n) > 0 whenever n ≡ 0 (mod 3), and r(n) < 0 whenever n ≡ 1 or 2 (mod 3),
for every n >= 21.

## Open-status check

WebSearch (`arXiv 2606.27902 Sign law Ramanujan third order mock theta function rho(q)`)
confirms the paper: proves the sign law holds "for all sufficiently large n" via a
Rademacher-type asymptotic expansion, without pinning an explicit numeric threshold in
the search snippet. Direct arXiv fetch is blocked at this environment's egress proxy
(`WebFetch` on `arxiv.org/abs/2606.27902` and `arxiv.org/html/2606.27902` both returned
`EGRESS_BLOCKED`, confirming the harvest log's prior finding) — I could not independently
read the paper's own precise cutoff, if it states one at all. **Open-status verdict**:
genuinely open for the exact claim "cutoff is exactly n=21, no exceptions" — the paper's
asymptotic result does not by itself pin down a concrete small threshold, so this is
exactly the kind of residual the mission is designed to attack computationally.

**Definition-precision caveat** (recorded honestly): I could not confirm from search
snippets alone whether the source paper phrases its own numerical observation with
strict or non-strict inequalities at small n (one summary phrase suggested the *empirical*
pattern was first observed as r(3n)>0, r(3n+1)<=0, r(3n+2)<=0, i.e. possibly allowing
r(n)=0, before the paper's asymptotic theorem gives strict inequality for large n). The
corpus's `statement_nl` (and this attack) use the strict form starting at n=21, taken
verbatim from the corpus entry.

## Method

Exact integer power-series arithmetic — no floating point anywhere. Implemented from
scratch (`check.py`):
- `invert_series`: computes 1/(1 + q^(2j+1) + q^(4j+2)) mod q^(N+1) via the standard
  triangular recurrence for a monic power series (a_0=1), using only the 3 nonzero
  coefficients of each factor (cheap).
- `mul_trunc`: truncated power-series multiplication.
- `compute_r(N)`: builds the running product `P_m = prod_{j=0}^m 1/A_j` incrementally
  and accumulates `q^(2m(m+1)) * P_m` into `r`, for every m with `2m(m+1) <= N`.

**Bug caught and fixed during this attack**: an early version added the m-th
contribution using `P` *before* multiplying in the m-th factor (an off-by-one in the
accumulation loop), which produced a coefficient sequence that looked plausible
(similar magnitude, right parity of zeros) but was simply wrong. Caught by
cross-checking the first 31 coefficients against an independent `sympy.series` symbolic
computation of the same defining sum (`sympy.series(1/denom, q, 0, N+1)`), which is the
"fresh independent implementation" sanity check this kind of ad hoc arithmetic code
needs. After the fix, the two implementations agree exactly on all 31 cross-checked
coefficients. This is exactly the failure mode a T2 fresh-checker step would have caught
— recorded here since there is no T2 step in this exploratory run.

Repro:
```
python3 mine/attacks/lit-numbertheory-mock-theta-rho-sign-law/check.py
```

## Frontier reached

- N=400: `r(0..400)` computed exactly, wall time 0.08s. Zero violations of the strict
  sign law for n in [21,400]. Empirically observed minimal n0 such that the strict sign
  law holds for ALL n in [n0,400] is exactly **21** — n=20 itself is a violation
  (r(20)=0, not <0, since 20 ≡ 2 mod 3), matching the conjectured cutoff exactly (not
  just "cutoff <= 21" but "cutoff is exactly 21, sharp").
- N=3000 (ad hoc follow-up, not in the committed script's default but reproducible via
  `python3 -c "from check import compute_r; ..."` with N=3000 — see this log's repro
  note below): wall time 12.8s, zero violations for n in [21,3000].

Repro for the N=3000 run:
```
python3 -c "
import sys; sys.path.insert(0, 'mine/attacks/lit-numbertheory-mock-theta-rho-sign-law')
from check import compute_r
N=3000; r=compute_r(N)
def expected_sign(n): return 1 if n%3==0 else -1
violations=[(n,r[n]) for n in range(21,N+1) if not ((r[n]>0) if expected_sign(n)==1 else (r[n]<0))]
print(len(violations), violations[:10])
"
```

## Wall time

Total agent time on this target: ~9 minutes, including the bug hunt above.

## Verdict

**No counterexample found for n in [21, 3000]** to the strict sign law, and the
empirically observed sharp cutoff (21) matches the conjectured cutoff exactly. This is a
positive computational corroboration, not a proof, and **it cannot ship as a
mine/results/ entry — there is no frozen checker for this target, and this run's
verifier freeze predates this problem's selection.** A genuine attack would need to push
N much further (the series is cheap — O(N) per new m, O(N^2) per multiplication, ~12
active m values for N~400 growing like sqrt(N) — so N=10^5 or more is plausible within
seconds to minutes) or look for a proof of the exact threshold, not brute-force refutation,
since 3000 terms of uniform agreement is strong evidence *for* the conjecture, not against
it. Recommend this as a "confirm, don't refute" target for run-2, ideally with someone who
can read the actual paper (arXiv fetch is blocked here) to check whether it already proves
the n=21 threshold explicitly, which would retire this as already-settled rather than open.

## Negative-memory entry

See `mine/memory/negative-a5.jsonl`: brute-force sign-law refutation up to n=3000 found
nothing; the arm is not flat because it's hard, it's flat because the conjecture appears
true on the range checked — recorded as a "no counterexample, positive signal" result,
distinct from a genuinely stuck/flat arm.
