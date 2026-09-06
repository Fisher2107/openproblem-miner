# MISSION: Open-Problem Mining Run

You are the orchestrator of an autonomous mathematical discovery run. Your job is not to
"do math research." Your job is to **run a mine**: harvest a large corpus of pre-registered
open problems, triage them by attack surface, spend compute only where a machine-checkable
witness is plausibly reachable, and ship only results a proof kernel has signed off on.

Work in `./mine/`. Create it. Everything below lands there.

---

## 0. DEFINITION OF DONE

The run is complete when `mine/REPORT.md` exists and contains, with on-disk evidence for
every claim:

1. A corpus of **≥ 400 open problems** in `mine/corpus/problems.jsonl`, each with a source URL.
2. Every problem triaged into class A/B/C/D with a tractability score (rubric in §3).
3. A **frozen, hash-locked verifier harness** in `mine/verify/` that you built and tested
   against known-good and known-bad inputs BEFORE any search ran.
4. Attack logs for **≥ 40 problems**, including failed ones, in `mine/attacks/<id>/`.
5. A yield table: attempts, compute spent, and results by tier and by class.
6. Either ≥ 1 **T3-verified** result (§5) — or an honest negative report explaining which
   part of the triage rubric was wrong. **A zero-result run with a correct diagnosis is a
   success. A run that claims results it cannot reproduce is a total failure.**

You have finished when the report is written, not when you have found something.

---

## 1. HARD CONSTRAINTS — read twice

- **Never modify anything in `mine/verify/` after the Phase-3 freeze.** If a verifier
  rejects your witness, the witness is wrong. Editing a checker to make a result pass is
  the single worst failure mode available to you and it has happened to systems like this
  before. After the freeze, write `mine/verify/FREEZE.sha256` and re-check it before every
  verification call. If the hash has drifted, halt and report.
- **Never report a result you have not actually executed.** Every claim in the report cites
  a file path and a command that reproduces it. No "this would show", no summarizing an
  intended run as a completed one.
- **Search agents may not write to `mine/verify/` or `mine/corpus/`.** They write only to
  their own `mine/attacks/<id>/` directory. Enforce this in the subagent prompts.
- **A result is not a discovery until it survives Tier 3** (or Tier 2 + flagged for human
  review, for Class C). Do not use the words "solved", "proved", or "disproved" about
  anything below that bar. Use "candidate".
- **Check for prior discovery before spending budget** and again before reporting. A large
  fraction of apparent finds are in a paper from 1974.
- Respect robots.txt and rate limits when scraping. Prefer official APIs, bulk downloads,
  and git clones over page-by-page crawling. Cache every fetch to `mine/cache/` so you
  never hit the same URL twice.

---

## 2. PHASE 1 — HARVEST (parallel subagents)

Spawn **six subagents in parallel**, one per source cluster. Give each the corpus schema
in §2.2 verbatim and tell it to append to its own `mine/corpus/raw/<cluster>.jsonl`, never
to a shared file. Each returns a count and a list of fields it could not populate.

### 2.1 Cluster assignments

**Agent H1 — Erdős corpus.** `erdosproblems.com`. This is the richest single seam: ~1000
problems, already numbered, already stated crisply, and several have fallen to machine
search recently. Look for a bulk/JSON endpoint or database dump before crawling. Capture
the problem number, statement, status, monetary prize if any, and any "known cases" notes.

**Agent H2 — Formal corpus.** Clone Google DeepMind's `formal-conjectures` repo and any
comparable Lean 4 collections of formalized open statements. Also sweep `mathlib` for
`sorry` and for TODO-marked open statements. These are gold: the formalization cost is
already paid, so they skip straight to attackable. Record the Lean declaration verbatim
and the file path.

**Agent H3 — Curated open-problem lists.** Open Problem Garden; Wikipedia's list of
unsolved problems in mathematics and its per-field children; Polymath problem pages;
Smale's list; the Millennium problems (tag these D immediately, they are corpus ballast,
not targets).

**Agent H4 — Numerical bound tables (Class C seam).** Radziszowski's dynamic survey of
small Ramsey numbers; Sloane's tables for sphere packing, kissing numbers and lattice
records; cage graphs; crossing numbers; Zarankiewicz numbers; van der Waerden and Schur
number tables. **You want every row where the published lower and upper bound differ.**
Each such gap is a Class C problem with a built-in objective function. This cluster will
likely produce your best yield-per-dollar; do not let it get shortchanged.

