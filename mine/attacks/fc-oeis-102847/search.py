#!/usr/bin/env python3
"""
fc-oeis-102847: a(0)=1, a(n) = a(n-1)^2 + 2  (N -> N, natural-number arithmetic, exact).

Lean source: mine/cache/formal-conjectures/FormalConjectures/OEIS/102847.lean
    def a : N -> N | 0 => 1 | n+1 => (a n)^2 + 2

Known: a(1)=3 (prime), a(2)=11 (prime), a(3)=123=3*41, a(4)=15131 (prime),
a(5)=228947163=3*76315721, a(6) has 4 prime factors (composite),
a(7) = 41 * 811^2 * 106693969 * 317171188688357726699 * 8272236925540996054440172449761
  (composite, 34 digits).
Open question: sInf {n : N | 4 < n and (a n).Prime} -- next n>4 with a(n) prime.

a(n) grows doubly-exponentially: digits(a(n)) ~ 2 * digits(a(n-1)), so a(8) has ~68
digits, a(9) ~136, a(10) ~272, a(11) ~544, a(12) ~1088, a(13) ~2176, a(14) ~4352,
a(15) ~8704 digits, etc. Miller-Rabin/BPSW primality testing scales roughly like
digits^2-ish per test with Python bignums (or better with GMP-backed libs), so we can
push this a fair distance within the time budget, but not indefinitely.
"""
import sys, time
sys.set_int_max_str_digits(2_000_000)
from sympy import isprime

def a_upto(N):
    vals = {0: 1}
    cur = 1
    for n in range(1, N + 1):
        cur = cur * cur + 2
        vals[n] = cur
    return vals

def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    t0 = time.time()
    vals = a_upto(N)
    known = {0: 1, 1: 3, 2: 11, 3: 123, 4: 15131}
    for k, v in known.items():
        assert vals[k] == v, (k, vals[k], v)
    print("sanity check against Lean a_0..a_4 tests: OK")
    # NOTE: corpus statement_nl claims "a(7) = 41 * 811^2 * 106693969 * ...
    # * 8272236925540996054440172449761" (a 67-digit product) and "a(6) has 4 prime
    # factors". Neither matches the Lean-indexed a(6)/a(7) computed here (a(6) is a
    # 17-digit number with 6 DISTINCT prime factors 19,43,59,313,6091,570379; a(7) is a
    # 34-digit number). The 67-digit product instead matches Lean's a(8) exactly. This
    # looks like an off-by-one shift in the informal OEIS-derived comment for n>=6 (the
    # comment's "a(1)..a(5)" match the Lean-indexed a_1..a_5 exactly, but "a(6)","a(7)"
    # do not). We defer entirely to the Lean definition/recurrence and its own bound
    # (4 < n), which is unambiguous, and flag this discrepancy in log.md.
    a8_matches_claimed_a7_text = (
        vals[8] == 41 * 811**2 * 106693969 * 317171188688357726699
        * 8272236925540996054440172449761
    )
    print(f"corpus-quoted 'a(7)' factorization actually equals Lean a(8): {a8_matches_claimed_a7_text}")
    found = None
    for n in range(5, N + 1):
        d = len(str(vals[n]))
        tstart = time.time()
        p = isprime(vals[n])
        dt = time.time() - tstart
        print(f"n={n:3d}  digits={d:6d}  isprime={p}   (test took {dt:.2f}s)")
        if p:
            found = n
            break
    if found is None:
        print(f"No prime found for 4 < n <= {N}. Elapsed {time.time()-t0:.1f}s")
    else:
        print(f"FOUND: a({found}) is prime.")
    print(f"Total wall time: {time.time()-t0:.2f}s")

if __name__ == "__main__":
    main()
