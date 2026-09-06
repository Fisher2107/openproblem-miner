# Repo rules — read before doing anything

This repo runs an open-problem mine. The full mission brief is `GOAL.md` (short, the
one-shot prompt) and `MISSION.md` (long, with per-phase detail). Read `GOAL.md` first.

These rules are not advisory. They are what makes the output trustworthy.

## The verifier is frozen

`mine/verify/` is built once, before any search, and then hash-locked by
`scripts/freeze.sh`. After that:

- **Never modify anything under `mine/verify/`.** Run `scripts/check-freeze.sh` before
  every verification; if it reports drift, halt and report rather than continuing.
- If a checker rejects a witness, **the witness is wrong**. Editing a checker so a result
  passes is the worst failure available to this system and invalidates the entire run. If
  you notice yourself about to do it, stop, record it in the report, and treat the result
  as refuted.

## No unexecuted claims

Every claim in any report cites a file path and a command that reproduces it. Never write
up an intended run as a completed one. "I did not run this" is always an acceptable answer.

## Write scope

Attack subagents write **only** to their own `mine/attacks/<problem-id>/`. They never write
to `mine/verify/`, `mine/corpus/`, or `mine/results/`. Put this in every subagent prompt.

## Vocabulary

Nothing is "solved", "proved", or "disproved" below tier T3 (see GOAL.md VERIFY). Below
that it is a **candidate**. This applies to commit messages and PR titles too.

## Committing results

A result enters `mine/results/` only after passing its required tier. Each result is a
directory containing the statement, the witness, the checker invocation, the tier reached,
and a prior-art check. CI re-verifies every committed witness from scratch — see
`.github/workflows/verify.yml`. If CI cannot reproduce it, it is not a result.

## Honest failure

A run that finds nothing and correctly diagnoses why is a success. A run that inflates
near-misses is a failure. If every bandit arm flatlines, stop early and write the negative
report instead of burning the remaining budget.
