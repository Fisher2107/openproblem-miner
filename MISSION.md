# MISSION: Open-Problem Mining Run

You are the orchestrator of an autonomous mathematical discovery run. Your job is not to
"do math research." Your job is to **run a mine**: harvest a large corpus of pre-registered
open problems, triage them by **frontier gap**, spend compute only where your reachable
frontier exceeds the frontier already published, and ship only results a proof kernel has
signed off on.

Work in `./mine/`. Create it. Everything below lands there.

**Read `mine/REPORT.md` before starting.** Run 1 of this mine returned zero results, and the
reason was not difficulty or luck: it spent every core-hour in regions that had already been
swept. WOWII conjectures were searched at n ≤ 10 when that family's known counterexamples
sit at n = 11, 13 and 18; Erdős–Straus was pushed to N = 10⁴ against a published 10¹⁷;
R(5,5) was attacked with four core-hours against a record that absorbed roughly 80 CPU-years.
The rubric asked "is this class enumerable". The question that decides the outcome is **"has
anyone already looked, and how far"**. Every change in this document follows from that.

---

## 0. DEFINITION OF DONE

The run is complete when `mine/REPORT.md` exists and contains, with on-disk evidence for
every claim:

1. A corpus of **≥ 2000 open problems** in `mine/corpus/problems.jsonl`, each with a source
   citation and a populated `frontier` field (§2.2). At most 10% may be class D.
2. Every problem triaged into class A/B/C/D with a tractability score (rubric in §3), and
   marked attack-eligible only where `reachable_n > published_n`.
3. A **frozen, hash-locked verifier harness** in `mine/verify/`, built after the harvest and
   triage were complete and tested against known-good and known-bad inputs BEFORE any
   search ran.
4. Attack logs for **≥ 40 problems**, including failed ones, in `mine/attacks/<id>/`, each
   recording its frontier comparison and its positive-control result.
5. A yield table: attempts, compute spent, and results by tier and by class.
6. Either ≥ 1 **T3-verified** result (§5) — or an honest negative report explaining which
   part of the triage rubric was wrong. **A zero-result run with a correct diagnosis is a
   success. A run that claims results it cannot reproduce is a total failure.**

You have finished when the report is written, not when you have found something.

---

## 1. HARD CONSTRAINTS — read twice

- **No compute on any target without a recorded frontier comparison.** A target is
  attack-eligible only if the size your hardware reaches exceeds the size already searched
  in the literature. If you cannot locate the published frontier, the corpus entry is
  under-specified — that is not the same as novel, and it does not license spending.
- **No negative from a searcher that has not passed a positive control.** Until the
  instrument has rediscovered a known counterexample of the same shape, its "objective flat
  after N steps" is not evidence and does not enter the report as one.
- **Harvest and triage complete before the verifier is built.** Run 1 froze on schedule and
  orphaned 100 late-arriving problems — four of them attackable class A — because they had
  no checker and nothing found about them could ship.
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

## 1b. PHASE 0 — PROBE THE ENVIRONMENT FIRST

Before planning anything, establish what this container can actually do and write it to
`mine/verify/TOOLCHAIN.md`: which of Lean 4 + mathlib (**and its olean cache** — if that is
blocked, mathlib must be compiled from source, which will be the largest compute item in the
run), nauty/geng, a SAT and an SMT solver, a Gröbner engine (Singular, Macaulay2, msolve),
and an SDP solver actually install; and which mathematical sources egress reaches.

**The budget split in §3 is derived from this probe, not fixed in advance.** A class whose
certificate engine is missing gets 0% and the report says so. Run 1 reserved 20% of its
budget for class B and then could install neither Gröbner nor SDP, leaving 144 problems
untouched and the budget to be reallocated mid-run.

Also measure, once, how much CPU a **detached** background process actually receives between
orchestrator turns. In run 1 it was about 3 minutes per 54 minutes of wall clock, because the
container suspends between turns — roughly a 90% loss. Plan long sweeps accordingly (§5).

---

## 2. PHASE 1 — HARVEST (parallel subagents)

Spawn **six subagents in parallel**, one per source cluster. Give each the corpus schema
in §2.2 verbatim and tell it to append to its own `mine/corpus/raw/<cluster>.jsonl`, never
to a shared file. Each returns a count and a list of fields it could not populate.

