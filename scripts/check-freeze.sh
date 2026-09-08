#!/usr/bin/env bash
# Verify the verifier has not drifted. Exit 0 = intact. Run before EVERY verification.
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/_sha.sh
V=mine/verify
M="$V/FREEZE.sha256"
[ -f "$M" ] || { echo "NOT FROZEN: $M missing. Run scripts/freeze.sh before searching."; exit 2; }
tmp=$(mktemp); ref=$(mktemp)
verify_source_files "$V" > "$tmp"
manifest_source_lines "$M" > "$ref"
if diff -u "$ref" "$tmp" > /dev/null; then
  echo "VERIFIER INTACT ($(wc -l < "$ref") source files)"; rm -f "$tmp" "$ref"; exit 0
fi
echo "VERIFIER DRIFT DETECTED — halt the run and report this."; diff -u "$ref" "$tmp" || true
rm -f "$tmp" "$ref"; exit 1
