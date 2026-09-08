"""
Erdos-Straus: for every n>2, does 4/n = 1/x+1/y+1/z have a solution in
distinct positive integers 1<=x<y<z ?

Complete x-range for a solution (if x is the smallest of the three
denominators): n/4 < x <= 3n/4 (since 1/x < 4/n and 1/x >= (4/n)/3).

For fixed x, let e = 4x-n, M = n*x. Remaining fraction to split into two
DISTINCT unit fractions y<z is e/M. We use the SUFFICIENT (not just
necessary) witness family: if e | M, let w = M//e (so e/M = 1/w exactly);
then split 1/w = 1/(w+1) + 1/(w(w+1)) (always valid, always distinct from
w+1 for w>=1), giving a 3-term distinct representation
  4/n = 1/x + 1/(w+1) + 1/(w(w+1)).
This is a real witness whenever found (checked exactly with integer
arithmetic) -- but scanning only e|M (not the fully general divisor-pair
condition on M^2) means a "not found in range" result here does NOT prove
non-existence; it only means our search didn't resolve n. We report the
frontier as the largest N such that EVERY n in [3,N] got a witness by this
method (honest: some individual n mid-range may have failed and needed the
brute continuation to the very end of the x-range, which we allow).
"""
import time, sys

def find_witness(n):
    xmax = (3*n)//4
    xmin = n//4 + 1
    for x in range(xmin, xmax+1):
        e = 4*x - n
        M = n*x
        if M % e == 0:
            w = M // e
            y, z = w+1, w*(w+1)
            # sanity check + distinctness + ordering
            vals = sorted([x, y, z])
            if len(set(vals)) == 3:
                a,b,c = vals
                # verify exactly with integer cross-multiplication
                # 4*b*c*a == n*(b*c+a*c+a*b)  <=> 4/n == 1/a+1/b+1/c
                lhs = 4*a*b*c
                rhs = n*(b*c + a*c + a*b)
                if lhs == rhs:
                    return (a,b,c)
    return None

def scan(N):
    t0 = time.time()
    fail = []
    for n in range(3, N+1):
        w = find_witness(n)
        if w is None:
            fail.append(n)
    t1 = time.time()
    return fail, t1-t0

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    fail, dt = scan(N)
    print(f"scanned n=3..{N} in {dt:.2f}s; unresolved (not necessarily counterexamples): {fail[:50]} total={len(fail)}")