**Harvest for breadth in under-attended families, not depth in famous ones.** Run 1's corpus
was 56% proof-only lottery tickets and 3.4% machine-generated conjectures — and the only
genuinely unswept ground it found in six clusters was inside that 3.4%. The cluster weights
below are inverted from run 1's accordingly.

### 2.1 Cluster assignments

**Agent H1 — Machine-generated graph-invariant conjectures. THIS IS THE PRIMARY CLUSTER;
target ≥ 2000 entries on its own.** Graffiti and Graffiti.pc conjecture lists, TxGraffiti,
Written on the Wall / WOWII, AutoGraphiX output, House of Graphs, and published lists of
unresolved graph-invariant inequalities. Four properties make this the ore body: the
statements are *numerous*, they are *heuristically generated* rather than human-vetted so a
real fraction of them are simply false, they are *cheap to check* by exhaustive enumeration,
and their published exhaustive frontier is usually **zero** — nobody has swept them, because
nobody has a reason to. Do not stop at the famous ones in the family; the long tail is the
point. For each, record the hypothesis class verbatim (girth, degree, connectivity,
planarity, bipartiteness) — §3 schedules on exactly that.

**Agent H2 — Formal corpus.** Clone Google DeepMind's `formal-conjectures` repo and any
comparable Lean 4 collections of formalized open statements. Also sweep `mathlib` for
`sorry` and for TODO-marked open statements. The formalization cost is already paid, so
these skip straight to attackable and to T3. Record the Lean declaration verbatim and the
file path. **Read the docstrings for prior exhaustive sweeps** — run 1 found one family's
entire published frontier sitting in a single Lean docstring, and finding it repriced the
whole seam.

**Agent H3 — Erdős corpus.** `erdosproblems.com`, joined to `formal-conjectures` where the
same problem appears in both. Capture the problem number, statement, status, prize, and any
"known cases" notes. Be aware that this cluster skews hard toward class D and toward
problems with enormous published frontiers; harvest it, but expect most of it to fail the
§3 gate.

**Agent H4 — Numerical bound tables (Class C seam).** Radziszowski's dynamic survey of
small Ramsey numbers; Sloane's tables for sphere packing, kissing numbers and lattice
records; cage graphs; crossing numbers; Zarankiewicz numbers; van der Waerden and Schur
number tables. Every row where the published lower and upper bound differ is a class C
problem with a built-in objective. **State a feasibility verdict per row and trust it.**
Run 1's H4 agent correctly judged every bound family out of reach before any compute was
spent; the orchestrator spent the compute anyway and confirmed the harvester was right in
every single case.

**Agent H5 — Curated open-problem lists.** Open Problem Garden; Wikipedia's list of
unsolved problems and its per-field children; Polymath pages; Smale's list; the Millennium
problems (tag D immediately — ballast, not targets).

**Agent H6 — Literature sweep.** arXiv `math.CO`, `math.NT`, `cs.DM` from the last ~5 years,
full-text searched for statements flagged as still open ("we conjecture", "remains open",
"Conjecture N"). Prefer the bulk API. Keep only statements that are (a) self-contained in
under ~5 lines and (b) quantified over an enumerable class. Discard anything you cannot
state precisely — a vague corpus entry costs more later than it is worth.

