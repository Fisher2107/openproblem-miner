#!/usr/bin/env python3
"""wow2-194 -- WOWII Conjecture 194  [research SOLVED: already refuted]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture194.lean
Lean statement, verbatim from that file:
    theorem conjecture194 : answer(False) <->
        forall (G : SimpleGraph a) (_h : G.Connected),
          (G.indepNum : R) <= 1 + averageIndepNeighbors G ->
          exists u v, exists p : G.Walk u v, p.IsHamiltonian
Natural language:
    It was conjectured that for every finite simple connected graph G,
        if alpha(G) <= 1 + l_avg(G) then G has a Hamiltonian path.
    THIS CONJECTURE IS ALREADY REFUTED in the literature; the checker exists so that the
    freeze-time test suite can exercise the ACCEPT path of the verifier end to end against
    a published counterexample, rather than only its REJECT path. Nothing this checker
    accepts is a new result.
A counterexample is: a connected graph with alpha <= 1 + l_avg and no Hamiltonian path.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)
alpha = E.independence_number(n, adj)
lavg = E.average_indep_neighbors(n, adj)
hyp = (alpha <= 1 + lavg)
ham = E.has_hamiltonian_path(n, adj)
computed = {"n": n, "alpha": alpha, "l_avg": lavg, "hypothesis_holds": hyp,
            "has_hamiltonian_path": ham}
H.check_claims(w, computed)
H.verdict(hyp and not ham, computed,
          "hypothesis alpha <= 1 + l_avg: %s" % hyp,
          "conclusion (Hamiltonian path): %s" % ham)
