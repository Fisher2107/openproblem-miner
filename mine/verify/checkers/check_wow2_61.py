#!/usr/bin/env python3
"""wow2-61 -- WOWII Conjecture 61  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture61.lean
Lean statement, verbatim from that file:
    theorem conjecture61 (G : SimpleGraph a) [DecidableRel G.Adj] (h : G.Connected) :
        (residue G : R) + ceil ((G.diam : R) / 3) <= (G.largestInducedForestSize : R)
Natural language:
    For every finite simple connected graph G:
        residue(G) + ceil(diam(G)/3)  <=  f(G)
    where residue is the Havel-Hakimi residue of the degree sequence and f the largest
    induced forest order.
A counterexample is: a connected graph with residue + ceil(diam/3) > f.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)
res = E.residue(n, adj)
d = E.diameter(n, adj)
f = E.largest_induced_forest_size(n, adj)
lhs = res + -((-d) // 3)
computed = {"n": n, "residue": res, "diam": d, "f": f, "lhs": lhs}
H.check_claims(w, computed)
H.verdict(lhs > f, computed, "residue + ceil(diam/3) = %d" % lhs, "f = %d" % f)
