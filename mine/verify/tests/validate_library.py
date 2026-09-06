#!/usr/bin/env python3
"""Freeze-time validation of mine/verify/lib/exactgraph.py.

Three independent kinds of evidence, because an unvalidated checker manufactures
confidence and is worse than no checker at all:

  (1) hand-computed invariant values on textbook reference graphs;
  (2) the ONE identity the library relies on instead of a literal definition
      (Ls = n - gamma_c) checked against brute-force spanning-tree enumeration for
      EVERY connected graph on 3..7 vertices;
  (3) the minimality shortcut used by is_well_totally_dominated (single-vertex
      deletion) checked against the literal "every proper subset" definition for
      every connected graph on 2..6 vertices;
  (4) the graph6 decoder checked against nauty's own listg output.

Exits 0 iff every check passes.
"""
import subprocess
import sys
import os
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import exactgraph as E     # noqa: E402

fails = []


def check(label, got, want):
    if got != want:
        fails.append("%s: got %r want %r" % (label, got, want))


# ------------------------------------------------------------------ (1) reference graphs
REF = {
    # graph6            name        n   m  alpha  Ls  diam rad girth  b   f  tree path residue
    "IheA@GUAo": ("Petersen",      10, 15,   4,   6,   2,  2,    5,  7,  7,   7,   5,     3),
    "DUW":       ("C5",             5,  5,   2,   2,   2,  2,    5,  4,  4,   4,   4,     2),
    "C~":        ("K4",             4,  6,   1,   3,   1,  1,    3,  2,  2,   2,   2,     1),
    "Ch":        ("P4",             4,  3,   2,   2,   3,  2, None,  4,  4,   4,   4,     2),
    "EFz_":      ("K3,3",           6,  9,   3,   4,   2,  2,    4,  6,  4,   4,   3,     2),
}
for g6, (name, n_, m_, a_, ls_, d_, r_, gi_, b_, f_, t_, p_, res_) in REF.items():
    n, adj = E.decode_graph6(g6)
    check(name + " n", n, n_)
    check(name + " m", E.num_edges(n, adj), m_)
    check(name + " alpha", E.independence_number(n, adj), a_)
    check(name + " Ls", E.max_leaf_spanning_tree(n, adj), ls_)
    check(name + " diam", E.diameter(n, adj), d_)
    check(name + " rad", E.radius(n, adj), r_)
    check(name + " girth", E.girth(n, adj), gi_)
    check(name + " b", E.largest_induced_bipartite_size(n, adj), b_)
    check(name + " f", E.largest_induced_forest_size(n, adj), f_)
    check(name + " tree", E.largest_induced_tree_size(n, adj), t_)
    check(name + " path", E.largest_induced_path_size(n, adj), p_)
    check(name + " residue", E.residue(n, adj), res_)

# hand-computed local independence: every Petersen neighbourhood is 3 independent vertices
n, adj = E.decode_graph6("IheA@GUAo")
check("Petersen max l(v)", E.max_indep_neighbors(n, adj), 3)
check("Petersen l_avg", E.average_indep_neighbors(n, adj), Fraction(3))
check("Petersen has C4", E.has_cycle_of_length_4(n, adj), False)
check("Petersen triangles at 0", E.num_triangles_at_vertex(n, adj, 0), 0)
check("Petersen gamma_t", E.total_domination_number(n, adj), 4)
check("Petersen hamiltonian path", E.has_hamiltonian_path(n, adj), True)
check("Petersen path cover", E.path_cover_number(n, adj), 1)
# K4: every neighbourhood is a triangle, so l(v) = 1 and every vertex is in 3 triangles
n, adj = E.decode_graph6("C~")
check("K4 max l(v)", E.max_indep_neighbors(n, adj), 1)
check("K4 triangles at 0", E.num_triangles_at_vertex(n, adj, 0), 3)
check("K4 has C4", E.has_cycle_of_length_4(n, adj), True)
# exact ceiling helper: ceil((2L + sqrt(S))/4) with S a perfect square is elementary
check("ceil helper L=0 S=0", E.ceil_of_quarter_2L_plus_sqrtS(0, 0), 0)
check("ceil helper L=0 S=16", E.ceil_of_quarter_2L_plus_sqrtS(0, 16), 1)      # ceil(4/4)
check("ceil helper L=0 S=25", E.ceil_of_quarter_2L_plus_sqrtS(0, 25), 2)      # ceil(5/4)
check("ceil helper L=3 S=4", E.ceil_of_quarter_2L_plus_sqrtS(3, 4), 2)        # ceil(8/4)
check("ceil helper L=3 S=9", E.ceil_of_quarter_2L_plus_sqrtS(3, 9), 3)        # ceil(9/4)

