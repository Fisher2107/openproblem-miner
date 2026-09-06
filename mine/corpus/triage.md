# Phase 2 — Triage

Corpus: **1,541 problems** after semantic dedupe (1,553 raw, 12 merged), from six clusters.
Produced by `python3 mine/tools/triage.py`, which writes `mine/corpus/problems.jsonl`
(every row carries its class, its tractability score, and the *itemised list of scoring
terms that produced it*) and `mine/corpus/triage.json`.

## Class distribution

| class | meaning | count |
|---|---|---|
| A | finite-witness refutable — a counterexample is a small finite object | 147 |
| B | parametric-construction refutable — needs a symbolic certificate | 144 |
| C | bound-improvable — a constant to push, so search has a gradient | 383 |
| D | proof-only — no finite witness | 867 |

Attack-eligible after exclusions: **1,483**. Excluded: **58** (already solved/refuted, or
`model-knowledge-unverified` provenance, which policy bars from the attack pool).

## The scoring rubric, and the two versions of it

Tractability is a sum of named terms, so that the report's calibration section can ask
which *signals* were wrong rather than which scores were wrong.

| term | delta | rationale |
|---|---|---|
| class base A / C / B / D | +4.0 / +3.0 / +1.5 / 0.0 | A is refutable by one object; C has a gradient; B needs a CAS this container lacks; D has no witness |
| checker cost trivial / poly / exponential / unknown | +1.5 / +1.0 / −0.5 / −0.5 | ease of writing a *correct* checker dominates ease of search |
| statement already formalised in Lean | +1.5 | the T3 cost is partly pre-paid |
| quantified over an enumerable structured class | +1.0 | brute force over the first sizes is meaningful |
| machine-generated graph conjecture (Graffiti / WOWII / TxGraffiti) | +1.5 | structurally the easiest ore: cheap exhaustive verification over a class |
| asymptotic language ("sufficiently large", "infinitely many", O(·)) | −1.5 | no finite witness however the entry was tagged |
| heavy prior machine search | −2.0 | the cheap seam is already mined — this is the signal the run exists to price |
| carries a monetary prize | −1.0 | decades of attention; the mispricing this run wants is the opposite |
| unbounded arithmetic witness space (integers, factorials, primes) | −3.0 | published searches already reach 10^9+; 4 cores add nothing |
| statement > 900 chars / < 320 chars | −1.0 / +0.5 | long statements are usually not self-contained enough to encode correctly |
| already solved or refuted | score forced to 0, removed from pool | test material, not a target |

**Rubric v1 → v2.** The first pass ranked already-refuted WOWII conjectures and
astronomically-searched number-theory problems (Brocard, Euler bricks, consecutive
powerful numbers) at the top, because "a counterexample is a finite object" is true of
them and says nothing about reachability. v2 added the last two rows of the table above.
This change was made **before any search ran** and is recorded here rather than quietly
applied — the triage rubric is not the frozen verifier, and revising it in the light of
its own obviously-wrong output is the point of having it written down.

## Budget allocation

The mission's split is 70% A+C, 20% B, 10% D. What this container can actually spend it on:

- **Class B is unfundable here.** No Gröbner engine (Singular / Macaulay2 / msolve) and no
  SDP solver could be installed — see `mine/verify/TOOLCHAIN.md`. An ansatz family cannot
  be closed symbolically, so B's 20% is reallocated: **B gets a documented 0%**, and the
  reason is a missing tool, not a judgement about the problems.
- **Class A gets ~60%.** All of it goes to the ten `research open` WOWII / Graffiti.pc
  conjectures, which are the only Class A problems in the corpus with *both* a frozen
  checker and a witness small enough for this hardware.
- **Class C gets ~30%**, concentrated on the bound families with a frozen certificate
  checker (Ramsey, van der Waerden, Schur). Agent H4's own realism ranking says every one
  of these is out of reach of 4 cores in an hour; the budget is spent to establish that
  claim by measurement rather than by assertion.
- **Class D gets ~10%**, spent only on brute-forcing first cases, never on proof attempts.

## The ordering cost we actually paid

The verifier was frozen (`mine/verify/FREEZE.sha256`, 40 files, 71 passing checks) while
harvest clusters H3 and H6 were still running. Those two clusters then delivered 100 more
problems, four of which — Brouwer's conjecture, the total colouring conjecture, the linear
arboricity conjecture, Conway's thrackle conjecture — are Class A graph conjectures that
would have ranked in the attack set had they arrived before the freeze.

They have **no frozen checker, so nothing found about them in this run can ship.** The
freeze is not being reopened to fix this: re-freezing is the exact failure mode this repo
exists to prevent, and the escape hatch for a "genuinely premature" freeze is not worth
spending on a marginal yield gain. The cost is recorded here and in `mine/REPORT.md`, and
the fix for run 2 is one line: **finish the harvest before starting Phase 3.**
