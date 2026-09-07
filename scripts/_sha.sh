# sourced helper: portable sha256 over stdin
sha256_stdin() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum | awk '{print $1}'
  else shasum -a 256 | awk '{print $1}'; fi
}

# The frozen surface is source, never derived bytecode. CPython drops
# __pycache__/*.pyc next to any module it imports, so whether those files exist at
# freeze time depends on nothing but whether the test suite happened to run first —
# and they are gitignored, so a clean checkout never has them at all. Every .py they
# are derived from is hashed here, so excluding them removes no coverage.
# Run freeze.sh with PYTHONDONTWRITEBYTECODE=1 as well.
#
# The exclusion is __pycache__/ ONLY, deliberately narrow. A loose *.pyc elsewhere in
# the tree stays hashed, because Python 3 will import a sourceless .pyc sitting where
# the .py would be; excluding those would let one be added undetected. Inside
# __pycache__/ that is not reachable: the loader uses the cache only when the matching
# .py exists and its hash/mtime agree, and every .py here is frozen.
verify_source_files() {   # $1 = verifier dir -> "<sha>  <path>" lines, sorted
  find "$1" -type f ! -name FREEZE.sha256 ! -path '*/__pycache__/*' -print0 \
    | LC_ALL=C sort -z \
    | while IFS= read -r -d '' f; do printf '%s  %s\n' "$(sha256_stdin < "$f")" "$f"; done
}

# The same exclusion applied to a stored manifest, so one written before this rule
# existed still compares cleanly. __pycache__ lines are the only thing dropped; every
# other line in the manifest must still match its file exactly.
manifest_source_lines() { grep -v -E '/__pycache__/' -- "$1" || true; }
