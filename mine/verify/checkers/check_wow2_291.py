#!/usr/bin/env python3
"""wow2-291 -- WOWII Conjecture 291  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture291.lean
Lean statement, verbatim from that file:
    theorem conjecture291 (G : SimpleGraph a) [DecidableRel G.Adj] (h : G.Connected)
        (hn : 2 < Fintype.card a) :
        G.totalDominationNumber <= havelHakimiZeroStep G + freqMinTriangles G
Natural language:
    For every finite simple connected graph G with n > 2:
        gamma_t(G) <= k(G) + freq_min_T(G)
    where gamma_t is the total domination number, k(G) is the first index i >= 0 at which
    the i-th Havel-Hakimi iterate of the descending degree sequence contains a zero (or is
    empty), and freq_min_T(G) = #{v : T(v) = min_u T(u)}.
A counterexample is: a connected graph on n > 2 vertices with gamma_t > k + freq_min_T.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)
if n <= 2:
    print("REFUSE: the statement assumes n > 2.", file=sys.stderr)
    sys.exit(H.REFUSE)
gt = E.total_domination_number(n, adj)
if gt is None:
    print("REJECT: no total dominating set exists (isolated vertex); gamma_t undefined.",
          file=sys.stderr)
    sys.exit(H.REJECT)
k = E.havel_hakimi_zero_index(n, adj)
tri = [E.num_triangles_at_vertex(n, adj, v) for v in range(n)]
freq = sum(1 for t in tri if t == min(tri))
rhs = k + freq
computed = {"n": n, "gamma_t": gt, "havel_hakimi_zero_index": k,
            "min_triangles": min(tri), "freq_min_triangles": freq, "rhs": rhs}
H.check_claims(w, computed)
H.verdict(gt > rhs, computed, "gamma_t = %d" % gt, "k + freq_min_T = %d" % rhs)
