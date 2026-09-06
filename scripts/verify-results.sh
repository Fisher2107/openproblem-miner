#!/usr/bin/env bash
# Independently re-verify every committed result from a clean checkout.
# This is what CI runs. A result that does not reproduce here is not a result.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0; n=0

if [ -f mine/verify/FREEZE.sha256 ]; then
  scripts/check-freeze.sh || { echo "::error::verifier drift"; exit 1; }
else
  echo "note: verifier not yet frozen (no results expected yet)"
fi

shopt -s nullglob
for d in mine/results/*/; do
  [ -f "$d/checker.txt" ] || continue
  n=$((n+1)); id=$(basename "$d")
  tier=$(cat "$d/TIER" 2>/dev/null | tr -d '[:space:]' || echo "?")
  cmd=$(grep -v '^#' "$d/checker.txt" | grep -v '^[[:space:]]*$' | head -1)
  echo "=== $id (tier $tier)"
  echo "    \$ $cmd"
  if bash -c "$cmd"; then
    echo "    ACCEPTED"
  else
    echo "::error::$id — frozen verifier REJECTED the committed witness"; fail=1
  fi
  case "$tier" in
    T3) [ -d "$d/lean" ] || { echo "::error::$id claims T3 with no lean/ directory"; fail=1; }
        [ -f "$d/backtranslation.md" ] || { echo "::error::$id claims T3 without a statement back-translation"; fail=1; } ;;
  esac
  [ -f "$d/prior-art.md" ] || { echo "::error::$id has no prior-art check"; fail=1; }
done

echo "---"; echo "$n result(s) checked"
[ "$fail" = 0 ] && echo "ALL REPRODUCED" || echo "REPRODUCTION FAILURES PRESENT"
exit $fail
