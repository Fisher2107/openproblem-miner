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

## How it works

1. **Harvest** — six parallel subagents scrape pre-registered open problems: the Erdős
   problem collection, formalized Lean corpora, curated open-problem lists, published
   bound tables with open gaps, machine-generated graph-invariant conjectures, and recent
   arXiv conjecture statements.
2. **Triage** — every problem is classified by *attack surface*, not by fame:
   - **A** finite-witness refutable — counterexample is a small finite object
   - **B** parametric-construction refutable — needs a symbolic certificate
   - **C** bound-improvable — continuous objective, so search has a gradient
   - **D** proof-only — Riemann-shaped lottery tickets
   
   Budget goes 70% to A+C, 20% to B, 10% to D. Pointing everything at the famous problems
   is the losing move.
3. **Build the verifier first** — before any search, then hash-lock it.
4. **Attack** — waves of subagents on a cost ladder: brute-force small cases → SAT/ILP/SMT
   encodings → evolve short generator *programs* scored by distance-to-violation → symbolic
   close. Scheduled as a bandit; flat arms are killed and their budget reallocated. Failed
   approaches are logged and fed to later waves.
5. **Verify in tiers** — T0 float screen → T1 exact/interval → T2 a fresh agent that sees
   only the statement and the witness, never the original code → T3 Lean, compiling with
   no `sorry`.

## Running it

Point a cloud agent session at this repo and give it `GOAL.md` as the task. `GOAL.md` is a
self-contained one-shot brief under 4,000 characters; `MISSION.md` is the long form with
per-phase detail. `CLAUDE.md` is loaded automatically and carries the non-negotiable rules.

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

Scaffolding only — no mining run has been executed yet. `mine/` is empty by design.

## Prior art worth reading first

FunSearch and AlphaEvolve (evolutionary search over generator programs — the Class A/C
engine), Wagner's reinforcement-learning work on constructing counterexamples in
combinatorics, Lean and mathlib, and Sakana AI's AI Scientist (the autonomous outer loop).
The contribution here is the wrapper: none of the search systems had an autonomous harvest
and triage layer in front of them, and the autonomous loop had no proof kernel behind it.
