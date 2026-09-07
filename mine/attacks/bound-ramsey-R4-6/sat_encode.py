#!/usr/bin/env python3
"""SAT encoding of 'does an (s,t,n)-Ramsey graph exist' -- rung 3 of the attack ladder.

One boolean variable per edge {i,j} of K_n (True = edge present / colour A).
For every s-subset: at least one non-edge among its pairs (forbid monochromatic K_s).
For every t-subset: at least one edge among its pairs (forbid independent t-set / K_t
in the complement colour).

This is deliberately the exact same semantics as
mine/verify/checkers/check_ramsey_lower.py so that a SAT model, if found, produces a
witness the frozen checker can accept unmodified.

Usage: python3 sat_encode.py <s> <t> <n> [solve_timeout_seconds]
Prints timing for clause generation and (if attempted) solve time / result.
"""
import sys, time, json, os
from itertools import combinations

def var(i, j, n, idx):
    return idx[(i, j)]

def build_cnf(s, t, n):
    idx = {}
    k = 1
    for i, j in combinations(range(n), 2):
        idx[(i, j)] = k
        k += 1
    nvars = k - 1
    clauses = []
    t0 = time.time()
    for c in combinations(range(n), s):
        clause = []
        for i, j in combinations(c, 2):
            a, b = (i, j) if i < j else (j, i)
            clause.append(-idx[(a, b)])   # at least one pair NOT both-edge -> forbid all-edge (clique)
        clauses.append(clause)
    t1 = time.time()
    for c in combinations(range(n), t):
        clause = []
        for i, j in combinations(c, 2):
            a, b = (i, j) if i < j else (j, i)
            clause.append(idx[(a, b)])    # at least one pair IS an edge -> forbid all-nonedge (indep set)
        clauses.append(clause)
    t2 = time.time()
    print("nvars=%d nclauses=%d (K%d-clauses gen in %.2fs, I%d-clauses gen in %.2fs)" %
          (nvars, len(clauses), s, t1 - t0, t, t2 - t1))
    return nvars, clauses, idx

if __name__ == "__main__":
    s, t, n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    solve_timeout = float(sys.argv[4]) if len(sys.argv) > 4 else None
    t0 = time.time()
    nvars, clauses, idx = build_cnf(s, t, n)
    print("total build wall time: %.2fs" % (time.time() - t0))
    if solve_timeout is None:
        sys.exit(0)
    from pysat.solvers import Cadical153
    import threading
    solver = Cadical153(bootstrap_with=clauses)
    result = {}
    def run():
        result['sat'] = solver.solve()
    th = threading.Thread(target=run, daemon=True)
    t_solve0 = time.time()
    th.start()
    th.join(timeout=solve_timeout)
    elapsed = time.time() - t_solve0
    if th.is_alive():
        print("SOLVE TIMEOUT after %.1fs (no result within budget)" % elapsed)
        solver.interrupt()
        sys.exit(3)
    else:
        print("SOLVE finished in %.1fs: sat=%s" % (elapsed, result.get('sat')))
        if result.get('sat'):
            model = solver.get_model()
            positive = set(l for l in model if l > 0)
            edges = [ (i,j) for (i,j),v in idx.items() if v in positive ]
            outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "sat_model_s%d_t%d_n%d.json" % (s,t,n))
            json.dump({"family":"ramsey","s":s,"t":t,"n":n,"edges":edges}, open(outpath,"w"))
            print("wrote", outpath)
