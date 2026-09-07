# openproblem-miner

An autonomous pipeline for **mining verified mathematical discoveries** from the backlog of
pre-registered open problems.

The thesis in one paragraph: autonomous research agents have a reviewer problem — in ML
research there is no oracle, so systems like Sakana's AI Scientist have to approximate peer
review with an LLM ensemble that lands around 69% balanced accuracy, and every downstream
weakness (hallucination, unverifiable claims, shallow rigor) follows from that. Mathematics
has had a sound, ~100%-precision reviewer for twenty years. It's called Lean. This repo is
the factory built around it: **take the autonomous research loop, delete the automated
reviewer, and bolt the loop onto a proof kernel.** False positives then cost nothing — they
get rejected by a compiler instead of by a human's afternoon.

The second premise is sociological. Human math incentives reward *proving*, so conjectures
that are widely believed but were never seriously attacked *from below* are systematically
under-searched. Falsification is far cheaper than proof, and a counterexample is often a
small finite object. That gap is the ore body.

## Run 1 outcome (2026-09-06)

**Zero new results, reported as zero.** `mine/REPORT.md` is the full account; the short
version:

- **1,541 problems** harvested and triaged, every one citing a cloned file or a search
  result — none resting on model memory.
- A **frozen verifier** (40 files, 71 passing checks, validated against two *published*
  counterexamples before the freeze) that was never reopened, and that **caught a false
  witness** produced by a buggy search script.
- **50 million** exhaustive graph-conjecture evaluations. One negative that appears to be
  new: Written on the Wall II conjecture 141 holds for every connected graph on at most
  16 vertices.
- The most valuable output is the **calibration** section: six triage predictions that were
  wrong, and the rule that replaces them — schedule on how restrictive a conjecture's
  hypotheses are, not on how tractable its statement looks.

## What run 2 changes

Run 1's zero was not bad luck. It spent every core-hour in regions already swept — WOWII at
n ≤ 10 when that family's known counterexamples sit at n = 11, 13 and 18; Erdős–Straus at
10⁴ against a published 10¹⁷. Its rubric asked *is this class enumerable*; the question that
decides the outcome is *has anyone already looked, and how far*. Four changes follow:

- **A frontier gate.** `frontier.published_n` is a required corpus field, and a target is
  attack-eligible only when `reachable_n > published_n`. No compute crosses that line.
- **Breadth over fame.** Machine-generated conjecture families become the primary harvest
  cluster (target ≥ 2000), class D is capped at 10%. Run 1's corpus was 56% proof-only
  lottery tickets and 3.4% machine-generated — and the only unswept ground it found was
  inside the 3.4%.
- **Schedule on hypothesis restrictiveness, not statement tractability.** Restrictive
  hypotheses shrink the class, which is what buys reach: n = 22 on cubic+bipartite+planar
  +3-connected versus n = 10 on general graphs, same hardware.
- **Positive controls are a precondition.** No searcher's negative counts until it has
  rediscovered a known counterexample of the same shape.

## How it works

1. **Probe** — establish the toolchain and egress first; the budget split is derived from
   what actually installs, not fixed in advance.
2. **Harvest** — six parallel subagents, weighted toward machine-generated conjecture
   families, each entry carrying a cited published search frontier.
3. **Triage** — every problem is classified by *attack surface*, not by fame:
   - **A** finite-witness refutable — counterexample is a small finite object
   - **B** parametric-construction refutable — needs a symbolic certificate
   - **C** bound-improvable — continuous objective, so search has a gradient
   - **D** proof-only — Riemann-shaped lottery tickets
   
   …and then gated: only targets whose reachable frontier exceeds the published one are
   attacked at all. Pointing everything at the famous problems is the losing move.
4. **Build the verifier** — after the harvest and triage are complete, before any search,
   with checkers written per *witness shape*; then hash-lock it.
5. **Attack** — one broad sweep across every eligible statement at its own frontier size
   first, then deep arms on whatever that flags: brute force → SAT/ILP/SMT encodings →
   evolve short generator *programs* scored by distance-to-violation → symbolic close.
   Bandit-scheduled on reach per core-hour. Failed approaches feed later waves.
6. **Verify in tiers** — T0 float screen → T1 exact/interval → T2 a fresh agent that sees
   only the statement and the witness, never the original code → T3 Lean, compiling with
   no `sorry`.

## Running it

Point a cloud agent session at this repo and give it `GOAL.md` as the task. `GOAL.md` is a
self-contained one-shot brief; `MISSION.md` is the long form with per-phase detail. `CLAUDE.md` is loaded automatically and carries the non-negotiable rules.

```bash
scripts/setup-verifier.sh   # P3: install the toolchain, record what's missing
scripts/freeze.sh           # lock the verifier — run once, before searching
scripts/check-freeze.sh     # confirm no drift — run before every verification
scripts/verify-results.sh   # re-verify every committed result from scratch
```

CI runs `verify-results.sh` on every push. **If a witness doesn't reproduce in a clean
checkout, it isn't a result.**

## What makes the output trustworthy

- **The verifier is frozen.** Built and hash-locked before any search, never touched again.
  If a checker rejects a witness, the witness is wrong. Editing a checker so a result passes
  invalidates the whole run — this is the single worst failure mode available to a system
  like this, and it is guarded structurally rather than by good intentions.
- **Independent reimplementation at T2.** A fresh agent gets only the statement and the
  witness — never the original code or reasoning — and writes a checker from scratch. This
  catches the case where the constructor and the checker share one misreading.
- **Statement back-translation before T3.** The Lean statement is rendered back to English
  by a separate agent and diffed against the original. Formalizing the wrong statement lets
  you correctly prove something nobody asked about; this is the dominant failure mode, and
  human sign-off on the *statement* is the one manual step that cannot be removed.
- **Nothing is "proved" below T3.** Below that it is a *candidate*, in reports and commit
  messages alike.
- **Honest failure is a success condition.** A run that finds nothing and correctly
  diagnoses why prices the next run. A run that inflates near-misses is worthless.

## Status

**Run 1 complete (2026-09-06), zero results, fully reported.** See `mine/REPORT.md` and the
outcome summary above; `bash scripts/reproduce-run1.sh` re-verifies every claim in it.

`GOAL.md`, `MISSION.md` and `CLAUDE.md` have since been revised against run 1's calibration
section — the changes are listed under "What run 2 changes". Run 2 has not been executed.

## Prior art worth reading first

FunSearch and AlphaEvolve (evolutionary search over generator programs — the Class A/C
engine), Wagner's reinforcement-learning work on constructing counterexamples in
combinatorics, Lean and mathlib, and Sakana AI's AI Scientist (the autonomous outer loop).
The contribution here is the wrapper: none of the search systems had an autonomous harvest
and triage layer in front of them, and the autonomous loop had no proof kernel behind it.
