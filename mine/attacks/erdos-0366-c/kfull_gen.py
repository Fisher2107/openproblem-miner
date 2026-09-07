"""
Generate all k-full numbers <= N via the standard parametrization
n = a_k^k * a_{k+1}^{k+1} * ... * a_{2k-1}^{2k-1}
(every k-full number has such a representation; conversely every number of
this form is k-full). For k=2 (powerful): n = a^2 * b^3.
For k=3 (cube-full): n = a^3 * b^4 * c^5.

This is a sparse generation (total operation count converges, roughly
O(N^{1/k}) up to log factors) so it reaches far larger N than any sieve
over all integers up to N.
"""
import numpy as np
import time

def powerful_upto(N):
    """All n<=N with n=a^2*b^3 (2-full / 'powerful'), as a sorted unique np array."""
    chunks = []
    b = 1
    while b**3 <= N:
        rem = N // (b**3)
        if rem >= 1:
            amax = int(rem**0.5)
            while amax*amax > rem: amax -= 1
            while (amax+1)*(amax+1) <= rem: amax += 1
            a = np.arange(1, amax+1, dtype=np.int64)
            vals = (a*a) * (b**3)
            chunks.append(vals)
        b += 1
    if not chunks:
        return np.array([], dtype=np.int64)
    return np.unique(np.concatenate(chunks))

def cubefull_upto(N):
    """All n<=N with n=a^3*b^4*c^5 (3-full / 'cube-full'), as a sorted unique np array."""
    chunks = []
    c = 1
    while c**5 <= N:
        rem_c = N // (c**5)
        b = 1
        while b**4 <= rem_c:
            rem_b = rem_c // (b**4)
            if rem_b >= 1:
                amax = round(rem_b ** (1/3)) + 2
                while amax**3 > rem_b: amax -= 1
                while (amax+1)**3 <= rem_b: amax += 1
                a = np.arange(1, amax+1, dtype=np.int64)
                vals = (a**3) * (b**4) * (c**5)
                chunks.append(vals)
            b += 1
        c += 1
    if not chunks:
        return np.array([], dtype=np.int64)
    return np.unique(np.concatenate(chunks))

if __name__ == "__main__":
    import sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10**9
    t0 = time.time()
    P = powerful_upto(N)
    t1 = time.time()
    print(f"powerful_upto({N}): {len(P)} numbers, {t1-t0:.2f}s")
    Q = cubefull_upto(N)
    t2 = time.time()
    print(f"cubefull_upto({N}): {len(Q)} numbers, {t2-t1:.2f}s")
