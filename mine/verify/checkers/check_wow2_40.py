#!/usr/bin/env python3
"""wow2-40 -- WOWII Conjecture 40  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture40.lean
Lean statement, verbatim from that file:
    theorem conjecture40 (h_conn : G.Connected) (h_nontrivial : 1 < Fintype.card a) :
        ceil (((pathCoverNumber G : R) + b G + 1) / 2) <= G.largestInducedForestSize
Natural language:
    For every finite simple connected graph G on at least two vertices:
        ceil( (p(G) + b(G) + 1)/2 )  <=  f(G)
    where p(G) is the path cover number (minimum number of vertex-disjoint paths of G
    covering V(G)), b(G) the largest induced bipartite subgraph order, and f(G) the
    largest induced forest order.
A counterexample is: a connected graph on >= 2 vertices with ceil((p + b + 1)/2) > f.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)
if n < 2:
    print("REFUSE: the statement assumes n > 1.", file=sys.stderr)
    sys.exit(H.REFUSE)
try:
    p = E.path_cover_number(n, adj)
except ValueError as e:
    print("REFUSE: %s" % e, file=sys.stderr)
    sys.exit(H.REFUSE)
b = E.largest_induced_bipartite_size(n, adj)
f = E.largest_induced_forest_size(n, adj)
lhs = -((-(p + b + 1)) // 2)                 # exact ceiling of an integer division
computed = {"n": n, "path_cover_number": p, "b": b, "f": f, "lhs_ceiling": lhs}
H.check_claims(w, computed)
H.verdict(lhs > f, computed, "ceil((p + b + 1)/2) = %d" % lhs, "f = %d" % f)
