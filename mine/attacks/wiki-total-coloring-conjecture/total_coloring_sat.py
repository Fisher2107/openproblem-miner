#!/usr/bin/env python3
"""Exhaustive SAT search for total-coloring-conjecture counterexamples.
For each graph read from stdin (graph6 lines), test whether it admits a
total coloring with Delta(G)+2 colors. Report any graph where the SAT
solver returns UNSAT with k=Delta+2 colors (a candidate counterexample).
"""
import sys, time
import networkx as nx
from pysat.formula import IDPool
from pysat.solvers import Glucose3

def total_colorable(G, k):
    vp = IDPool()
    def xv(v, c):
        return vp.id(('v', v, c))
    def ye(e, c):
        return vp.id(('e', e, c))
    edges = list(G.edges())
    cnf = []
    # each vertex exactly one color
    for v in G.nodes():
        lits = [xv(v, c) for c in range(k)]
        cnf.append(lits)
        for i in range(k):
            for j in range(i+1, k):
                cnf.append([-lits[i], -lits[j]])
    # each edge exactly one color
    for e in edges:
        lits = [ye(e, c) for c in range(k)]
        cnf.append(lits)
        for i in range(k):
            for j in range(i+1, k):
                cnf.append([-lits[i], -lits[j]])
    # adjacent vertices differ
    for (u, v) in edges:
        for c in range(k):
            cnf.append([-xv(u, c), -xv(v, c)])
    # incident edges differ (share a vertex)
    inc = {v: [] for v in G.nodes()}
    for e in edges:
        inc[e[0]].append(e)
        inc[e[1]].append(e)
    for v in G.nodes():
        es = inc[v]
        for i in range(len(es)):
            for j in range(i+1, len(es)):
                for c in range(k):
                    cnf.append([-ye(es[i], c), -ye(es[j], c)])
    # vertex and incident edge differ
    for v in G.nodes():
        for e in inc[v]:
            for c in range(k):
                cnf.append([-xv(v, c), -ye(e, c)])
    with Glucose3(bootstrap_with=cnf) as m:
        return m.solve()

def main():
    n_checked = 0
    n_skipped_wrong_delta = 0
    t0 = time.time()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        G = nx.from_graph6_bytes(line.encode())
        degs = [d for _, d in G.degree()]
        Delta = max(degs)
        if Delta < 6:
            n_skipped_wrong_delta += 1
            continue  # Delta<=5 already a theorem (Kostochka et al.); only Delta=6 is open
        k = Delta + 2
        sat = total_colorable(G, k)
        n_checked += 1
        if not sat:
            print(f"COUNTEREXAMPLE CANDIDATE: {line} Delta={Delta} k={k} UNSAT", flush=True)
        if n_checked % 500 == 0:
            print(f"...checked {n_checked} graphs, {time.time()-t0:.1f}s", file=sys.stderr, flush=True)
    print(f"DONE checked={n_checked} time={time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()
