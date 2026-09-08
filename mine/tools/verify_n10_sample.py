#!/usr/bin/env python3
"""Re-check the n<=10 negative with the FROZEN checkers on a random sample.

The exhaustive sweep is the fast C screener's word. This takes a uniform random sample of
connected graphs at n=9 and n=10 and runs all ten frozen WOWII checkers on each. Every one
must REJECT (exit 1) or REFUSE (exit 2, e.g. conjecture 141 on an acyclic graph); a single
ACCEPT would mean the screener under-reported and the headline negative is wrong.
"""
import subprocess, random, json, sys

CHECKERS = ["check_wow2_19.py", "check_wow2_40.py", "check_wow2_61.py", "check_wow2_100.py",
            "check_wow2_133.py", "check_wow2_141.py", "check_wow2_160.py",
            "check_wow2_198a.py", "check_wow2_291.py", "check_wow2_314.py"]

print(subprocess.run(["bash", "scripts/check-freeze.sh"], capture_output=True, text=True).stdout.strip())
random.seed(1010)
accepts, runs, refuses = [], 0, 0
for n, k in ((9, 60), (10, 240)):
    pool = subprocess.run(["nauty-geng", "-qc", str(n)], capture_output=True, text=True).stdout.split()
    for g6 in random.sample(pool, k):
        json.dump({"graph6": g6}, open("/tmp/wn10.json", "w"))
        for c in CHECKERS:
            rc = subprocess.run(["python3", "mine/verify/checkers/" + c, "/tmp/wn10.json"],
                                capture_output=True).returncode
            runs += 1
            if rc == 0:
                accepts.append((c, g6))
            elif rc == 2:
                refuses += 1
    print("n=%d: sampled %d graphs, %d checker runs so far, %d ACCEPTs" % (n, k, runs, len(accepts)), flush=True)
print("TOTAL frozen-checker runs: %d, REFUSEs: %d, ACCEPTs: %d" % (runs, refuses, len(accepts)))
if accepts:
    print("SCREENER UNDER-REPORTED:", accepts[:5]); sys.exit(1)
print("CONFIRMED: the frozen checkers agree with the screener on every sampled graph.")
