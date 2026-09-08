#!/usr/bin/env python3
"""CEGAR SAT search for linear-arboricity-conjecture counterexamples.
For each graph from stdin (graph6), with Delta(G)=D, test whether edges can
be partitioned into ceil((D+1)/2) linear forests (max degree<=2 per class,
AND acyclic per class). Encoded as: SAT for max-degree<=2 per color, then
check each color class for cycles; if found, add a blocking clause
forbidding that exact edge set from being monochromatic, and re-solve
(CEGAR loop). Report UNSAT (no linear-forest decomposition found) as a
candidate counterexample.
"""
import sys, time, math
import networkx as nx
from pysat.formula import IDPool
from pysat.solvers import Glucose3

def find_cycles_in_color_class(G, edges_of_color):
    H = nx.Graph()
    H.add_edges_from(edges_of_color)
    cycles = []
    try:
        cyc = nx.find_cycle(H)
        cycles.append([tuple(sorted(e[:2])) for e in cyc])
    except nx.NetworkXNoCycle:
        pass
    return cycles

def linear_arb_decomposable(G, k, max_iters=200):
    vp = IDPool()
    edges = [tuple(sorted(e)) for e in G.edges()]
    def y(e, c):
        return vp.id(('e', e, c))
    cnf = []
    # each edge exactly one color
    for e in edges:
        lits = [y(e, c) for c in range(k)]
        cnf.append(lits)
        for i in range(k):
            for j in range(i+1, k):
                cnf.append([-lits[i], -lits[j]])
    # each vertex has degree <=2 in each color: at most 2 of its incident edges share color c
    inc = {v: [] for v in G.nodes()}
    for e in edges:
        inc[e[0]].append(e)
        inc[e[1]].append(e)
    for v in G.nodes():
        es = inc[v]
        for c in range(k):
            lits = [y(e, c) for e in es]
            # at most 2: for every 3-subset, not all true
            if len(lits) > 2:
                from itertools import combinations
                for trio in combinations(lits, 3):
                    cnf.append([-trio[0], -trio[1], -trio[2]])
    extra_clauses = []
    with Glucose3(bootstrap_with=cnf) as m:
        for it in range(max_iters):
            if not m.solve(assumptions=[]):
                return False, it  # UNSAT even before acyclicity -> genuinely impossible
            model = set(x for x in m.get_model() if x > 0)
            # build color classes
            color_edges = {c: [] for c in range(k)}
            for e in edges:
                for c in range(k):
                    if y(e, c) in model:
                        color_edges[c].append(e)
                        break
            found_cycle = False
            for c in range(k):
                cycles = find_cycles_in_color_class(G, color_edges[c])
                for cyc in cycles:
                    found_cycle = True
                    # blocking clause: not all these edges have color c simultaneously
                    m.add_clause([-y(e, c) for e in cyc])
            if not found_cycle:
                return True, it  # valid linear-forest decomposition found
        return None, max_iters  # inconclusive within iteration budget

def main():
    n_checked = 0
    n_skipped = 0
    t0 = time.time()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        G = nx.from_graph6_bytes(line.encode())
        degs = [d for _, d in G.degree()]
        Delta = max(degs)
        target_open_delta = int(sys.argv[1]) if len(sys.argv) > 1 else 7
        if Delta != target_open_delta:
            n_skipped += 1
            continue
        k = (Delta + 2) // 2  # ceil((Delta+1)/2)
        ok, iters = linear_arb_decomposable(G, k)
        n_checked += 1
        if ok is False:
            print(f"COUNTEREXAMPLE CANDIDATE: {line} Delta={Delta} k={k} UNSAT", flush=True)
        elif ok is None:
            print(f"INCONCLUSIVE (cegar budget exhausted): {line} Delta={Delta} k={k}", flush=True)
        if n_checked % 200 == 0:
            print(f"...checked {n_checked} graphs, {time.time()-t0:.1f}s", file=sys.stderr, flush=True)
    print(f"DONE checked={n_checked} skipped={n_skipped} time={time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()
