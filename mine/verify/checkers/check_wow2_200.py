#!/usr/bin/env python3
"""wow2-200 -- WOWII Conjecture 200  [research SOLVED: already refuted]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture200.lean
Lean statement, verbatim from that file:
    theorem conjecture200 : answer(False) <->
        forall (G : SimpleGraph a) (_h : G.Connected),
          (largestInducedTreeSize G : R) = ceil (1 + averageIndepNeighbors G) ->
          exists u v, exists p : G.Walk u v, p.IsHamiltonian
Natural language:
    It was conjectured that for every finite simple connected graph G,
        if tree(G) = ceil(1 + l_avg(G)) then G has a Hamiltonian path.
    ALREADY REFUTED; this checker exists only as end-to-end ACCEPT-path test material for
    the freeze suite, using the published 11-vertex counterexample J??FFBRq}N_.
A counterexample is: a connected graph with tree(G) = ceil(1 + l_avg) and no Hamiltonian path.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)
tree = E.largest_induced_tree_size(n, adj)
lavg = E.average_indep_neighbors(n, adj)
one_plus = 1 + lavg
rhs = -((-one_plus.numerator) // one_plus.denominator)      # exact ceiling of a Fraction
hyp = (tree == rhs)
ham = E.has_hamiltonian_path(n, adj)
computed = {"n": n, "tree": tree, "l_avg": lavg, "ceil_1_plus_l_avg": rhs,
            "hypothesis_holds": hyp, "has_hamiltonian_path": ham}
H.check_claims(w, computed)
H.verdict(hyp and not ham, computed,
          "hypothesis tree = ceil(1 + l_avg): %s" % hyp,
          "conclusion (Hamiltonian path): %s" % ham)
