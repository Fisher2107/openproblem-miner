#!/usr/bin/env python3
"""wow2-133 -- WOWII Conjecture 133  [research open]

Source (informal):  http://cms.dt.uh.edu/faculty/delavinae/research/wowII/
Source (formal):    google-deepmind/formal-conjectures@8323e878
                    FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean
Lean statement, verbatim from that file:
    theorem conjecture133 (G : SimpleGraph a) [DecidableRel G.Adj] (h : G.Connected) :
        let rad := G.radius.toNat
        let hasC4 := exists a b c d, (all distinct) and G.Adj a b and G.Adj b c and G.Adj c d and G.Adj d a
        let cC4 : N := if hasC4 then 0 else 1
        (rad : R) + (floor (l G) : R) ^ cC4 <= (path G : R)
Natural language:
    For every finite simple connected graph G:
        rad(G) + floor(l_avg(G))^{cC4(G)}  <=  path(G)
    where l_avg is the average over v of l(v) = alpha(G[N(v)]), path(G) is the number of
    vertices of a largest INDUCED path, and cC4(G) = 1 if G has no 4-cycle else 0.
    NOTE ON A NAMING COLLISION. The docstring of GraphConjecture314.lean claims that
    SimpleGraph.path is "the floor of the average distance". At commit 8323e878 that
    comment is stale: the repository contains exactly one definition of SimpleGraph.path
    (FormalConjecturesForMathlib/Combinatorics/SimpleGraph/VertexDistance.lean:50) and it
    is the largest-induced-path size. This checker uses that definition, for two reasons
    settled BEFORE any search was run:
      (a) it is the only definition actually present in the repository, and
      (b) under the floor-of-average-distance reading the right-hand side is tiny for
          essentially every graph (the Petersen graph would already be a counterexample),
          so that reading cannot be the statement DeLaVina registered.
    The alternative value is still computed and printed, so that a human signing off on
    an accepted witness can see both. Any witness this checker accepts must carry a human
    sign-off on the STATEMENT, not merely on the arithmetic.
A counterexample is: a connected graph with rad + floor(l_avg)^cC4 > path, under BOTH readings of path.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
H.require_connected(n, adj)

from fractions import Fraction
rad = E.radius(n, adj)
lavg = E.average_indep_neighbors(n, adj)
floor_lavg = lavg.numerator // lavg.denominator
cC4 = 0 if E.has_cycle_of_length_4(n, adj) else 1
term = 1 if cC4 == 0 else floor_lavg          # x^0 = 1, x^1 = x
lhs = rad + term
path_induced = E.largest_induced_path_size(n, adj)

# alternative (contested) reading: floor of the average distance over ordered pairs
dsum = 0
for u in range(n):
    seen, frontier, d = 1 << u, 1 << u, 0
    while frontier:
        nxt = 0
        for v in E.bits(frontier):
            nxt |= adj[v] & ~seen
        if not nxt:
            break
        seen |= nxt; frontier = nxt; d += 1
        for v in E.bits(nxt):
            dsum += d
avg_dist = Fraction(dsum, n * (n - 1)) if n > 1 else Fraction(0)
path_alt = avg_dist.numerator // avg_dist.denominator

computed = {"n": n, "rad": rad, "l_avg": lavg, "floor_l_avg": floor_lavg, "cC4": cC4,
            "lhs": lhs, "path_largest_induced": path_induced,
            "path_alt_floor_avg_distance": path_alt}
H.check_claims(w, computed)
v_main, v_alt = lhs > path_induced, lhs > path_alt
if v_main and not v_alt:
    print("NOTE: this witness violates the conjecture under the repository's induced-path "
          "definition but NOT under the stale floor-of-average-distance reading; flag the "
          "statement for human sign-off.")
H.verdict(v_main, computed, "rad + floor(l_avg)^cC4 = %d" % lhs, "path = %d" % path_induced)
