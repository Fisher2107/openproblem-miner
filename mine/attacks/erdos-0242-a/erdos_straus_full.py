"""
Full (complete, not just sufficient) exhaustive check for a single n:
for x in (n/4, 3n/4], reduce e/M = p/q lowest terms, scan y in (q/p, 2q/p]
computing z in O(1); this is a COMPLETE case analysis for that x (finds a
witness if one exists for that x). Used only for the residual hard
residue class (n = 1 mod 4) where the simple e|M sufficient test in
erdos_straus.py never fires, to get a real (not just heuristic) frontier.
"""
import time, sys
from math import gcd

def find_witness_full(n, x_cap=None):
    xmax = (3*n)//4
    xmin = n//4 + 1
    if x_cap: xmax = min(xmax, xmin + x_cap)
    for x in range(xmin, xmax+1):
        e = 4*x - n
        M = n*x
        g = gcd(e, M)
        p, q = e//g, M//g
        ymin = q//p + 1
        ymax = (2*q)//p
        for y in range(ymin, ymax+1):
            num = p*y - q
            if num <= 0:
                continue
            if (q*y) % num == 0:
                z = (q*y)//num
                if z > y:
                    vals = sorted([x,y,z])
                    a,b,c = vals
                    if len(set(vals))==3 and 4*a*b*c == n*(b*c+a*c+a*b):
                        return (a,b,c)
    return None

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    t0=time.time()
    fail=[]
    for n in range(5, N+1, 4):  # n = 1 mod 4, the hard residue class
        w = find_witness_full(n)
        if w is None:
            fail.append(n)
    t1=time.time()
    print(f"n=1 mod 4 up to {N}: {t1-t0:.2f}s, unresolved: {fail}")
