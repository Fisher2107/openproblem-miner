#!/usr/bin/env bash
# Does the fast C screener ever MISS what the frozen checker would accept?
# Ground truth = the frozen checker run on every connected graph in the range.
# The screener is allowed to over-report; it must never under-report.
set -uo pipefail
cd "$(dirname "$0")/../.."
LO=${1:-3}; HI=${2:-7}
tmp=$(mktemp -d)
for n in $(seq "$LO" "$HI"); do nauty-geng -qc "$n"; done > "$tmp/all.g6"
echo "graphs: $(wc -l < "$tmp/all.g6")"
./mine/tools/wowscan < "$tmp/all.g6" > "$tmp/screener.txt" 2>"$tmp/screener.err"
cat "$tmp/screener.err"
python3 - "$tmp" <<'PY'
import json, subprocess, sys, os
tmp = sys.argv[1]
CH = {"wow2-19":"check_wow2_19.py","wow2-40":"check_wow2_40.py","wow2-61":"check_wow2_61.py",
      "wow2-100":"check_wow2_100.py","wow2-133":"check_wow2_133.py","wow2-141":"check_wow2_141.py",
      "wow2-160":"check_wow2_160.py","wow2-198a":"check_wow2_198a.py","wow2-291":"check_wow2_291.py",
      "wow2-314":"check_wow2_314.py"}
graphs = [l.strip() for l in open(os.path.join(tmp,"all.g6")) if l.strip()]
screened = set()
for l in open(os.path.join(tmp,"screener.txt")):
    cid, g6 = l.split()
    screened.add((cid.replace("?p",""), g6))
truth, refused = set(), 0
wf = os.path.join(tmp,"w.json")
for g6 in graphs:
    json.dump({"graph6": g6}, open(wf,"w"))
    for cid, script in CH.items():
        rc = subprocess.run(["python3","mine/verify/checkers/"+script,wf],
                            capture_output=True).returncode
        if rc == 0: truth.add((cid,g6))
        elif rc == 2: refused += 1
missed = truth - screened
print("frozen checker ACCEPTED %d (graph,conjecture) pairs; screener emitted %d; REFUSE count %d"
      % (len(truth), len(screened), refused))
if missed:
    print("SCREENER UNDER-REPORTED %d pair(s) -- the gates are unsound:" % len(missed))
    for m in sorted(missed)[:20]: print("   ", m)
    sys.exit(1)
print("SCREENER SOUND on this range: it missed nothing the frozen checker accepts.")
PY