**Agent H5 — Graph-invariant conjecture generators.** Graffiti / Graffiti.pc conjecture
lists, AutoGraphiX output, House of Graphs, and published lists of unresolved
graph-invariant inequalities. These are machine-generated conjectures over a class with
cheap exhaustive verification — structurally the easiest ore in the mine.

**Agent H6 — Literature sweep.** arXiv `math.CO`, `math.NT`, `cs.DM` from the last ~5 years.
Search full text for conjecture statements that are flagged as still open ("we conjecture",
"remains open", "Conjecture N"). Prefer the arXiv bulk API. Keep only statements that are
(a) self-contained in under ~5 lines and (b) quantified over an enumerable class. Discard
anything you cannot state precisely — a vague corpus entry costs you more later than it
is worth.

### 2.2 Corpus schema

One JSON object per line:

```json
{
  "id": "erdos-0707",
  "source": "erdosproblems.com",
  "url": "https://...",
  "statement_nl": "precise natural-language statement, self-contained",
  "statement_formal": "Lean 4 declaration if available, else null",
  "quantifier_shape": "forall-graphs | forall-integers | exists-construction | bound | other",
  "witness_type": "finite-object | parametric-family | numeric-bound | none",
  "witness_check_cost": "trivial | poly | exponential | unknown",
  "known_cases": "what has been verified/proved so far",
  "current_bounds": {"lower": null, "upper": null},
  "prior_attempts": "notable attacks in the literature, if noted at source",
  "prize": null,
  "class": null,
  "tractability": null,
  "notes": ""
}
```

Then dedupe across clusters into `mine/corpus/problems.jsonl` — the same conjecture appears
under different names in different sources, so match on statement semantics, not on title.
Record merged aliases.

---

## 3. PHASE 2 — TRIAGE

This phase decides whether the run succeeds. **Do it carefully; do not delegate it to a
single cheap pass.** Classify every problem:

- **A — finite-witness refutable.** Universally quantified over an enumerable structured
  class; a counterexample is a finite object verifiable in polynomial time. (Most Erdős
  combinatorics, graph-theory inequalities, Graffiti conjectures.) Highest priority.
- **B — parametric-construction refutable.** A counterexample lives in an algebraic family
  and needs a symbolic certificate. Requires a CAS to close.
- **C — bound-improvable.** No truth value, just a constant to push. Has a continuous,
  measurable objective, which means search has a gradient. The steady seam.
- **D — proof-only.** No finite witness. Riemann-shaped. Lottery tickets.

Then score **tractability 0–10** on: smallness of the smallest plausible witness; whether
brute force over the first few sizes is even feasible; whether a checker is easy to write
correctly; how much of the statement is already formalized; and how heavily the problem has
already been attacked from below (heavy prior counterexample search is a negative signal;
30 years of attempted *proofs* with no attempted refutation is a strong positive signal —
that gap is exactly the mispricing this run exists to exploit).

**Budget allocation: 70% of compute on A and C, 20% on B, 10% on D.** The instinct to point
everything at the famous problems is the losing move; resist it. Write
`mine/corpus/triage.md` explaining the allocation you chose and why.

---

## 4. PHASE 3 — BUILD THE VERIFIER FIRST

Before any search. Non-negotiable ordering.

In `mine/verify/`, set up and smoke-test whatever of this stack the environment supports:
Lean 4 + mathlib (via elan/lake); a SAT solver (CaDiCaL or Kissat) and an SMT solver (Z3);
`nauty`/`geng` for graph enumeration; Python with `sympy`, `mpmath`, and exact rational or
interval arithmetic (`flint`/`arb` if available); a CAS for Gröbner bases (Singular,
Macaulay2, or `msolve`); an SDP solver for sum-of-squares certificates.

Install what is missing and record what you could not install — a missing component
narrows which classes you can ship, and the report must say so.

Write one checker per problem you intend to attack, as a standalone script that reads a
witness file and exits 0 or nonzero. **Test every checker against a known-true and a
known-false input before trusting it.** An unvalidated checker is worse than no checker.

Then freeze: hash the directory into `mine/verify/FREEZE.sha256`.

---

## 5. PHASE 4 — ATTACK (parallel subagents, bandit-scheduled)

