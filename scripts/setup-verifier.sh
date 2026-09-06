#!/usr/bin/env bash
# Install the verification toolchain. Run BEFORE any search (GOAL.md phase P3).
# Records what installed and what did not — a missing component narrows which problem
# classes can ship, and the run report must say so.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=mine/verify/TOOLCHAIN.md
mkdir -p mine/verify
{ echo "# Toolchain report"; echo; echo "Generated: $(date -u +%FT%TZ)"; echo; } > "$OUT"

note() { printf -- "- %s: %s\n" "$1" "$2" >> "$OUT"; echo "  $1: $2"; }
have() { command -v "$1" >/dev/null 2>&1; }

if [ "$(uname)" = "Linux" ]; then
  sudo apt-get update -qq || true
  sudo apt-get install -y -qq z3 nauty libflint-dev python3-pip >/dev/null 2>&1 || true
elif have brew; then
  brew install -q z3 nauty flint >/dev/null 2>&1 || true
fi

python3 -m pip install -q --disable-pip-version-check \
  sympy mpmath networkx python-sat cvxpy scs numpy >/dev/null 2>&1 || true

for t in z3 geng python3; do
  if have "$t"; then note "$t" "OK ($($t --version 2>&1 | head -1 | cut -c1-60))"; else note "$t" "MISSING"; fi
done
for m in sympy mpmath networkx pysat cvxpy; do
  if python3 -c "import $m" 2>/dev/null; then note "python:$m" "OK"; else note "python:$m" "MISSING"; fi
done

# Lean is optional but T3 is unreachable without it.
if have lake; then
  note "lean/lake" "OK ($(lake --version 2>&1 | head -1))"
else
  note "lean/lake" "MISSING — T3 unreachable; run ships as 'unformalized' at T2"
fi

{ echo; echo "## Consequences"; echo;
  echo "- No Lean => no T3. Class A/B results cannot ship; label the run 'unformalized'.";
  echo "- No SAT/SMT => ladder step 2 unavailable; Class A falls back to brute force.";
  echo "- No SDP/CAS => Class B unavailable."; } >> "$OUT"
echo "toolchain report -> $OUT"