**Class D intake is capped at 10% of the final corpus.** No finite witness means no witness
this pipeline can check, so a D entry can consume harvest and triage effort and can never
produce a result. Run 1 carried 867 of them.

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
  "hypothesis_class": "the restriction the statement quantifies over, verbatim: 'connected, girth >= 6' | 'cubic, bipartite, planar, 3-connected' | 'all graphs' | 'all integers'",
  "frontier": {
    "published_n": null,
    "published_source": "citation for the sweep already run, or 'not located'",
    "reachable_n": null,
    "reachable_basis": "how you estimated it on this hardware"
  },
  "known_cases": "what has been verified/proved so far",
  "current_bounds": {"lower": null, "upper": null},
  "prior_attempts": "notable attacks in the literature, if noted at source",
  "prize": null,
  "class": null,
  "tractability": null,
  "notes": ""
}
```

**`frontier` is the field this run turns on, and it is required.** `published_n` is the size
to which an exhaustive search has already been run, with a citation — from a paper, a
docstring, a README, a table, anywhere. Populate it deliberately; do not leave it for triage
to guess. Three readings and what each means:

- `published_n` located and small → the target is live if you can beat it.
- `published_n` located and large → the target is dead for this pipeline. Say so and move on.
- **`not located` → the entry is under-specified, NOT novel.** Run 1 could find no published
  bound for three of six number-theory targets, and in one of those the "known examples" that
  search kept surfacing turned out, on inspection, to answer the *opposite* direction of the
  conjecture. Absence of a located frontier is a warning about the entry, never a licence to
  claim new coverage.

Then dedupe across clusters into `mine/corpus/problems.jsonl` — the same conjecture appears
under different names in different sources, so match on statement semantics, not on title.
Record merged aliases. **A hash of a normalised statement string is not semantic dedupe**: it
catches near-identical wordings and misses the same conjecture stated in two vocabularies, so
run 1 merged only 12 of 1,553 entries while its own agents recognised more overlap by hand.
Use embeddings or pairwise comparison, and report the method.

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

### 3.1 The gate — apply this before anything else

**A target is attack-eligible if and only if `reachable_n > published_n`.** Compute
`reachable_n` from the actual hardware, the actual class size, and the actual per-instance
check cost, and record the arithmetic. Everything failing the gate is triaged, recorded, and
not attacked, however famous or tempting it is.

This single rule is the difference between run 1 and this run. Searching below a frontier
someone has already passed cannot produce a result at any budget. Run 1's ratios of our
frontier to the published one ran from 10⁻² down to 10⁻¹³; a hundredfold more compute would
have changed none of them.

### 3.2 Score on hypothesis restrictiveness, not statement tractability

Then score **tractability 0–10**, and make the dominant term **how restrictive the
hypothesis class is** — because that is what buys reach past the frontier. A restrictive
hypothesis shrinks the class, which is why run 1 reached n = 16 on a conjecture requiring
girth ≥ 6, and n = 22 on cubic + bipartite + planar + 3-connected, while general-graph
sweeps stalled at n = 10 on the same hardware. Simple-looking statements over all graphs are
the trap: they read as tractable and they are the ones already swept.

Remaining terms: smallness of the smallest plausible witness; whether a correct checker is
easy to write; how much of the statement is already formalized; and prior attack history —
heavy prior counterexample search is a negative signal, and long attention with no attempted
refutation is a positive one. Note that run 1 could not test the second half of that
signal, because no harvested source recorded whether a refutation search had ever been run.
That is exactly what the `frontier` field now exists to capture.

**Exclude unbounded-arithmetic targets** unless your frontier can exceed the published one.
"A counterexample is a finite object" is true of Brocard's problem and of Euler bricks, and
both are searched far past anything reachable here.

**Budget allocation is derived from the Phase-0 probe, not fixed.** Fund only classes whose
certificate engine exists: no Gröbner or SDP means class B gets 0%, stated plainly, not 20%
reallocated mid-run. Cap D at its 10% corpus share or below. Where a harvester has recorded
a feasibility verdict on its own cluster, that verdict gates the attack list directly — do
not write it down and then override it. Write `mine/corpus/triage.md` explaining the
allocation and why.

---

## 4. PHASE 3 — BUILD THE VERIFIER (after harvest and triage, before any search)

Non-negotiable ordering, in both directions: **Phases 1 and 2 must be complete before you
freeze**, and the freeze must happen before any search. Run 1 got the second half right and
the first half wrong — clusters delivered 100 problems after `freeze.sh` ran, including four
attackable class-A graph conjectures, and none of them could ever have shipped because the
frozen verifier had no checker for them. The freeze was correctly not reopened, which is what
made the error permanent.

In `mine/verify/`, set up and smoke-test whatever of this stack the environment supports:
Lean 4 + mathlib (via elan/lake); a SAT solver (CaDiCaL or Kissat) and an SMT solver (Z3);
`nauty`/`geng` for graph enumeration; Python with `sympy`, `mpmath`, and exact rational or
interval arithmetic (`flint`/`arb` if available); a CAS for Gröbner bases (Singular,
Macaulay2, or `msolve`); an SDP solver for sum-of-squares certificates.

Install what is missing and record what you could not install — a missing component
narrows which classes you can ship, and the report must say so.

**Write checkers per witness shape, not per problem.** Enumerate the witness shapes present
in the triaged attack list — "k-colour Ramsey edge partition for arbitrary k", "Schur
partition, standard and weak conditions", "graph-invariant inequality over an arbitrary
hypothesis class", "integer tuple satisfying a Diophantine predicate" — and write one
parameterised checker per shape. Run 1 wrote per-problem checkers and lost two arms to the
gap: R(3,3,3,3) had no multi-colour schema, and the weak Schur number needed an `x < y`
condition the frozen standard-Schur checker does not implement. Neither was a search failure
and neither could be repaired after the freeze.

Every checker is a standalone script that reads a witness file and exits 0 or nonzero.
**Test every checker against a known-true and a known-false input before trusting it.** An
unvalidated checker is worse than no checker. Validate at least one against a *published*
counterexample, so the accept path is known to work and not merely the reject path.

Then freeze: hash the directory into `mine/verify/FREEZE.sha256`. Hash source files only —
run `scripts/freeze.sh` with `PYTHONDONTWRITEBYTECODE=1` and exclude `__pycache__`, or the
manifest pins gitignored bytecode and every later freeze check reports false drift
(`mine/logs/FREEZE-DEFECT.md`).

---

## 5. PHASE 4 — ATTACK (parallel subagents, bandit-scheduled)

### 5.0 Wave 1 is a breadth sweep, not a set of deep arms

Before any problem gets a dedicated agent, run **one uniform exhaustive sweep across every
attack-eligible class-A statement at once**, each starting at **its own `published_n + 1`**
— never at n = 3. Only statements this sweep flags earn a deep arm in a later wave.

The arithmetic: run 1 spent 442 million evaluations on ten conjectures and found nothing.
The same compute spread over a thousand unswept statements at their frontier size is roughly
a hundred times as many chances at one that is actually false, and machine-generated
conjectures have a genuinely nonzero false rate — the one counterexample run 1's machinery
rediscovered came from exactly that family. Depth is what you spend *after* breadth has
pointed somewhere.

**Run long sweeps in the foreground, in turn-sized chunks**, and slice them so that a partial
result is still an exact statement ("all connected graphs on 11 vertices with at most k
edges"), not a meaningless fragment. Detached background sweeps received about 3 minutes of
CPU per 54 minutes of wall clock in run 1, because the container suspends between orchestrator
turns — a ~90% loss that no amount of patience recovers.

### 5.1 Deep arms

Take the top ~40 flagged problems, respecting the class allocation from §3. Attack them in
waves of 6–8 parallel subagents, each owning one problem and one budget.

### Per-problem protocol, given to each attack subagent

Escalate up a cost ladder and stop the moment something works:

0. **Pass the positive control.** Before its own negatives count for anything, the searcher
   must rediscover a known counterexample of the same shape. See "Rules" below.
1. **Brute force the small cases.** Exhaustively enumerate, starting above the published
   frontier. This alone has killed real conjectures and costs almost nothing.
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

- **A positive control is a precondition, not a nicety.** Keep known-refuted conjectures of
  the same shape in the target set. Until this searcher has rediscovered one, it has produced
  no evidence and its "flat" is not reportable. Run 1's first annealer seeded every restart
  from a random spanning path — which guarantees a Hamiltonian path — so it could not
  represent a counterexample to the very family it was searching, and would have reported
  flat forever. It was caught only because a control was in the target set.
- **Record the frontier comparison in `log.md` before spending**, and stop if the target
  fails the gate.
- Log **every failed ansatz family with a structured reason for failure** to
  `mine/memory/negative.jsonl`. This is not bookkeeping, it is the compounding asset of the
  run: later agents read it and prune. Schema: `{problem_id, ansatz, why_failed, cost}`.
- Report progress on a scalar objective each checkpoint so the orchestrator can schedule.
- Never call a verifier you wrote yourself mid-run. Use only the frozen harness.
- Halt at budget and return honestly. "No progress, objective flat after N steps" is a
  valid and useful return value.

### Orchestrator scheduling

Treat each problem as a bandit arm, but **make the reward reach-per-core-hour, not movement
in the scalar objective.** Run 1 tried objective movement and it misled: conjectures 19, 40
and 61 all drove their objective to exactly 0 and stopped there at n = 11 through 14. An arm
that reaches the boundary from below and stays is not about to succeed — objective 0 means
the inequality is *tight*, i.e. the bound is sharp and there is nothing to find. What
actually predicted usable reach was hypothesis restrictiveness, so reallocate toward the
arms whose class is small enough to push past the published frontier fastest.

Kill an arm immediately if it **fails to reproduce a known record or a known counterexample**
near its own threshold — at that point nothing it reports can be trusted, so further budget
cannot buy a result. Read `mine/memory/negative.jsonl` before each wave and inject the
relevant prior failures into the subagent prompt.

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
  `#print axioms` showing no `sorry` and no `ofReduceBool`. **Do not reach for
  `native_decide`**: it is easier and it silently adds an axiom. Keep every computation
  inside what the kernel reduces. If the mathlib olean cache is unreachable, self-contained
  core Lean with no imports still reaches this tier — run 1 demonstrated it.
