#!/usr/bin/env python3
"""Random-sample screen for Brouwer's conjecture past the published
exhaustive frontier (n<=11, Brouwer's own computation). Exhaustive
enumeration beyond n=11 is infeasible (>10^9 unlabeled graphs at n=11
already), so this is a targeted random probe across n=12..40 and several
random graph models, float-screened with numpy and exact-rechecked with
sympy on any near-violation.
"""
import random, time
import numpy as np
import networkx as nx
from brouwer_screen import screen_numpy, exact_recheck

random.seed(20260907)

def gen_graphs(n, k):
    out = []
    for _ in range(k):
        p = random.choice([0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
        out.append(nx.gnp_random_graph(n, p, seed=random.randint(0, 10**9)))
    # a couple of structured extremal-flavoured families known to be tight/near-tight
    out.append(nx.star_graph(n-1))
    out.append(nx.complete_graph(n))
    out.append(nx.turan_graph(n, max(2, n // 3)))
    if n % 2 == 0:
        out.append(nx.random_regular_graph(min(n-1, 6), n, seed=1))
    out.append(nx.barbell_graph(n // 2, n - n // 2 - 2) if n // 2 >= 2 else nx.path_graph(n))
    return out

def main():
    t0 = time.time()
    n_checked = 0
    n_flagged = 0
    for n in list(range(12, 41, 2)):
        for G in gen_graphs(n, 40):
            if G.number_of_nodes() == 0 or not nx.is_connected(G):
                continue
            n_checked += 1
            viol, eigs = screen_numpy(G)
            if viol:
                n_flagged += 1
                print(f"FLAGGED n={n} m={G.number_of_edges()} viol={viol}")
                exact = exact_recheck(G)
                print(f"  exact recheck: {exact if exact else 'float artefact only, no real violation'}")
    print(f"DONE checked={n_checked} flagged={n_flagged} time={time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
