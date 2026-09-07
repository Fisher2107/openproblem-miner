# Open-problem mine — run 1 report

**Bottom line: zero new results. One end-to-end validated pipeline, three genuinely new
negative results, and a priced diagnosis of why the yield was zero.**

No conjecture in this corpus was refuted, no published bound was improved, and
`mine/results/` is empty. That is the honest outcome, and the rest of this document is
about making it a useful one: what was searched, how far, with what instrument, and which
of the triage rubric's predictions were wrong.

Everything below cites a file and a command. Nothing here is a summary of an intended run.

---

## 1. Yield table

Regenerate with `python3 mine/tools/yield_table.py`.

| stage | number | artefact |
|---|---|---|
| problems harvested (raw, 6 clusters) | **1,553** | `mine/corpus/raw/*.jsonl` |
| after semantic dedupe | **1,541** | `mine/corpus/problems.jsonl` |
| attack-eligible (excludes already-solved and unverified-provenance) | 1,483 | same, field `attack_eligible` |
| frozen checkers written and validated | 15 | `mine/verify/checkers/` |
| files hash-locked in the verifier | 40 | `mine/verify/FREEZE.sha256` |
| verifier self-tests passing (both directions) | 71 | `bash mine/verify/run-tests.sh` |
| graphs exhaustively searched | **> 32 million** | §4 |
| candidates reaching T1 | 0 (new) / 1 (positive control) | §5 |
| **T3-verified new results** | **0** | — |
| cost per verified result | undefined (no results) | — |

### Corpus by cluster

| cluster | source | entries |
|---|---|---|
| H1 | Erdős problems (teorth/erdosproblems joined to formal-conjectures) | 578 |
| H2 | rest of google-deepmind/formal-conjectures + mathlib sweep | 803 |
| H3 | curated lists, via a GitHub mirror of the Wikipedia unsolved-problems list | 70 |
| H4 | numerical bound tables (Ramsey, vdW, Schur, cages, crossing, kissing…) | 19 |
| H5 | Graffiti / Graffiti.pc / TxGraffiti graph-invariant conjectures | 53 |
| H6 | recent literature, via an arXiv conjecture-extraction pipeline on GitHub | 30 |

### Corpus by class

| class | meaning | count |
|---|---|---|
| A | finite-witness refutable | 147 |
| B | parametric-construction refutable | 144 |
| C | bound-improvable | 383 |
| D | proof-only | 867 |

---

## 2. The environment, and what it cost

The container's egress policy allows GitHub, PyPI and the Ubuntu archive, and **blocks
essentially every mathematical source on the open web**: erdosproblems.com, arXiv,
Wikipedia, OEIS, the Radziszowski Ramsey survey, McKay's data pages, House of Graphs, and
the Lean toolchain and mathlib olean caches. Probes and HTTP codes are in
`mine/logs/NETWORK.md`.

Consequences that shaped the whole run:

- The harvest became **GitHub-mirror-first**. Every corpus entry cites either a
  `clone:<owner>/<repo>@<commit>:<path>` or a `websearch:<url>`; entries resting on model
  memory alone are tagged `model-knowledge-unverified` and are barred from the attack pool
  by policy. Zero entries in the final corpus carry that tag.
- Lean 4 was installed by unpacking the GitHub release tarball by hand after
  `elan toolchain install` was refused by the proxy. **The mathlib olean cache is blocked**
  (403 on all 8,865 files, logged), so mathlib had to be compiled from source; a 1,293-module
  `SimpleGraph` subset did build successfully, but `Mathlib.Data.Real.Basic` is not in it.
- **No Gröbner engine and no SDP solver could be installed**, so Class B — 144 problems —
  was unfundable. Its 20% budget was reallocated. This is a tooling limit, not a judgement
  about the problems.

Full accounting: `mine/verify/TOOLCHAIN.md`.

---

## 3. The verifier (built and frozen before any search)

`mine/verify/` holds 15 standalone checkers over an exact-arithmetic graph library. **No
floating point anywhere**: counts are integers, averages are `Fraction`, and the single
square root in the corpus (WOWII 100) is decided by exact integer comparison. A crash in
any checker is converted to REFUSE, never ACCEPT.

Validated *before* `scripts/freeze.sh` ran, five independent ways:

1. hand-computed invariants on five reference graphs (Petersen, C5, K4, P4, K3,3);
2. the one identity used in place of a definition — `Ls(G) = n − γ_c(G)` — checked against
   brute-force spanning-tree enumeration for **every connected graph on 3..7 vertices**;
3. the induced-path characterisation checked against the literal Lean list definition for
   every connected graph on 2..6 vertices;
