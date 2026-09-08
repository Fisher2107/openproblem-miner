# Repo rules — read before doing anything

This repo runs an open-problem mine. The full mission brief is `GOAL.md` (short, the
one-shot prompt) and `MISSION.md` (long, with per-phase detail). Read `GOAL.md` first.
`mine/REPORT.md` is run 1's post-mortem and prices everything below.

These rules are not advisory. They are what makes the output trustworthy.

## The verifier is frozen

`mine/verify/` is built once — **after harvest and triage are complete**, before any search
— and then hash-locked by `scripts/freeze.sh`. After that:

- **Never modify anything under `mine/verify/`.** Run `scripts/check-freeze.sh` before
  every verification; if it reports drift, halt and report rather than continuing.
- If a checker rejects a witness, **the witness is wrong**. Editing a checker so a result
  passes is the worst failure available to this system and invalidates the entire run. If
  you notice yourself about to do it, stop, record it in the report, and treat the result
  as refuted.
- Freezing before the harvest finishes orphans problems: anything harvested later has no
  checker, so nothing found about it can ship. Run 1 lost 100 problems this way, four of
  them attackable. The ordering is a rule, not a preference.
- Checkers cover **witness shapes**, not individual problems. A checker that handles only
  2-colour Ramsey, or only the standard Schur condition, kills every arm whose witness has
  a different shape — run 1 lost two arms to exactly that, neither for mathematical
  reasons. Design the checker family around the witness shapes present in the triage list.

## No compute without a frontier comparison

Every attacked target records `frontier.published_n` (what exhaustive search already ran,
to what size, cited) and `reachable_n` (what this hardware reaches). **A target is
attack-eligible only if `reachable_n > published_n`.** Searching below a published frontier
cannot produce a result no matter how much compute it gets; that is why run 1 returned zero.

If the published frontier cannot be located, the corpus entry is **under-specified, not
novel**. Say so and do not spend on it, and never report coverage as new on that basis.

## No negative without a positive control

A searcher that has not rediscovered a known counterexample of the same shape produces no
evidence, and its "flat after N steps" does not go in the report as a negative. Keep
known-refuted conjectures in the target set as controls. Run 1's first annealer seeded from
a spanning path — which guarantees a Hamiltonian path — and would have reported flat
forever on a family whose counterexamples it could not represent.

## No unexecuted claims

Every claim in any report cites a file path and a command that reproduces it. Never write
up an intended run as a completed one. "I did not run this" is always an acceptable answer.

## Statement drift is a corpus risk, not only a Lean risk

Before spending on a target, read its statement against its own `known_cases` and bounds.
Two run-1 entries carried notation drift — a van der Waerden entry whose prose and data used
opposite conventions, and an exclusion clause naming one exception where the truth is three
— either of which would have produced a fake result. The Lean back-translation step catches
drift at T3; nothing catches it at harvest except reading.

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
