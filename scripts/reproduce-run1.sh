#!/usr/bin/env bash
# Re-run the checkable claims of run 1 from a clean checkout.
#
# This is the audit path. It does NOT re-run the multi-hour exhaustive sweeps; it re-runs
# every claim whose truth does not depend on how long you are willing to wait, plus a
# short sweep that exercises the same code path as the long ones.
#
# Requires: python3, nauty (geng/listg/amtog), gcc. Lean only for the T3 step.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
step () { echo; echo "=== $* ==="; }

step "1. the verifier has not drifted"
bash scripts/check-freeze.sh || fail=1

step "2. the frozen verifier's own tests (71 checks, both directions)"
bash mine/verify/run-tests.sh || fail=1

step "3. the search-side screener agrees with the frozen library, invariant by invariant"
gcc -O3 -o mine/tools/wowscan mine/tools/wowscan.c || fail=1
gcc -O3 -o mine/tools/graphtool mine/tools/graphtool.c || fail=1
./mine/tools/graphtool --selftest || fail=1
python3 mine/tools/crosscheck_invariants.py 9 150 || fail=1

step "4. short exhaustive sweep (n<=8, all ten open WOWII conjectures) — expect 0 candidates"
for n in 3 4 5 6 7 8; do nauty-geng -qc $n | ./mine/tools/wowscan; done || fail=1

step "5. conjecture 141 over every girth>=5 graph at n=11,12 — expect 0 candidates"
for n in 11 12; do nauty-geng -qc -tf $n | ./mine/tools/wowscan --only 141; done || fail=1

step "6. the positive control: the generator rediscovers a counterexample to the REFUTED conjecture 200"
python3 mine/tools/genfamilies.py 12 2>/dev/null | grep '^[A-Za-z~]' > /tmp/fam12.g6
found=$(while read -r g; do ./mine/tools/wowclimb --eval 200 "$g"; done < /tmp/fam12.g6 | grep -c "objective 1")
echo "family members violating the refuted conjecture 200: $found (must be > 0)"
[ "$found" -gt 0 ] || { echo "POSITIVE CONTROL FAILED — a negative from this searcher would be meaningless"; fail=1; }

step "7. the frozen checker accepts the published counterexamples (T1 accept path)"
python3 mine/verify/checkers/check_wow2_200.py mine/verify/tests/known_true_wow2_200.json >/dev/null || fail=1
python3 mine/verify/checkers/check_wow2_194.py mine/verify/tests/known_true_wow2_194.json >/dev/null || fail=1
echo "both accepted"

step "8. the blind T2 reimplementation still agrees"
( cd mine/attacks/t2-independent && python3 checker.py | tail -5 ) || fail=1

step "9. T3: the Lean formalization compiles with clean axioms (skipped if lean is absent)"
if command -v lean >/dev/null 2>&1 || [ -x "$HOME/.elan/bin/lean" ]; then
  export PATH="$HOME/.elan/bin:$PATH"
  ( cd mine/attacks/t3-positive-control && lean Conj200Control.lean ) || fail=1
  echo "(expect: no sorryAx and no ofReduceBool in the axiom lists above)"
else
  echo "lean not installed; skipping T3"
fi

step "10. no result is committed that the frozen verifier does not accept"
bash scripts/verify-results.sh || fail=1

echo
[ "$fail" = 0 ] && echo "RUN 1 CLAIMS REPRODUCED" || echo "REPRODUCTION FAILURES PRESENT"
exit $fail
