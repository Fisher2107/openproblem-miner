#!/usr/bin/env bash
# Hash-lock the verifier. Run ONCE, after mine/verify/ is built and its checkers are
# tested against known-true AND known-false inputs. Never run again to "re-bless" drift.
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/_sha.sh
V=mine/verify
[ -d "$V" ] || { echo "no $V"; exit 1; }
if [ -f "$V/FREEZE.sha256" ]; then
  echo "REFUSING: $V/FREEZE.sha256 already exists."
  echo "The verifier is frozen. Re-freezing to accommodate a failing result is the"
  echo "failure mode this repo exists to prevent. Delete it deliberately if the freeze"
  echo "was genuinely premature, and say so in the report."
  exit 1
fi
verify_source_files "$V" > "$V/FREEZE.sha256"
echo "frozen: $(wc -l < "$V/FREEZE.sha256") source files -> $V/FREEZE.sha256"
