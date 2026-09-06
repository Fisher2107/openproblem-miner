#!/usr/bin/env python3
"""wow2-19 -- WOWII Conjecture 19  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture19.lean
Lean statement, verbatim from that file:
    theorem conjecture19 (G : SimpleGraph a) [Nontrivial a] (h_conn : G.Connected) :
        floor ((sum over v of (G.eccent v).toNat) / (Fintype.card a) + sSup (range (indepNeighbors G)))
          <= b G
Natural language:
    For every finite simple connected graph G on at least two vertices:
        floor( (sum_v ecc(v))/n + max_v l(v) )  <=  b(G)
    where b(G) is the largest order of an induced bipartite subgraph.
    The floor is applied to the SUM of the average eccentricity and the maximum of l(v),
    not to each summand separately.
A counterexample is: a connected graph on >= 2 vertices with floor(avg_ecc + maxL) > b.
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
avg_ecc = E.average_eccentricity(n, adj)
maxL = E.max_indep_neighbors(n, adj)
total = avg_ecc + maxL
lhs = total.numerator // total.denominator          # exact floor of a Fraction
b = E.largest_induced_bipartite_size(n, adj)
computed = {"n": n, "avg_ecc": avg_ecc, "maxL": maxL, "floor_sum": lhs, "b": b}
H.check_claims(w, computed)
H.verdict(lhs > b, computed, "floor(avg_ecc + maxL) = %d" % lhs, "b = %d" % b)
