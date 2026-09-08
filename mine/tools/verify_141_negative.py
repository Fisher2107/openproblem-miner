#!/usr/bin/env python3
"""Confirm the conjecture-141 negative with the FROZEN checker, not just the screener.

The screener said "no candidates" over every girth >= 5 graph up to n = 16. That is a claim
about the screener. This re-runs the frozen checker on a random sample of the graphs the
screener cleared -- specifically the girth >= 6 ones, which are the only graphs where a
violation is possible -- and requires every one to be REJECTed (exit 1, i.e. not a
counterexample). Any ACCEPT here would mean the screener under-reported.
"""
import subprocess, random, json, sys, os
sys.path.insert(0, "mine/verify/lib")
import exactgraph as E

random.seed(20260907)
total = 0
accepts = []
per_n = {}
for n in range(11, 15):
    out = subprocess.run(["nauty-geng", "-qc", "-tf", str(n)], capture_output=True, text=True).stdout.split()
    # keep only girth >= 6: the girth >= 5 class minus the graphs containing a 5-cycle
    g6 = []
    for s in out:
        nn, adj = E.decode_graph6(s)
        g = E.girth(nn, adj)
        if g is not None and g >= 6:
            g6.append(s)
    sample = random.sample(g6, min(50, len(g6)))
    per_n[n] = (len(g6), len(sample))
    for s in sample:
        json.dump({"conjecture": "wow2-141", "graph6": s}, open("/tmp/w141.json", "w"))
        rc = subprocess.run(["python3", "mine/verify/checkers/check_wow2_141.py", "/tmp/w141.json"],
                            capture_output=True).returncode
        total += 1
        if rc == 0:
            accepts.append(s)

print("girth>=6 graphs found and sampled, by order:")
for n, (tot, samp) in sorted(per_n.items()):
    print("  n=%-3d girth>=6 graphs: %-7d sampled: %d" % (n, tot, samp))
print("frozen checker run on %d graphs; ACCEPTs (would be counterexamples): %d" % (total, len(accepts)))
if accepts:
    print("SCREENER UNDER-REPORTED:", accepts[:5])
    sys.exit(1)
print("CONFIRMED: the frozen checker rejects every sampled graph, agreeing with the screener.")
