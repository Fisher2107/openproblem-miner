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
find "$V" -type f ! -name FREEZE.sha256 -print0 \
  | LC_ALL=C sort -z \
  | while IFS= read -r -d '' f; do printf '%s  %s\n' "$(sha256_stdin < "$f")" "$f"; done \
  > "$V/FREEZE.sha256"
echo "frozen: $(wc -l < "$V/FREEZE.sha256") files -> $V/FREEZE.sha256"
