#!/usr/bin/env python3
"""wow2-160 -- WOWII Conjecture 160  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/160.lean
Lean statement, verbatim from that file:
    theorem conjecture160 (G : SimpleGraph a) [DecidableRel G.Adj] (h : G.Connected) :
        let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
        let maxT := maxTrianglesAtVertex G
        let cC4 : N := if exists v, exists c : G.Walk v v, c.IsCycle and c.length = 4 then 0 else 1
        (maxL : R) + (maxT : R) * (cC4 : R) <= Ls G
Natural language:
    For every finite simple connected graph G:
        max_v l(v) + (max_v T(v)) * cC4(G)  <=  Ls(G)
    where l(v) = alpha(G[N(v)]), T(v) = number of triangles containing v,
    cC4(G) = 1 if G has no cycle of length 4 (not necessarily induced) else 0,
    and Ls(G) = max number of leaves over all spanning trees.
A counterexample is: a connected graph with maxL + maxT*cC4 > Ls.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)

maxL = E.max_indep_neighbors(n, adj)
maxT = max(E.num_triangles_at_vertex(n, adj, v) for v in range(n))
cC4 = 0 if E.has_cycle_of_length_4(n, adj) else 1
Ls = E.max_leaf_spanning_tree(n, adj)
lhs = maxL + maxT * cC4
computed = {"n": n, "maxL": maxL, "maxT": maxT, "cC4": cC4, "Ls": Ls, "lhs": lhs}
H.check_claims(w, computed)
H.verdict(lhs > Ls, computed, "maxL + maxT*cC4 = %d" % lhs, "Ls = %d" % Ls)
