#!/usr/bin/env python3
"""Run the FROZEN checker over EVERY girth>=6 graph up to n=14.

A violation of WOWII conjecture 141 forces girth >= 6 (tree(G) >= max_v l(v) + 1, so
floor(girth/2) - 1 + maxL > tree(G) requires floor(girth/2) > 2). The girth >= 6 class is
small, so instead of trusting the fast screener plus a sample, the frozen checker itself is
run on every member. That makes the negative a statement about the verifier, not about the
search tooling.
"""
import subprocess, json, sys, os
sys.path.insert(0, "mine/verify/lib")
import exactgraph as E

lo, hi = int(sys.argv[1]), int(sys.argv[2])
grand, accepts = 0, []
print(subprocess.run(["bash", "scripts/check-freeze.sh"], capture_output=True, text=True).stdout.strip())
for n in range(lo, hi + 1):
    out = subprocess.run(["nauty-geng", "-qc", "-tf", str(n)], capture_output=True, text=True).stdout.split()
    g6s = []
    for s in out:
        nn, adj = E.decode_graph6(s)
        g = E.girth(nn, adj)
        if g is not None and g >= 6:
            g6s.append(s)
    for s in g6s:
        json.dump({"conjecture": "wow2-141", "graph6": s}, open("/tmp/w141f.json", "w"))
        rc = subprocess.run(["python3", "mine/verify/checkers/check_wow2_141.py", "/tmp/w141f.json"],
                            capture_output=True).returncode
        if rc == 0:
            accepts.append(s)
    grand += len(g6s)
    print("n=%-3d girth>=6 graphs checked by the FROZEN checker: %-7d ACCEPTs so far: %d"
          % (n, len(g6s), len(accepts)), flush=True)
print("TOTAL %d graphs, %d ACCEPTs" % (grand, len(accepts)))
if accepts:
    print("SCREENER UNDER-REPORTED:", accepts[:5]); sys.exit(1)
print("CONFIRMED BY THE FROZEN VERIFIER: conjecture 141 has no counterexample of girth >= 6 "
      "on at most %d vertices, and a counterexample must have girth >= 6." % hi)
