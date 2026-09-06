#!/usr/bin/env python3
"""wow2-314 -- WOWII Conjecture 314  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture314.lean
Lean statement, verbatim from that file:
    theorem conjecture314 [Nontrivial a] (G : SimpleGraph a) [DecidableRel G.Adj]
        (hG : G.Connected)
        (hTriFree : forall x y z, G.Adj x y -> G.Adj y z -> G.Adj z x -> False)
        (hPath : largestInducedPathSize G <= 4) :
        IsWellTotallyDominated G
Natural language:
    For every finite simple connected graph G on at least two vertices:
        if G is triangle-free and its largest induced path has at most 4 vertices,
        then every minimal total dominating set of G has the same cardinality.
A counterexample is: a connected triangle-free graph on >= 2 vertices with largest induced path <= 4 that has two minimal total dominating sets of different sizes.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)
if n < 2:
    print("REFUSE: the statement assumes Nontrivial (n >= 2).", file=sys.stderr)
    sys.exit(H.REFUSE)
tri_free = all(E.num_triangles_at_vertex(n, adj, v) == 0 for v in range(n))
lip = E.largest_induced_path_size(n, adj)
hyp = tri_free and lip <= 4
mtds = E.minimal_total_dominating_sets(n, adj)
sizes = sorted({E.popcount(S) for S in mtds})
wtd = len(sizes) <= 1
computed = {"n": n, "triangle_free": tri_free, "largest_induced_path": lip,
            "hypothesis_holds": hyp, "minimal_tds_sizes": sizes,
            "is_well_totally_dominated": wtd}
H.check_claims(w, computed)
H.verdict(hyp and not wtd, computed,
          "hypotheses (triangle-free, induced path <= 4): %s" % hyp,
          "conclusion (well totally dominated): %s" % wtd)
