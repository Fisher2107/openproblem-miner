#!/usr/bin/env python3
"""SAT encoder: does an r-colouring of [1,n] with no monochromatic x+y=z (x<=y, x,y,z in
[1,n]) exist? Standard Schur condition (x=y allowed), matching the frozen checker
check_schur_lower.py exactly.

Usage: schur_sat.py r n [timeout via external `timeout` cmd]
Prints witness JSON on SAT to stdout; UNSAT message to stderr + exit 1 otherwise.
"""
import sys, json, itertools
from pysat.solvers import Cadical153
from pysat.formula import IDPool

def solve(r, n):
    vpool = IDPool()
    def v(i, c):
        return vpool.id(("x", i, c))
    solver = Cadical153()
    for i in range(1, n + 1):
        lits = [v(i, c) for c in range(r)]
        solver.add_clause(lits)
        for c1, c2 in itertools.combinations(range(r), 2):
            solver.add_clause([-v(i, c1), -v(i, c2)])
    for x in range(1, n + 1):
        for y in range(x, n + 1):
            z = x + y
            if z > n:
                break
            for c in range(r):
                solver.add_clause([-v(x, c), -v(y, c), -v(z, c)])
    sat = solver.solve()
    if not sat:
        return None
    model = set(solver.get_model())
    col = []
    for i in range(1, n + 1):
        for c in range(r):
            if v(i, c) in model:
                col.append(c)
                break
    return col

if __name__ == "__main__":
    r, n = int(sys.argv[1]), int(sys.argv[2])
    col = solve(r, n)
    if col is None:
        print("UNSAT for r=%d n=%d" % (r, n), file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"family": "schur", "r": r, "n": n, "colouring": col}))