# ------------------------------------------------------------------ geng-backed sweeps
def geng(n, extra=("-c",)):
    exe = None
    for cand in ("nauty-geng", "geng"):
        try:
            subprocess.run([cand, "--help"], capture_output=True)
            exe = cand
            break
        except FileNotFoundError:
            continue
    if exe is None:
        return None
    out = subprocess.run([exe, "-q"] + list(extra) + [str(n)], capture_output=True, text=True)
    return [l for l in out.stdout.split("\n") if l.strip()]


missing_geng = False
for n_ in range(3, 8):                                   # (2) Ls identity
    gs = geng(n_)
    if gs is None:
        missing_geng = True
        break
    for g6 in gs:
        n, adj = E.decode_graph6(g6)
        got = E.max_leaf_spanning_tree(n, adj)
        want = E.max_leaf_spanning_tree_bruteforce(n, adj)
        if got != want:
            fails.append("Ls identity broken on %s: n-gamma_c=%d, brute force=%d" % (g6, got, want))

if not missing_geng:
    # (3b) the induced-path invariant, recomputed from the LITERAL Lean definition
    # (a nodup vertex list whose adjacency holds exactly between consecutive indices),
    # over every connected graph on 2..6 vertices. Independent of the tree+degree<=2
    # characterisation used by the library.
    from itertools import permutations

    def lip_by_sequences(n, adj):
        best = 0
        for k in range(1, n + 1):
            ok_k = False
            for seq in permutations(range(n), k):
                good = True
                for i in range(k):
                    for j in range(i + 1, k):
                        if bool(adj[seq[i]] >> seq[j] & 1) != (j == i + 1):
                            good = False
                            break
                    if not good:
                        break
                if good:
                    ok_k = True
                    break
            if ok_k:
                best = k
        return best

    for n_ in range(2, 7):
        for g6 in geng(n_):
            n, adj = E.decode_graph6(g6)
            if E.largest_induced_path_size(n, adj) != lip_by_sequences(n, adj):
                fails.append("induced-path characterisation disagrees with the literal "
                             "definition on %s" % g6)

    for n_ in range(2, 7):                               # (3) minimality shortcut
        for g6 in geng(n_):
            n, adj = E.decode_graph6(g6)
            shortcut = sorted(E.minimal_total_dominating_sets(n, adj))
            literal = []
            tds = [S for S in range(1 << n) if E.is_total_dominating(n, adj, S)]
            tdset = set(tds)
            for S in tds:
                if not any((T != S and (T & ~S) == 0 and T in tdset) for T in range(1 << n)):
                    literal.append(S)
            if shortcut != sorted(literal):
                fails.append("minimal-TDS shortcut disagrees with the literal definition on %s" % g6)

    # (4) decoder vs nauty's own listg
    sample = (geng(6) or [])[:40]
    for g6 in sample:
        out = subprocess.run(["nauty-listg", "-q", "-a"], input=g6, capture_output=True, text=True)
        rows = [r for r in out.stdout.strip().split("\n") if set(r.strip()) <= {"0", "1"} and r.strip()]
        if not rows:
            continue
        n, adj = E.decode_graph6(g6)
        if len(rows) != n:
            fails.append("listg row count mismatch on %s" % g6)
            continue
        for i, row in enumerate(rows):
            for j, ch in enumerate(row.strip()):
                if (ch == "1") != bool(adj[i] >> j & 1):
                    fails.append("decoder disagrees with nauty-listg on %s at (%d,%d)" % (g6, i, j))
else:
    fails.append("nauty geng not available: the Ls identity and minimality sweeps could not run. "
                 "Refusing to declare the library validated.")

if fails:
    print("LIBRARY VALIDATION FAILED (%d):" % len(fails))
    for f in fails[:40]:
        print("  " + f)
    sys.exit(1)
print("LIBRARY VALIDATION PASSED: reference graphs; Ls identity vs brute-force spanning trees "
      "over all connected graphs n=3..7; induced-path characterisation vs the literal list "
      "definition over all connected graphs n=2..6; minimal-TDS shortcut vs the literal "
      "subset definition over all connected graphs n=2..6; graph6 decoder vs nauty-listg.")
