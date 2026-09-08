"""
Target: lit-numbertheory-overpartition-congruence-mod7
Source corpus entry: mine/corpus/raw/h6_literature.jsonl (arXiv:2603.08510,
"New Ramanujan-type congruences for overpartitions modulo 11 and 13")

Statement (restated exactly, all symbols defined):
  The overpartition function pbar(n) counts overpartitions of n (partitions of n in
  which the first occurrence of a part may be overlined), with generating function
      sum_{n>=0} pbar(n) q^n = prod_{k>=1} (1+q^k)/(1-q^k).
  Conjecture: pbar(2^4 * (56n+k)) = 0 (mod 7) for all n >= 0 and all k in {11, 43, 51}.

This is EXACT integer arithmetic (arbitrary-precision Python ints, no floats, no
modular reduction until the final check -- pbar(m) is computed exactly, then reduced
mod 7, so there is zero risk of a floating-point or premature-reduction error).

Method: standard partition-DP power series computation of
  prod_{k=1}^{K} (1+q^k)/(1-q^k)   (mod q^(M+1))
via two per-k passes: (1+q^k) is a finite-degree polynomial multiply (top-down knapsack
order, in place), 1/(1-q^k) is the standard unbounded-coin partition recurrence
(ascending order, in place). K = M suffices (factors (1+q^k)/(1-q^k) for k>M contribute
only q^k+... which is beyond truncation order M).
"""
import time

def overpartition_coeffs(M):
    c = [0] * (M + 1)
    c[0] = 1
    for k in range(1, M + 1):
        # multiply by (1 + q^k)  (finite polynomial, top-down so we read pre-update values)
        for n in range(M, k - 1, -1):
            c[n] += c[n - k]
        # multiply by 1/(1 - q^k) = sum_i q^(ik)  (unbounded, ascending so updates compound)
        for n in range(k, M + 1):
            c[n] += c[n - k]
    return c

if __name__ == "__main__":
    M = 15000
    t0 = time.time()
    pbar = overpartition_coeffs(M)
    t1 = time.time()

    # sanity check against known OEIS A015128 (overpartition numbers) initial terms:
    # pbar(0..9) = 1, 2, 4, 8, 14, 24, 40, 64, 100, 154
    known = [1, 2, 4, 8, 14, 24, 40, 64, 100, 154]
    sanity_ok = pbar[:10] == known
    print(f"sanity check pbar(0..9) == known OEIS A015128 values: {sanity_ok}")
    print(f"  computed: {pbar[:10]}")
    print(f"  expected: {known}")
    if not sanity_ok:
        raise SystemExit("SANITY CHECK FAILED -- generating function implementation is wrong, halting")

    ks = [11, 43, 51]
    violations = []
    checked = []
    n = 0
    while True:
        any_in_range = False
        for k in ks:
            m = 16 * (56 * n + k)
            if m > M:
                continue
            any_in_range = True
            val = pbar[m]
            ok = (val % 7 == 0)
            checked.append((n, k, m, val % 7, ok))
            if not ok:
                violations.append((n, k, m, val))
        if not any_in_range:
            break
        n += 1

    print(f"\ncomputed pbar(0..{M}) exactly, wall={t1-t0:.2f}s")
    print(f"checked {len(checked)} (n,k) pairs across n=0..{n-1}, k in {ks}")
    print("last 10 checks (n,k,m,pbar(m) mod 7, ok):", checked[-10:])
    if violations:
        print(f"COUNTEREXAMPLES ({len(violations)}):", violations[:10])
    else:
        print("NO COUNTEREXAMPLE found in the checked range")
