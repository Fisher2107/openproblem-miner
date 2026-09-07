# Defect: the freeze manifest pins two derived bytecode files

**Status: open. Not repaired, because repairing it means editing `mine/verify/`, and this
repo's first rule is that nothing under `mine/verify/` changes after the freeze.**

## What is wrong

`mine/verify/FREEZE.sha256` has 40 entries. Two of them are not source files:

```
mine/verify/lib/__pycache__/exactgraph.cpython-311.pyc
mine/verify/lib/__pycache__/harness.cpython-311.pyc
```

Those are CPython bytecode caches. They were on disk when `scripts/freeze.sh` ran — because
the verifier's own test suite had just been executed, which imports those modules — and
`freeze.sh` hashes every file it finds under `mine/verify/`, so they were pinned along with
the real ones.

They are a bad thing to pin, for two independent reasons:

1. **They are gitignored** (`.gitignore` has `__pycache__/`), so they do not exist in a
   fresh clone. `scripts/check-freeze.sh` then sees 38 files where the manifest lists 40 and
   reports drift.
2. **They are not reproducible.** A `.pyc` embeds the source file's mtime and size, so it is
   regenerated with different bytes whenever the sources are checked out afresh — which is
   exactly what happened when this work was replayed onto a new branch.

## Consequence

`scripts/check-freeze.sh` — and therefore `scripts/verify-results.sh` and the
`.github/workflows/verify.yml` CI job — **report `VERIFIER DRIFT` on any fresh checkout**,
including CI. This is a manifest-hygiene bug, not a modified checker.

## Proof that no checker actually changed

Every one of the 38 **source** files under `mine/verify/` — all 15 checkers, the exact
arithmetic library, the harness, and the test fixtures — hashes to exactly its frozen value.
Reproduce:

```bash
. scripts/_sha.sh
tmp=$(mktemp)
find mine/verify -type f ! -name FREEZE.sha256 ! -path "*__pycache__*" -print0 \
  | LC_ALL=C sort -z \
  | while IFS= read -r -d '' f; do printf '%s  %s\n' "$(sha256_stdin < "$f")" "$f"; done > "$tmp"
diff <(grep -v __pycache__ mine/verify/FREEZE.sha256) "$tmp" && echo "ALL 38 SOURCE FILES INTACT"
```

That command exits 0. The verifier's logic is untouched; only two derived artefacts that
should never have been in the manifest are unaccounted for.

## Why it was not "fixed"

The obvious repair — delete the two lines from `FREEZE.sha256` — is an edit to the frozen
verifier. That is the precise move this repo exists to forbid, and the fact that it would be
harmless *this* time (zero results were shipped, so nothing passes or fails as a result) is
exactly the reasoning that makes the rule worthless if it is ever accepted. `freeze.sh` also
refuses to re-freeze by design. So the defect is reported instead of repaired, and the
decision is left to a human.

## Fix for run 2 (one line)

`scripts/freeze.sh` should exclude derived files before hashing:

```bash
find "$V" -type f ! -name FREEZE.sha256 ! -path "*__pycache__*" ! -name "*.pyc" -print0
```

and the verifier should be invoked with `PYTHONDONTWRITEBYTECODE=1` so the caches are never
created in the first place. Freeze before running the test suite, not after.