Take the top ~40 problems by tractability, respecting the class allocation. Attack them in
waves of 6–8 parallel subagents, each owning one problem and one budget.

### Per-problem protocol, given to each attack subagent

Escalate up a cost ladder and stop the moment something works:

1. **Brute force the small cases.** Exhaustively enumerate the smallest instances. This
   alone has killed real conjectures and costs almost nothing.
2. **Encode and solve.** Express "a counterexample of size n exists" as SAT/ILP/SMT and
   hand it to the solver for increasing n.
3. **Evolve generator programs, not objects.** Search over short programs that *construct*
   candidate objects, scored by a fitness function measuring distance to violation. This is
   the key trick — the program space is vastly better structured than the object space.
   Keep a population, mutate with the model, retain the best.
4. **Symbolic close (Class B).** Propose ansatz families, then let the CAS decide them via
   Gröbner bases, resultants, or SOS certificates.

For Class C, replace "violation" with the bound itself and just optimize it, logging every
improvement over the published record.

### Rules for every attack agent

- Log **every failed ansatz family with a structured reason for failure** to
  `mine/memory/negative.jsonl`. This is not bookkeeping, it is the compounding asset of the
  run: later agents read it and prune. Schema: `{problem_id, ansatz, why_failed, cost}`.
- Report progress on a scalar objective each checkpoint so the orchestrator can schedule.
- Never call a verifier you wrote yourself mid-run. Use only the frozen harness.
- Halt at budget and return honestly. "No progress, objective flat after N steps" is a
  valid and useful return value.

### Orchestrator scheduling

Treat each problem as a bandit arm; reward is measured movement in its scalar objective.
After each wave, kill arms that have flatlined and reallocate their remaining budget to
arms still moving. Read `mine/memory/negative.jsonl` before launching each new wave and
inject the relevant prior failures into the subagent prompt.

---

## 6. PHASE 5 — VERIFICATION TIERING

No candidate is promoted without passing every tier below it:

- **T0** — floating-point / numerical check. Fast, unsound, screening only.
- **T1** — exact recheck in rational or interval arithmetic. No floats anywhere.
- **T2** — **independent reimplementation.** Spawn a fresh subagent, give it only the
  natural-language statement and the witness — never the original code, never the original
  reasoning — and have it write a checker from scratch and confirm. This is what catches
  the case where the constructor and the checker share the same misreading of the problem.
- **T3** — Lean formalization of the statement plus the witness, compiling clean with
  `#print axioms` showing no `sorry`.

Class A and B candidates ship at T3 only. Class C ships at T2 and is explicitly flagged
`needs-human-referee`.

**Watch for the dominant failure mode: statement drift.** Formalizing the wrong statement
lets you prove something true that nobody asked about. Before T3, back-translate the Lean
statement into English with a separate agent and diff it against `statement_nl`. If they
differ in substance, the formalization is wrong, not the source. Flag every T3 result for
human sign-off on the *statement* — that is the one human step in this pipeline you may
not remove.

---

## 7. PHASE 6 — REPORT

Write `mine/REPORT.md`:

- Yield table: problems harvested, triaged by class, attacked, candidates by tier, compute
  and wall-clock spent, and **cost per verified result**.
- Every T3 result: statement, witness, reproduction command, Lean file, prior-art check,
  and why it is interesting (who registered the conjecture, what downstream work assumed it).
- Every near-miss, with the specific obstacle.
- **Calibration section**: which triage predictions were wrong. Did Class A actually
  outperform C? Was the "long-unrefuted" signal predictive? This is the most valuable
  output of run 1, because it prices run 2.
- Which verifier components were missing and what that cost you.
- Recommended next 40 problems.

---

## 8. IF THINGS GO WRONG

- Sources unreachable or rate-limited → shrink the corpus target, say so in the report,
  keep going. Do not fabricate corpus entries.
- Lean/mathlib won't install → ship at T2 for everything, label the whole run
  `unformalized`, and make that limitation the first line of the report.
- Every arm flatlines → stop early, do not burn the remaining budget. Write the negative
  report. Diagnosis: was the triage rubric wrong, were the witnesses too large, or were the
  checkers too slow?
- You catch yourself about to edit a checker so a result passes → stop, log the impulse in
  the report, and treat the result as refuted.

Begin with Phase 1. Report the corpus count before starting triage.