4. the minimal-total-dominating-set shortcut checked against the literal subset definition
   over the same range;
5. the graph6 decoder checked against `nauty-listg`.

Then the accept path was fired end to end on **two published counterexamples** (WOWII 194
and 200), reproducing their published invariant values exactly. A checker whose accept path
has never fired is not a validated checker.

`bash mine/verify/run-tests.sh` → 71 checks, 0 failures. `bash scripts/check-freeze.sh` →
`VERIFIER INTACT (40 files)`. **The freeze was never reopened.** Two moments where it would
have helped are recorded in §7 as costs, not repaired.

---

## 4. What was actually searched

### 4.1 The ten open WOWII / Graffiti.pc conjectures (Class A, the primary seam)

Full log: `mine/attacks/wave1-wowii-exhaustive/log.md`, `mine/attacks/wave2-wowii-families/log.md`.

| search | scope | candidates |
|---|---|---|
| exhaustive, all connected graphs n ≤ 10 | 11,989,762 graphs | 0 |
| exhaustive, conjecture 141 only, all girth ≥ 5 graphs n = 11..16 | 20,147,011 graphs | 0 |
| generator family 1 (validated by positive control) | 13,448 graphs, n ≤ 18 | 0 |
| generator family 2 (does **not** pass the control) | 7,460 graphs, n ≤ 18 | 0 |
| simulated annealing, n = 11..14, all ten objectives | 25 restarts × 20k steps per arm | 0 |

Two of these are genuinely new coverage rather than re-treading:

> **Conjecture 141 holds for every finite simple connected graph on at most 16 vertices.**
> The other nine hold for every one on at most 10 vertices.

The 141 result comes from a proof-shaped shortcut rather than brute force: `tree(G) ≥
max_v l(v) + 1` always (a vertex plus a maximum independent subset of its neighbourhood
induces a star), so a violation forces girth ≥ 6 — and graphs of girth ≥ 5 are rare enough
that geng can enumerate all 17.7 million of them at n = 16 in minutes. Every gate in the
screener is a necessary condition of this kind; they are listed and justified in the wave-1 log.

### 4.2 The screener is trustworthy, and that was checked

The fast C screener may over-report but must never under-report. Its 22 invariants were
compared against the frozen exact library on 850 graphs at n = 8, 9, 10 — **zero
mismatches** (`python3 mine/tools/crosscheck_invariants.py 10 250`).

### 4.3 Class C — bound records

`mine/attacks/bound-*/`. The arm reconstructed the **known records** for R(4,6) at n = 35
and R(5,5) at n = 42 and had the frozen checker accept them (exit 0), then failed to beat
either. Circulant simulated annealing stayed far from feasible at n = 36 and n = 43; a SAT
encoding at n = 36 (630 vars, ~2.0M clauses) did not resolve within budget.

A concrete lesson fell out of it: the actual record graphs at n = 35 and n = 42 are
**irregular** (degrees 12–15 and 19–22), so the circulant ansatz was searching a strictly
smaller space than the one containing the record. That is now in `mine/memory/`.

---

## 5. Verification tiering — demonstrated on a positive control

There is no new result to promote, so the tiering was exercised on a case whose answer is
independently known: the search machinery's own rediscovery of a counterexample to WOWII
**conjecture 200**, which was already refuted in the literature. **This is not a discovery**,
and it is not in `mine/results/`.

| tier | what happened |
|---|---|
| T0 | C screener flagged the graph (`mine/tools/wowscan`) |
| T1 | frozen checker accepted it in exact arithmetic: `python3 mine/verify/checkers/check_wow2_200.py` → exit 0, `l_avg = 24/11`, `tree = 4`, no Hamiltonian path |
| T2 | a **fresh agent given only the statement and the graph6 string** — no access to our code or reasoning — wrote its own checker from scratch, cross-checked its decoder against `nauty-listg`, and independently confirmed all three conditions with identical values, additionally deriving the leaf argument by hand. `mine/attacks/t2-independent/` |
| T3 | Lean formalization: see `mine/attacks/t3-positive-control/` |

The T2 pass is the meaningful one: it is designed to catch a constructor and a checker
sharing a misreading, and it was run blind, exactly as specified.

---

## 6. Near-misses, and the specific obstacle in each

