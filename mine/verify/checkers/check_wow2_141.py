#!/usr/bin/env python3
"""wow2-141 -- WOWII Conjecture 141  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture141.lean
Lean statement, verbatim from that file:
    theorem conjecture141 (G : SimpleGraph a) [DecidableRel G.Adj] (h : G.Connected) :
        (G.girth / 2 : Z) - 1 + ((Finset.univ.sup (indepNeighborsCard G) : N) : Z) <=
        (largestInducedTreeSize G : Z)
Natural language:
    For every finite simple connected graph G:
        floor(girth(G)/2) - 1 + max_v l(v)  <=  tree(G)
    where tree(G) is the largest order of an induced subgraph that is a tree.
A counterexample is: a connected graph WITH a cycle for which floor(girth/2) - 1 + maxL > tree.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)

g = E.girth(n, adj)
if g is None:
    print("REFUSE: this witness is acyclic, so G.girth is the top element of N-infinity and "
          "the value of its coercion into Z is convention-dependent. Refusing to guess.",
          file=sys.stderr)
    sys.exit(H.REFUSE)
maxL = E.max_indep_neighbors(n, adj)
tree = E.largest_induced_tree_size(n, adj)
lhs = g // 2 - 1 + maxL
computed = {"n": n, "girth": g, "maxL": maxL, "tree": tree, "lhs": lhs}
H.check_claims(w, computed)
H.verdict(lhs > tree, computed, "floor(girth/2) - 1 + maxL = %d" % lhs, "tree = %d" % tree)
