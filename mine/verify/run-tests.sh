#!/usr/bin/env bash
# Freeze-time (and CI-time) validation of the whole verifier.
#
# Every checker is exercised on BOTH a known-true and a known-false input, plus the
# degenerate inputs (malformed, disconnected, oversized) where the required answer is
# REFUSE or REJECT. An unvalidated checker is worse than no checker, because it
# manufactures confidence.
#
# exit 0 = every checker behaved exactly as required.
set -uo pipefail
cd "$(dirname "$0")/.."          # -> mine/
V=verify
fail=0; pass=0

expect () {  # expect <code> <label> <cmd...>
  local want="$1" label="$2"; shift 2
  "$@" >/dev/null 2>&1; local got=$?
  if [ "$got" = "$want" ]; then pass=$((pass+1));
  else echo "  FAIL $label: expected exit $want, got $got"; fail=$((fail+1)); fi
}

echo "== library validation (reference graphs, Ls identity, induced paths, minimal TDS, decoder)"
if python3 "$V/tests/validate_library.py"; then pass=$((pass+1)); else echo "  FAIL library"; fail=$((fail+1)); fi

echo "== ACCEPT path: published counterexamples must be accepted"
expect 0 "wow2-194 on its published 18-vertex counterexample" \
  python3 "$V/checkers/check_wow2_194.py" "$V/tests/known_true_wow2_194.json"
expect 0 "wow2-200 on its published 11-vertex counterexample" \
  python3 "$V/checkers/check_wow2_200.py" "$V/tests/known_true_wow2_200.json"
expect 0 "ramsey R(3,3)>5 via C5"   python3 "$V/checkers/check_ramsey_lower.py" "$V/tests/known_true_ramsey_R33.json"
expect 0 "ramsey R(4,4)>17 via Paley17" python3 "$V/checkers/check_ramsey_lower.py" "$V/tests/known_true_ramsey_R44.json"
expect 0 "vdW W(3,2)>8"             python3 "$V/checkers/check_vdw_lower.py" "$V/tests/known_true_vdw_W32.json"
expect 0 "Schur S(3)>=13"           python3 "$V/checkers/check_schur_lower.py" "$V/tests/known_true_schur_S3.json"

echo "== REJECT path: non-counterexamples must be rejected"
for c in "$V"/checkers/check_wow2_*.py; do
  expect 1 "$(basename "$c") on the Petersen graph" python3 "$c" "$V/tests/known_false_petersen.json"
  expect 1 "$(basename "$c") on C5"                 python3 "$c" "$V/tests/known_false_c5.json"
done
expect 1 "ramsey on K6 (contains a triangle)" python3 "$V/checkers/check_ramsey_lower.py" "$V/tests/known_false_ramsey.json"
expect 1 "vdW on [1,9] (W(3,2)=9)"            python3 "$V/checkers/check_vdw_lower.py" "$V/tests/known_false_vdw.json"
expect 1 "Schur on [1,14] (S(3)=13)"          python3 "$V/checkers/check_schur_lower.py" "$V/tests/known_false_schur.json"

echo "== a wrong claimed value must be rejected even when the graph is well formed"
expect 1 "wow2-160 with claimed Ls=999" python3 "$V/checkers/check_wow2_160.py" "$V/tests/bad_claim_petersen.json"

echo "== degenerate inputs must REFUSE (2) or REJECT (1), never ACCEPT (0)"
for c in "$V"/checkers/check_wow2_*.py; do
  expect 2 "$(basename "$c") on a malformed witness"   python3 "$c" "$V/tests/malformed.json"
  expect 2 "$(basename "$c") on an oversized witness"  python3 "$c" "$V/tests/too_big.json"
  expect 1 "$(basename "$c") on a disconnected graph"  python3 "$c" "$V/tests/disconnected.json"
done

echo "---"
echo "$pass check(s) passed, $fail failed"
[ "$fail" = 0 ] && echo "VERIFIER TESTS PASSED" || echo "VERIFIER TESTS FAILED"
exit $fail
