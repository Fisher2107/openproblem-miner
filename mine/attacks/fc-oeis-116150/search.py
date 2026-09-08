#!/usr/bin/env python3
"""
fc-oeis-116150: a(n) = sum_{j=1}^n (3^j + (-2)^j), a : N -> N (via .toNat, and the sum
is always nonnegative for n>=1 as verified below).

Lean source: mine/cache/formal-conjectures/FormalConjectures/OEIS/116150.lean
    def a (n : N) : N := (sum_{j=1}^n ((3:Z)^j + (-2:Z)^j)).toNat

Known primes (from corpus / Lean comment): a(11)=264353, a(17)=193622861,
a(71), a(91), a(431).
Open question: sInf {n : N | 431 < n and (a n).Prime} -- i.e. what is the next n>431
with a(n) prime.

This script computes a(n) with EXACT PYTHON INTEGER ARITHMETIC (no floats) and tests
primality with sympy.isprime (BPSW + Miller-Rabin, standard industrial primality test;
not a formally certified deterministic proof for arbitrary size, so we also record
which witnesses we'd want independently certified e.g. by a second checker/ECPP for
the record before this could ever ship -- it cannot ship regardless, no frozen checker
exists for this target).
"""
import sys, time
from sympy import isprime

def a(n):
    # exact integer sum, matches Lean def literally (Int arithmetic then toNat)
    s = 0
    for j in range(1, n + 1):
        s += 3 ** j + (-2) ** j
    assert s >= 0
    return s

def a_upto(N):
    """Compute a(1..N) via the recurrence a(n) = a(n-1) + 3^n + (-2)^n, O(N) bignum adds
    instead of O(N^2)."""
    vals = {}
    s = 0
    p3 = 1
    p2 = 1
    for j in range(1, N + 1):
        p3 *= 3
        p2 *= -2
        s += p3 + p2
        vals[j] = s
    return vals

def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    t0 = time.time()
    vals = a_upto(N)
    # sanity check against the Lean `theorem a_k` test values
    known = {1: 1, 2: 14, 3: 33, 4: 130, 5: 341}
    for k, v in known.items():
        assert vals[k] == v, (k, vals[k], v)
    known_primes_claimed = [11, 17, 71, 91, 431]
    for n in known_primes_claimed:
        p = isprime(vals[n])
        print(f"n={n:5d}  digits={len(str(vals[n])):5d}  isprime={p}")
        if not p:
            print("  !! discrepancy: corpus claims this is prime but isprime() disagrees")
    print("--- searching n=432.. for next prime ---")
    found = None
    for n in range(432, N + 1):
        if isprime(vals[n]):
            found = n
            print(f"FOUND next prime at n={n}, digits={len(str(vals[n]))}")
            break
        if n % 200 == 0:
            print(f"  ...checked up to n={n}, {time.time()-t0:.1f}s elapsed, no prime yet")
    if found is None:
        print(f"No prime found for 431 < n <= {N}. Elapsed {time.time()-t0:.1f}s")
    else:
        print(f"a({found}) = {vals[found]}")
    print(f"Total wall time: {time.time()-t0:.2f}s, searched n up to {N}")

if __name__ == "__main__":
    main()
