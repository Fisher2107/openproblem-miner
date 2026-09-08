#!/usr/bin/env python3
"""wow2-198a -- WOWII Conjecture 198a  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture198a.lean
Lean statement, verbatim from that file:
    theorem conjecture198a (G : SimpleGraph a) (h : G.Connected)
        (hb : b G <= 2 + averageEccentricity G) :
        exists u v, exists p : G.Walk u v, p.IsHamiltonian
Natural language:
    For every finite simple connected graph G on at least two vertices:
        if b(G) <= 2 + avg_ecc(G) then G has a Hamiltonian path.
A counterexample is: a connected graph satisfying b <= 2 + avg_ecc that has NO Hamiltonian path.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)

b = E.largest_induced_bipartite_size(n, adj)
avg_ecc = E.average_eccentricity(n, adj)
hyp = (b <= 2 + avg_ecc)
ham = E.has_hamiltonian_path(n, adj)
computed = {"n": n, "b": b, "avg_ecc": avg_ecc, "hypothesis_holds": hyp,
            "has_hamiltonian_path": ham}
H.check_claims(w, computed)
H.verdict(hyp and not ham, computed,
          "hypothesis b <= 2 + avg_ecc: %s" % hyp,
          "conclusion (Hamiltonian path): %s" % ham)