| target | how close | the obstacle |
|---|---|---|
| WOWII 19 | objective reached **0** (the inequality is tight — equality is achieved) at n = 11, 12 and 13, but never negative | the bound appears to be sharp rather than false; equality cases are common, violations absent |
| WOWII 141 | exhausted to n = 16 | none — this is a clean negative, and the girth argument makes larger n cheap; n = 17–18 is a few more core-hours |
| R(4,6) ≥ 36 | reproduced the n = 35 record; SA best objective 108 at n = 36 | the record graph is irregular, so the circulant ansatz cannot contain it; the full space is far beyond an hour of 4 cores |
| R(5,5) ≥ 43 | reproduced the n = 42 record | independently documented as having absorbed ~80 CPU-years; a 4-core hour is not a contribution |
| R(3,3,3,3) | **no compute spent** | verifier coverage gap: the frozen Ramsey checker handles only 2 colours and has no schema for a 4-colour edge partition. Not a search failure |

---

## 7. Calibration — which triage predictions were wrong

This is the part that prices run 2.

**1. "Machine-generated graph conjectures are the easiest ore" — half right, and the wrong
half mattered.** The rubric gave Graffiti/WOWII conjectures +1.5, and they *were* the only
Class A problems both cheap to check and small enough to witness. But the seam was already
mined at the sizes we could reach: the `GraphConjecture200.lean` docstring records an
exhaustive geng sweep over all 11,989,760 connected graphs on 4..10 vertices, done by
someone else. Our n ≤ 10 sweep largely reproduced known ground. **The rubric scored the
class, when the thing that matters is the frontier within the class.** Run 2 should score
"published exhaustive frontier vs. our reachable frontier", not "is this class enumerable".

**2. "Decades of attempted proofs with no attempted refutation is a strong positive
signal" — not tested, because the signal was unavailable.** Nothing in the harvested
metadata says whether a refutation search was ever run. We inferred it in exactly one case
(conjecture 200's docstring) and that inference immediately repriced the whole seam. Run 2
should make "has anyone run an exhaustive search, and to what n" a first-class corpus
field, populated deliberately.

**3. The unbounded-arithmetic penalty was correct and should be harsher.** Rubric v1 put
Brocard's problem and Euler bricks near the top because "a counterexample is a finite
object". They are searched past 10^9 and 10^17 respectively. v2's −3.0 penalty fixed the
ranking; the honest number is closer to "exclude entirely unless our frontier can exceed
the published one".

**4. Class C was mispriced upward by the corpus, and its own harvester said so first.**
Agent H4's realism ranking called every bound family out of reach of 4 cores in an hour
before any compute was spent, and it was right in every case. The lesson is that a
*harvester's* feasibility assessment is cheap and accurate and should gate the attack list
directly, rather than being written down and then partially ignored.

**5. The dominant process error was freezing the verifier before the harvest finished.**
Clusters H3 and H6 delivered 100 problems *after* `scripts/freeze.sh` ran — including four
Class A graph conjectures (Brouwer, total colouring, linear arboricity, thrackle) that
would have ranked in the attack set. They have no checker, so nothing found about them
could ship, and the same gap silently killed the R(3,3,3,3) arm. **Fix for run 2 is one
line: finish Phase 1 before starting Phase 3.** The freeze was not reopened, which is the
correct call and also the expensive one.

**6. A searcher that has not passed a positive control is not evidence.** The first
annealer seeded every restart from a random spanning path — which guarantees a Hamiltonian
path — and both positive controls are non-traceable graphs. It would have reported "flat"
forever on a family whose known counterexamples it could not represent. It was caught only
because known-refuted conjectures were deliberately kept in the target set as controls.
**Run 2 should make a positive control a hard precondition**: no "flat" result counts until
the same instrument has rediscovered a known counterexample of the same shape.

---

## 8. What the verifier could not check, and what that cost

- **Class B (144 problems): no Gröbner engine, no SDP.** Nothing in this class could be
  closed, so none was attacked. This is the single largest untouched slice of the corpus.
- **Multi-colour Ramsey**: 2 colours only (killed the R(3,3,3,3) arm).
- **Weak Schur numbers**: the frozen Schur checker implements the standard condition
  (x = y allowed) and does not certify weak Schur.
- **Witness size**: exhaustive invariants refuse above n = 22, path cover above n = 16.
- **Anything harvested after the freeze.**

---

## 9. Recommended next 40 problems

Generated by `python3 mine/tools/next40.py`, which re-ranks the corpus using the
calibration above — most importantly by demanding that our reachable frontier plausibly
*exceed* the published one, rather than merely that the problem be enumerable.
See `mine/corpus/next40.md`.

The three structural recommendations that matter more than the list:

1. **Finish the harvest, then freeze.** Write checkers for the whole triaged top-40, not
   for the subset that happened to exist on freeze day.
2. **Make "published exhaustive frontier" a corpus field**, and attack only where our
   frontier can exceed it. For the WOWII family that means starting at n = 11, not n = 3.
3. **Positive controls are mandatory.** Every heuristic searcher must rediscover a known
   counterexample before any of its negatives are reported.
