#!/usr/bin/env python3
"""Class C -- Ramsey number lower bound.

A witness is a graph on n vertices with no clique on s vertices and no independent set
on t vertices; such a graph certifies R(s,t) > n. This is the standard Ramsey lower-bound
certificate and is checkable in time O(C(n,s) + C(n,t)) by direct enumeration, which is
what this checker does -- no cleverness, because a clever clique routine that is subtly
wrong would silently manufacture a record.

Witness format:
  {"family": "ramsey", "s": 4, "t": 4, "n": 17, "graph6": "...",
   "published_lower_bound": 17}      # optional: the record this claims to match or beat

ACCEPT (0) means only "this graph has the stated clique/independence properties", i.e.
R(s,t) > n holds. Whether that BEATS the published record is a separate judgement the
checker prints but does not decide.
"""
import sys, os, json
from itertools import combinations
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import harness as H
import exactgraph as E

w, n, adj = H.load(sys.argv)
try:
    s, t = int(w["s"]), int(w["t"])
except Exception:
    print("REFUSE: witness must give integer 's' and 't'", file=sys.stderr)
    sys.exit(H.REFUSE)
if "n" in w and int(w["n"]) != n:
    print("REJECT: witness 'n'=%s disagrees with the graph's order %d" % (w["n"], n), file=sys.stderr)
    sys.exit(H.REJECT)

clique = None
for c in combinations(range(n), s):
    if all(adj[u] >> v & 1 for u, v in combinations(c, 2)):
        clique = c
        break
indep = None
for c in combinations(range(n), t):
    if all(not (adj[u] >> v & 1) for u, v in combinations(c, 2)):
        indep = c
        break

computed = {"n": n, "s": s, "t": t, "edges": E.num_edges(n, adj),
            "found_K%d" % s: list(clique) if clique else None,
            "found_independent_%d" % t: list(indep) if indep else None}
H.check_claims(w, computed)
ok = clique is None and indep is None
pub = w.get("published_lower_bound")
if ok and pub is not None:
    print("NOTE: this certifies R(%d,%d) > %d. The published lower bound supplied with the "
          "witness is %s, so this witness %s the record." %
          (s, t, n, pub, "BEATS" if n + 1 > int(pub) else "does not beat"))
H.verdict(ok, computed,
          "clique of order %d: %s" % (s, "none" if clique is None else str(clique)),
          "independent set of order %d: %s" % (t, "none" if indep is None else str(indep)))