- **The T3 theorem must state the conjecture and negate it.** Proving several true facts
  about one fixed object and leaving the modus tollens to a prose comment yields a theorem
  whose Lean *type* is strictly weaker than `¬ Conjecture`. Run 1's back-translation caught
  exactly this. Define the conjecture as a `Prop` quantified over the arbitrary structure,
  then prove `¬ Conjecture` by instantiating it.

Class A and B candidates ship at T3 only. Class C ships at T2 and is explicitly flagged
`needs-human-referee`.

**Watch for the dominant failure mode: statement drift.** Formalizing the wrong statement
lets you prove something true that nobody asked about. Before T3, back-translate the Lean
statement into English with a separate agent — given the Lean file and *nothing else*, not
the conjecture, not the corpus entry — and diff it against `statement_nl`. If they differ in
substance, the formalization is wrong, not the source. Flag every T3 result for human
sign-off on the *statement*; that is the one human step in this pipeline you may not remove.

**Drift lives in the corpus as well as in the Lean, and nothing catches it there but
reading.** Two run-1 entries carried it: a van der Waerden entry whose prose said
"2-colouring" while its own `known_cases` used the opposite convention, and an exclusion
clause naming `K_3` as the sole exception when the truth is `K_1, K_2, K_3` — the latter duly
produced a "violation" at `K_2` in an early run. Read each statement against its own bounds
and known cases before spending on it.

