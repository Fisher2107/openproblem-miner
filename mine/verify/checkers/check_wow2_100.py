#!/usr/bin/env python3
"""wow2-100 -- WOWII Conjecture 100  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture100.lean
Lean statement, verbatim from that file:
    theorem conjecture100 (G : SimpleGraph a) [DecidableRel G.Adj] (h : G.Connected) :
        let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
        (G.indepNum : R) <= ceil (((maxL : R) + (1 / 2) * (degreeL2Norm Gc : R)) / 2)
Natural language:
    For every finite simple connected graph G:
        alpha(G) <= ceil( ( max_v l(v) + (1/2)*||deg(complement of G)||_2 ) / 2 )
    where ||deg(H)||_2 = sqrt(sum_v deg_H(v)^2).
A counterexample is: a connected graph with alpha strictly greater than that ceiling.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)

maxL = E.max_indep_neighbors(n, adj)
full = (1 << n) - 1
comp = [full & ~adj[v] & ~(1 << v) for v in range(n)]
S = E.degree_l2_norm_squared(n, comp)     # exact integer: sum of squared complement degrees
rhs = E.ceil_of_quarter_2L_plus_sqrtS(maxL, S)   # exact ceil((maxL + sqrt(S)/2)/2), no floats
alpha = E.independence_number(n, adj)
computed = {"n": n, "maxL": maxL, "sum_sq_complement_degrees": S, "rhs_ceiling": rhs, "alpha": alpha}
H.check_claims(w, computed)
H.verdict(alpha > rhs, computed, "alpha = %d" % alpha, "ceil((maxL + sqrt(S)/2)/2) = %d" % rhs)
