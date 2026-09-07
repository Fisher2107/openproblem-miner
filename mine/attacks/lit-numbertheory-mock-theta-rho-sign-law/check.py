"""
Target: lit-numbertheory-mock-theta-rho-sign-law
Source corpus entry: mine/corpus/raw/h6_literature.jsonl (arXiv:2606.27902,
"Sign law for Ramanujan's third order mock theta function rho(q)")

Statement (restated exactly, all symbols defined):
  rho(q) = sum_{m>=0} q^(2m(m+1)) / [ prod_{j=0}^{m} (1 + q^(2j+1) + q^(2*(2j+1))) ]
         = sum_{n>=0} r(n) q^n   (defines the integer coefficients r(n))
  Conjecture: r(n) > 0 when n = 0 (mod 3), r(n) < 0 when n = 1 or 2 (mod 3),
  for every n >= 21.

DEFINITION CHECK: WebSearch of the paper (arxiv.org itself is egress-blocked, confirmed
again here; only search-snippet secondary sources were reachable) returned this summary
of the paper's own wording: "Numerical evidence suggests r(3n)>0, r(3n+1)<=0, r(3n+2)<=0
... [the paper's theorem] shows r(3n)>0, r(3n+1)<0, r(3n+2)<0 for all sufficiently large
n." That is consistent with the corpus's strict-inequality restatement, but the search
snippet did NOT let us independently confirm the exact cutoff n=21 (arxiv.org fetch is
blocked at the egress proxy, so the primary source could not be read). We proceed with
the corpus's stated cutoff n=21 as our target statement, and separately report what the
computation itself finds as the true minimal cutoff -- if the true cutoff we observe
differs from 21, that is itself a useful, reportable calibration finding regardless of
whether we can pin the paper's exact wording.

Method: compute r(n) EXACTLY (integer power-series arithmetic, no floats) via the
q^(2m(m+1))-indexed sum, truncated to a finite order N. For fixed truncation order N,
only finitely many m contribute (those with 2m(m+1) <= N), so this is an exact, finite
computation -- a genuine brute force over the defining series, not a numerical
approximation.
"""
import time

def invert_series(a, N):
    """Given power series coefficients a[0..N] with a[0]==1 (as a dict of nonzero
    coeffs, e.g. {0:1, 2j+1:1, 4j+2:1}), return b[0..N] with a*b = 1 (mod q^(N+1))."""
    b = [0] * (N + 1)
    b[0] = 1
    nz = [(k, v) for k, v in a.items() if k > 0]
    for n in range(1, N + 1):
        s = 0
        for k, v in nz:
            if k <= n:
                s += v * b[n - k]
        b[n] = -s
    return b

def mul_trunc(p, q, N):
    """Multiply two power series truncated to order N (dense lists of length N+1)."""
    r = [0] * (N + 1)
    for i, pi in enumerate(p):
        if pi == 0:
            continue
        maxj = N - i
        for j in range(min(len(q), maxj + 1)):
            qj = q[j]
            if qj:
                r[i + j] += pi * qj
    return r

def compute_r(N):
    """Return r(0..N) as a list of length N+1."""
    P = [0] * (N + 1)
    P[0] = 1  # empty product = 1
    r = [0] * (N + 1)
    m = 0
    while 2 * m * (m + 1) <= N:
        # update P *= 1/(1 + q^(2m+1) + q^(4m+2)) so that after this, P == prod_{j=0}^{m} 1/A_j
        a = {0: 1, 2 * m + 1: 1, 4 * m + 2: 1}
        invA = invert_series(a, N)
        P = mul_trunc(P, invA, N)
        shift = 2 * m * (m + 1)
        for n in range(shift, N + 1):
            r[n] += P[n - shift]
        m += 1
    return r

if __name__ == "__main__":
    N = 400
    t0 = time.time()
    r = compute_r(N)
    t1 = time.time()

    def expected_sign(n):
        m3 = n % 3
        return 1 if m3 == 0 else -1

    violations_strict = []
    for n in range(21, N + 1):
        sgn = expected_sign(n)
        val = r[n]
        ok = (val > 0) if sgn == 1 else (val < 0)
        if not ok:
            violations_strict.append((n, val))

    # also find the true minimal n0 such that the strict sign law holds for ALL n in [n0, N]
    true_n0 = None
    for cand in range(0, N + 1):
        if all((r[n] > 0 if expected_sign(n) == 1 else r[n] < 0) for n in range(cand, N + 1)):
            true_n0 = cand
            break

    print(f"computed r(0..{N}) exactly (integer arithmetic), wall={t1-t0:.2f}s")
    print("first 24 values r(0..23):", r[:24])
    print(f"violations of the CONJECTURED strict sign law for n in [21,{N}]:", violations_strict[:20],
          ("(showing first 20)" if len(violations_strict) > 20 else ""))
    print(f"count of violations in [21,{N}]: {len(violations_strict)}")
    print(f"empirically observed minimal n0 (strict sign law holds for ALL n in [n0,{N}]): {true_n0}")
