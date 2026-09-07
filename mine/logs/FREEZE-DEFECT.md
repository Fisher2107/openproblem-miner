# Defect: the freeze manifest pins two derived bytecode files

**Status: resolved in `scripts/`, without touching `mine/verify/`. See "How it was fixed"
below. `mine/verify/FREEZE.sha256` is byte-for-byte as it was written at freeze time, and
all 38 source files still hash to their frozen values.**

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
`.github/workflows/verify.yml` CI job — **reported `VERIFIER DRIFT` on every fresh
checkout**, including CI, which failed the `reproduce` job on PR #2. This is a
manifest-hygiene bug, not a modified checker.

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

## What was rejected

Deleting the two lines from `FREEZE.sha256` — the obvious one-line repair — is an edit to
the frozen verifier. That is the precise move this repo exists to forbid, and the fact that
it would be harmless *this* time (zero results shipped, so nothing passes or fails as a
result) is exactly the reasoning that makes the rule worthless once accepted. `freeze.sh`
also refuses to re-freeze by design.

## How it was fixed

In `scripts/`, which is outside the frozen tree and was never hash-locked. `_sha.sh` gained
two helpers, used by both `freeze.sh` and `check-freeze.sh`:

- `verify_source_files` — the same `find`, excluding `*/__pycache__/*`.
- `manifest_source_lines` — the same exclusion applied to the *stored* manifest, so a
  manifest written before this rule existed compares cleanly.

The comparison is therefore over the 38 source files, and both sides are filtered
identically. `mine/verify/` is untouched. `check-freeze.sh` now prints
`VERIFIER INTACT (38 source files)`.

**The exclusion is `__pycache__/` only, and that narrowness is the point.** An earlier
version of this fix also excluded `*.pyc` anywhere, which opened a real hole: Python 3
imports a sourceless `.pyc` sitting where the `.py` would be, so a file like
`mine/verify/checkers/evil.pyc` could have been added without detection. Inside
`__pycache__/` that is not reachable — the loader uses a cache only when the matching `.py`
exists and its hash/mtime agree, and every `.py` there is frozen.

Verified against a tamper matrix, each case run on a disposable copy of the frozen tree:

| case | expected | result |
|---|---|---|
| clean checkout | intact, exit 0 | exit 0, 38 files |
| one byte appended to `lib/harness.py` | drift, exit 1 | exit 1 |
| a frozen checker deleted | drift, exit 1 | exit 1 |
| a new file added under `mine/verify/` | drift, exit 1 | exit 1 |
| loose `checkers/evil.pyc` added | drift, exit 1 | exit 1 |
| regenerated `lib/__pycache__/*.pyc` present | intact, exit 0 | exit 0 |

## Still to do in run 2

Run the verifier with `PYTHONDONTWRITEBYTECODE=1` and freeze *before* running the test
suite, so the caches are never created and the manifest never has to be filtered at all.
`GOAL.md` and `MISSION.md` §4 now say so.
