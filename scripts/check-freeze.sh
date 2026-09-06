#!/usr/bin/env bash
# Verify the verifier has not drifted. Exit 0 = intact. Run before EVERY verification.
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/_sha.sh
V=mine/verify
M="$V/FREEZE.sha256"
[ -f "$M" ] || { echo "NOT FROZEN: $M missing. Run scripts/freeze.sh before searching."; exit 2; }
tmp=$(mktemp)
find "$V" -type f ! -name FREEZE.sha256 -print0 \
  | LC_ALL=C sort -z \
  | while IFS= read -r -d '' f; do printf '%s  %s\n' "$(sha256_stdin < "$f")" "$f"; done \
  > "$tmp"
if diff -u "$M" "$tmp" > /dev/null; then
  echo "VERIFIER INTACT ($(wc -l < "$M") files)"; rm -f "$tmp"; exit 0
fi
echo "VERIFIER DRIFT DETECTED — halt the run and report this."; diff -u "$M" "$tmp" || true
rm -f "$tmp"; exit 1
