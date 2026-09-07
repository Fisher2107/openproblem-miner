#!/usr/bin/env python3
"""Cross-check every invariant the C screener relies on against the FROZEN exact library.

The screener's gates are simple arithmetic on these invariants, so if the invariants agree
on a broad sample the gates are trustworthy; if they disagree anywhere, the screener's
"no candidates" output means nothing. Run: python3 mine/tools/crosscheck_invariants.py [n] [sample]
"""
import subprocess, sys, random, os
from fractions import Fraction
sys.path.insert(0, "mine/verify/lib")
import exactgraph as E

n = int(sys.argv[1]) if len(sys.argv) > 1 else 9
sample = int(sys.argv[2]) if len(sys.argv) > 2 else 300
all_g = subprocess.run(["nauty-geng", "-qc", str(n)], capture_output=True, text=True).stdout.split()
random.seed(20260906)
gs = random.sample(all_g, min(sample, len(all_g)))
dump = subprocess.run(["./mine/tools/wowscan", "--dump"], input="\n".join(gs),
                      capture_output=True, text=True).stdout.strip().split("\n")

bad, checked = [], 0
for line in dump:
    parts = line.split()
    g6 = parts[0]
    c = dict(p.split("=") for p in parts[1:] if "=" in p)
    N, adj = E.decode_graph6(g6)
    lv = [E.indep_neighbors_card(N, adj, v) for v in range(N)]
    tri = [E.num_triangles_at_vertex(N, adj, v) for v in range(N)]
    ecc = E.eccentricities(N, adj)
    g = E.girth(N, adj)
    want = {
        "n": N,
        "alpha": E.independence_number(N, adj),
        "maxL": max(lv), "sumL": sum(lv),
        "maxT": max(tri), "minT": min(tri),
        "freqT": sum(1 for t in tri if t == min(tri)),
        "cC4": 0 if E.has_cycle_of_length_4(N, adj) else 1,
        "diam": max(ecc), "rad": min(ecc), "sumEcc": sum(ecc),
        "girth": -1 if g is None else g,
        "Ls": E.max_leaf_spanning_tree(N, adj),
        "f": E.largest_induced_forest_size(N, adj),
        "b": E.largest_induced_bipartite_size(N, adj),
        "tree": E.largest_induced_tree_size(N, adj),
        "path": E.largest_induced_path_size(N, adj),
        "gt": E.total_domination_number(N, adj) or -1,
        "res": E.residue(N, adj),
        "hh": E.havel_hakimi_zero_index(N, adj),
        "ham": 1 if E.has_hamiltonian_path(N, adj) else 0,
        "mtdsdiff": 0 if E.is_well_totally_dominated(N, adj) else 1,
    }
    for k, v in want.items():
        if int(c[k]) != int(v):
            bad.append("%s %s: C=%s exact=%s" % (g6, k, c[k], v))
    checked += 1

print("cross-checked %d graphs on n=%d, %d invariant(s) each" % (checked, n, len(want)))
if bad:
    print("MISMATCHES (%d):" % len(bad))
    for b in bad[:25]:
        print("  " + b)
    sys.exit(1)
print("SCREENER INVARIANTS AGREE WITH THE FROZEN EXACT LIBRARY on every sampled graph.")
