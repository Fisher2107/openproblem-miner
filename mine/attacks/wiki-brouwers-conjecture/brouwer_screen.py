#!/usr/bin/env python3
"""Screen for Brouwer's conjecture violations: sum of t largest Laplacian
eigenvalues <= m + C(t+1,2), for every t=1..n.
Stage 1 (numpy float): compute Laplacian eigenvalues, flag near-violations
(margin < tol).
Stage 2 (sympy exact): for any flagged graph, recompute the Laplacian
characteristic polynomial exactly (integer matrix, exact rational/algebraic
eigenvalues via sympy) and re-check the inequality with exact arithmetic.
"""
import sys, time
import numpy as np
import networkx as nx
from math import comb

def laplacian_dense(G):
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    A = np.zeros((n, n))
    for u, v in G.edges():
        A[idx[u], idx[v]] = 1
        A[idx[v], idx[u]] = 1
    D = np.diag(A.sum(axis=1))
    return D - A

def screen_numpy(G, tol=1e-6):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    L = laplacian_dense(G)
    eigs = np.sort(np.linalg.eigvalsh(L))[::-1]  # descending
    viol = []
    running = 0.0
    for t in range(1, n+1):
        running += eigs[t-1]
        bound = m + comb(t+1, 2)
        margin = bound - running
        if margin < tol:
            viol.append((t, running, bound, margin))
    return viol, eigs

def exact_recheck(G):
    import sympy as sp
    n = G.number_of_nodes()
    m = G.number_of_edges()
    L = laplacian_dense(G).astype(int)
    Lm = sp.Matrix(L.tolist())
    eigs_exact = []
    # exact eigenvalues via sympy (algebraic numbers), sorted descending
    ev = Lm.eigenvals()  # dict eigenvalue->multiplicity
    for val, mult in ev.items():
        for _ in range(mult):
            eigs_exact.append(val)
    eigs_exact_sorted = sorted(eigs_exact, key=lambda x: sp.N(x), reverse=True)
    viol = []
    running = sp.Integer(0)
    for t in range(1, n+1):
        running = running + eigs_exact_sorted[t-1]
        bound = m + comb(t+1, 2)
        margin = sp.simplify(bound - running)
        if sp.N(margin) < 1e-9:
            viol.append((t, sp.N(running), bound, sp.N(margin)))
    return viol

def main():
    n_checked = 0
    n_flagged = 0
    t0 = time.time()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        G = nx.from_graph6_bytes(line.encode())
        viol, eigs = screen_numpy(G)
        n_checked += 1
        if viol:
            n_flagged += 1
            print(f"FLAGGED (float near-violation): {line} n={G.number_of_nodes()} m={G.number_of_edges()} viol={viol}", flush=True)
            exact = exact_recheck(G)
            if exact:
                print(f"  EXACT RECHECK CONFIRMS near-violation: {exact}", flush=True)
            else:
                print(f"  exact recheck: float artefact, no real violation", flush=True)
        if n_checked % 2000 == 0:
            print(f"...checked {n_checked}, flagged {n_flagged}, {time.time()-t0:.1f}s", file=sys.stderr, flush=True)
    print(f"DONE checked={n_checked} flagged={n_flagged} time={time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()