---

## 7. PHASE 6 — REPORT

Write `mine/REPORT.md`:

- Yield table: problems harvested, triaged by class, attacked, candidates by tier, compute
  and wall-clock spent, and **cost per verified result**.
- **The frontier table**: for every attacked target, `published_n`, `reachable_n`, and the
  ratio. This is the table that says whether the run was aimed anywhere it could have hit.
  Rows where the published frontier could not be located are reported as under-specified,
  never as novel coverage.
- Every T3 result: statement, witness, reproduction command, Lean file, prior-art check,
  and why it is interesting (who registered the conjecture, what downstream work assumed it).
- Every near-miss, with the specific obstacle.
- **Calibration section**: which triage predictions were wrong. Did the frontier gate select
  better than tractability did? Did hypothesis restrictiveness predict reach? Did any
  positive control fail, and what would have shipped if it had not been there? This is the
  most valuable output of any run, because it prices the next one.
- Which verifier components were missing and what that cost you.
- Recommended next 40 problems.

---

## 8. IF THINGS GO WRONG

- Sources unreachable or rate-limited → go **GitHub-mirror-first**: most of these corpora
  are mirrored in public repositories, and a `clone:<owner>/<repo>@<commit>:<path>` citation
  is stronger than a URL because it is pinned and reproducible. Run 1 harvested 1,523 of
  1,541 entries this way with the open mathematical web blocked. Shrink the target, say so in
  the report, keep going. Never fabricate corpus entries; tag anything resting on model
  memory and bar it from the attack pool.
- **The published frontier cannot be located for most of the corpus** → that is a harvest
  failure, not a licence to attack blind. Go back and mine docstrings, READMEs, and papers
  for sweep records before spending. If it stays unlocatable at scale, say so in the report
  and expect the run's headline to be a coverage claim you cannot call novel.
- Every arm flatlines *and* the frontier table shows every ratio below 1 → you aimed at
  already-swept ground. Stop, and fix the aim rather than the search.
- Lean/mathlib won't install → ship at T2 for everything, label the whole run
  `unformalized`, and make that limitation the first line of the report.
- Every arm flatlines → stop early, do not burn the remaining budget. Write the negative
  report. Diagnosis: was the triage rubric wrong, were the witnesses too large, or were the
  checkers too slow?
- You catch yourself about to edit a checker so a result passes → stop, log the impulse in
  the report, and treat the result as refuted.

Begin with Phase 1. Report the corpus count before starting triage.
