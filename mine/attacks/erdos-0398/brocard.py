"""
Brocard's problem: is there n>7 (other than 4,5,7) with n!+1 = m^2 ?
Incremental factorial with gmpy2 isqrt; big integers dominate cost as n grows.
"""
import time, sys
import gmpy2
from gmpy2 import mpz

def search(nmax):
    fact = mpz(1)
    found = []
    t0 = time.time()
    for n in range(1, nmax+1):
        fact *= n
        if n < 4:
            continue
        x = fact + 1
        r = gmpy2.isqrt(x)
        if r*r == x:
            found.append((n, int(r)))
    t1 = time.time()
    return found, t1-t0

if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    found, dt = search(nmax)
    print(f"checked n=1..{nmax} in {dt:.2f}s")
    print("solutions found:", found)
