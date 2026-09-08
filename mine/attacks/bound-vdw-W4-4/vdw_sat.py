#!/usr/bin/env python3
"""SAT encoder for: does an r-colouring of [1,n] with no monochromatic k-term AP exist?

For r=2 uses a single boolean per element (colour 0/1) with two clauses per AP.
For general r uses a one-hot boolean-per-(element,colour) encoding with AMO+ALO
and a negative clause per (AP, colour).

Usage: vdw_sat.py k r n [timeout_seconds]
Writes witness JSON to stdout on SAT, prints UNSAT / timeout on stderr otherwise.
"""
import sys, json, itertools
from pysat.solvers import Cadical153
from pysat.formula import IDPool

def all_aps(n, k):
    for a in range(1, n + 1):
        d = 1
        while True:
            terms = [a + i * d for i in range(k)]
            if terms[-1] > n:
                break
            yield terms
            d += 1

def solve(k, r, n, timeout=None):
    vpool = IDPool()
    def v(i, c):
        return vpool.id(("x", i, c))

    solver = Cadical153()

    if r == 2:
        # single var per element: True=colour0, False=colour1
        def var(i):
            return vpool.id(("x", i))
        for terms in all_aps(n, k):
            lits = [var(t) for t in terms]
            solver.add_clause(lits)          # not all colour1 (i.e. at least one True)
            solver.add_clause([-l for l in lits])  # not all colour0
    else:
        for i in range(1, n + 1):
            lits = [v(i, c) for c in range(r)]
            solver.add_clause(lits)  # at least one colour
            for c1, c2 in itertools.combinations(range(r), 2):
                solver.add_clause([-v(i, c1), -v(i, c2)])  # at most one
        for terms in all_aps(n, k):
            for c in range(r):
                solver.add_clause([-v(t, c) for t in terms])

    sat = solver.solve()
    if not sat:
        return None
    model = set(solver.get_model())
    colouring = []
    for i in range(1, n + 1):
        if r == 2:
            colouring.append(0 if vpool.id(("x", i)) in model else 1)
        else:
            for c in range(r):
                if v(i, c) in model:
                    colouring.append(c)
                    break
    return colouring

if __name__ == "__main__":
    k, r, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    col = solve(k, r, n)
    if col is None:
        print("UNSAT for k=%d r=%d n=%d" % (k, r, n), file=sys.stderr)
        sys.exit(1)
    out = {"family": "vdw", "k": k, "r": r, "n": n, "colouring": col}
    print(json.dumps(out))
