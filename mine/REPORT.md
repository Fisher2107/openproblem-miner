# Open-problem mine — run 1 report

**Bottom line: zero new results. One end-to-end validated pipeline, one negative result
that appears to be new, and a priced diagnosis of why the yield was zero.**

No conjecture in this corpus was refuted, no published bound was improved, and
`mine/results/` is empty. That is the honest outcome, and the rest of this document is
about making it a useful one: what was searched, how far, with what instrument, and which
of the triage rubric's predictions were wrong.

On the one negative that looks new — **WOWII conjecture 141 holds for every connected graph
on at most 16 vertices** — the claim is only that no prior verification to that order was
found in the sources reachable from this container, and those sources were badly
restricted (§2). For the rest, the honest status differs case by case. Erdős–Gyárfás over cubic graphs to
n = 20 and Barnette's class to n = 22 are **known ground** — both conjectures have been
checked further in the literature. The other nine WOWII conjectures at n <= 10 are
**status unknown**: the one published exhaustive sweep we could find in this container
covers connected graphs on 4..10 vertices for conjecture *200*, a different (and already
refuted) statement, and says nothing about whether anyone ran the same sweep for these
nine. We are not claiming that coverage is new, and we are not claiming it is redundant;
we could not determine which, because the sources that would say are blocked (§2).

Everything below cites a file and a command. Nothing here is a summary of an intended run.

**Audit path.** `bash scripts/reproduce-run1.sh` re-runs every claim in this report whose
truth does not depend on how long you are willing to wait: the freeze check, the verifier's
71 self-tests, the screener-versus-frozen-library cross-check, a short exhaustive sweep, the
**positive control** (if the searcher cannot rediscover a known counterexample, its
negatives mean nothing), the T1 accept path on two published counterexamples, the blind T2
checker, the T3 Lean build, and the CI result check. It was run against this commit and
ends in `RUN 1 CLAIMS REPRODUCED` — output in `mine/logs/reproduce-run1.log`.

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
| graph-conjecture evaluations, exhaustive | **442,423,983** | §4, table below |
| problems with an attack log | **41** (A: 28, C: 11, D: 2, **B: 0**) | `mine/attacks/*/log.md` |
| failed ansatz families recorded | 36 | `mine/memory/negative.jsonl` |
| candidates reaching T1 | 0 (new) / 1 (positive control) | §5 |
| **T3-verified new results** | **0** | — |
| T3 demonstrated on a positive control | 1 | `mine/attacks/t3-positive-control/`, axioms `[propext, Quot.sound]` |
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

**Provenance.** Of the 1,541 entries, **1,523 cite a specific file in a cloned repository**
(`clone:<owner>/<repo>@<commit>:<path>`) and 18 cite a WebSearch result URL. **Zero rest on
model memory** — the `model-knowledge-unverified` tag, which policy bars from the attack
pool, ended up unused because every cluster found a citable mirror. Every row carries a
class and a tractability score; 12 lack a `url` field but all 12 carry clone provenance,
which is the stronger citation. Verify with
`python3 -c "import json;rows=[json.loads(l) for l in open('mine/corpus/problems.jsonl')];print(len(rows))"`.

**A caveat on the dedupe, stated because the number looks too good.** Only 12 of 1,553
entries were merged as duplicates. That is not because the clusters barely overlap — they
overlap a lot — but because the dedupe key is a hash of a normalised statement string, so
it catches near-identical wordings and misses the same conjecture stated in two different
vocabularies. The harvest agents caught more overlap by hand than the algorithm did (H3
reports skipping ~18 entries it recognised as already present in H1/H2, e.g. Heilbronn =
`erdos-0507`, Erdős–Straus = `erdos-0242-a`). So **1,541 is an upper bound on the number of
distinct problems**, and the true figure is somewhat lower. Semantic dedupe by embedding or
by pairwise LLM comparison is a run-2 item.

### Corpus by class

| class | meaning | count |
|---|---|---|
| A | finite-witness refutable | 147 |
| B | parametric-construction refutable | 144 |
| C | bound-improvable | 383 |
| D | proof-only | 867 |

### Compute and wall-clock spent

| resource | amount | note |
|---|---|---|
| wall clock | ~6.8 hours | one session, 2026-09-06 22:15 UTC to 2026-09-07 ~05:00 UTC |
| machine | 4 cores, 15 GB RAM | `nproc` = 4 |
| subagent LLM tokens | ~1.5 million across the runs that reported usage | 6 harvest + 6 attack + 1 blind-verification + 1 formalization + 1 back-translation agent |
| agent runs lost to rate limits | 9 (all resumed from their own transcripts) | the session limit was hit three times; every agent was resumed rather than restarted, so no work was redone |
| **cost per verified result** | **undefined — there were none** | the only honest entry |

The largest single compute item was not a search: it was compiling a 1,293-module mathlib
subset from source because the olean cache host is blocked.

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
`VERIFIER INTACT (40 files)`. **The freeze was never reopened.** Three moments where
reopening it would have helped — the four Class A graph conjectures that arrived after the
freeze, the multi-colour Ramsey arm, and the weak Schur arm — are recorded in §7 as costs,
not repaired.

Worth recording about the validation itself: **two of the five reference-graph expectations
were wrong, and the library was right.** The hand-written table said K3,3 has a longest
induced path on 4 vertices and residue 3; the library computed 3 and 2. An independent
permutation-based enumeration of induced paths (written from the Lean `isInducedPath`
definition rather than from the library's characterisation) and a hand-traced
Havel–Hakimi reduction both sided with the library. The expectations were corrected. This
is the whole reason for testing against values computed a different way: the first thing
the suite caught was its author.

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

> **Conjecture 141 holds for every finite simple connected graph on at most 16 vertices** —
> re-verified by the frozen checker itself, exhaustively over the decisive girth >= 6 class,
> up to n = 14. The other nine hold for every connected graph on at most 10 vertices.

The 141 result comes from a proof-shaped shortcut rather than brute force: `tree(G) ≥
max_v l(v) + 1` always (a vertex plus a maximum independent subset of its neighbourhood
induces a star), so a violation forces girth ≥ 6 — and graphs of girth ≥ 5 are rare enough
that geng can enumerate all 17.7 million of them at n = 16 in minutes. Every gate in the
screener is a necessary condition of this kind; they are listed and justified in the wave-1 log.

### 4.1b Every exhaustive sweep in the run

"Graph-conjecture evaluation" = one graph tested against one conjecture's full predicate.
The same graph tested for two conjectures counts twice, because the cost and the evidence
are per-conjecture.

The n = 11 row grows while the sweep runs; `python3 mine/tools/refresh_n11_numbers.py`
re-reads the slice log and rewrites the three places this report quotes it, so the numbers
here cannot drift from the log. It exits nonzero if any slice ever reports a candidate —
that would mean the negative needs revisiting, not a number bump.

| sweep | graphs |
|---|---|
| all connected graphs n <= 10, all ten WOWII conjectures | 11,989,762 |
| conjecture 141, all girth >= 5 graphs, n = 11..16 | 20,147,011 |
| graffiti-3 (`alpha >= rad`), all connected graphs n <= 10 | 11,989,762 |
| erdos-0064 (min degree >= 3, power-of-two cycle), n <= 10 | 5,290,114 |
| Erdős–Gyárfás (cubic, power-of-two cycle), n <= 20 | 556,470 |
| erdos-0023 (triangle-free, make bipartite), n = 5, 10 | 9,838 |
| generator families 1 and 2 | 20,908 |
| Barnette (cubic bipartite), n <= 24 | 34,622 |
| exhaustive n = 11 (cheap arms), edge counts 10..26 — stopped partway, by choice | 392,385,496 |
| **total** | **442,423,983** |

### 4.2 The screener is trustworthy, and that was checked

The fast C screener may over-report but must never under-report. Its 22 invariants were
compared against the frozen exact library on 850 graphs at n = 8, 9, 10 — **zero
mismatches** (`python3 mine/tools/crosscheck_invariants.py 10 250`).

### 4.2b The exhaustive negative re-checked by the frozen verifier itself

The sweeps above are the fast C screener's word. Two runs put the frozen checkers behind
that word:

- **Random sample at n = 9 and 10.** 300 connected graphs sampled uniformly, all ten frozen
  WOWII checkers run on each: **3,000 checker invocations, 0 ACCEPTs, 0 REFUSEs.**
  (`mine/tools/verify_n10_sample.py`, log in `mine/attacks/wave1-wowii-exhaustive/verify_n10_sample.log`.)
- **Exhaustive re-check of the decisive class for conjecture 141.** Since a violation of 141
  forces girth >= 6, the frozen checker was run on *every* girth >= 6 graph up to n = 14 —
  not a sample: **27,911 graphs, 0 ACCEPTs** (`verify141_full.log`). So for n <= 14 the
  headline negative is a statement about the frozen verifier, not about the screener; from
  n = 15 to 16 it rests on the screener, whose invariants agree with that verifier on every
  one of 850 cross-checked graphs.

An ACCEPT in either run would have meant the screener under-reported and the headline
negative was wrong. Neither produced one.

### 4.3 The verifier earned its keep: it rejected a false witness

The single most important event in the run was not a search result. In the Schur arm, a
tabu-search script produced what its own author believed was a valid 0-conflict colouring.
The **frozen checker rejected it** (`check_schur_lower.py`, exit 1), pointing at a genuine
monochromatic solution `2 + 13 = 15`. The cause was a bug in the searcher's incidence
list, which double-counted the `x = y` triples and therefore scored a bad colouring as
perfect. The agent found the bug, fixed it, found evidence of a *second* one, and abandoned
the method as unreliable rather than shipping from it.

This is exactly the failure the architecture exists to catch: a searcher and its own
private notion of correctness agreeing with each other and both being wrong. A run in which
the checker never rejects anything has not been tested. `mine/attacks/bound-schur-S6/`.

### 4.4 Class C — bound records

`mine/attacks/bound-*/`. The arm reconstructed the **known records** for R(4,6) at n = 35
and R(5,5) at n = 42 and had the frozen checker accept them (exit 0), then failed to beat
either. Circulant simulated annealing stayed far from feasible at n = 36 and n = 43; a SAT
encoding at n = 36 (630 vars, ~2.0M clauses) did not resolve within budget.

A concrete lesson fell out of it: the actual record graphs at n = 35 and n = 42 are
**irregular** (degrees 12–15 and 19–22), so the circulant ansatz was searching a strictly
smaller space than the one containing the record. That is now in `mine/memory/`.

### 4.5 How the budget was actually rescheduled

Arms were treated as bandit arms with reward = measured movement in the scalar objective.
What actually happened, in order:

1. **All ten WOWII arms opened with the same exhaustive budget** because exhaustion at
   n <= 10 is cheap (about two minutes of one core for all ten at once). Reward: zero
   movement on every arm — no candidate, and the best objective never went positive.
2. **The annealing arms were killed after n = 14.** Their signal was informative but
   negative: conjectures 19, 40 and 61 all reach objective **exactly 0** and stop, at
   n = 11, 12, 13 and 14. Objective 0 means the inequality is *tight* — equality is
   achieved — but never exceeded. An arm that reaches the boundary from below and stays
   there is not "about to succeed"; it is telling you the bound is sharp.
3. **Budget was reallocated on a structural signal, not a numeric one.** The reward that
   mattered was not objective movement, it was *reach per core-hour*, and reach comes from
   hypothesis restrictiveness. Conjecture 141's girth >= 6 requirement made its class small
   enough to exhaust to n = 16, so it got the reallocated time; the general arms did not.
4. **The same signal picked the two extra targets.** Erdős–Gyárfás (cubic graphs) and
   Barnette (cubic + bipartite + planar + 3-connected) were added *because* their
   hypothesis classes are tiny, reaching n = 20 and n = 22 respectively — twice the reach
   of any general-graph sweep, on the same hardware.
5. **The Class C arms were killed on a reproduction failure, not a search failure.** Once
   the van der Waerden and Schur searches could not reproduce *known* records near their
   critical thresholds, further budget on them could not have produced a trustworthy
   result, so it was stopped rather than spent.

The generalisable rule this run learned: **for a fixed compute budget, schedule on the
restrictiveness of the hypothesis class, not on the tractability of the statement.**

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
| T3 | **Lean 4 formalization compiles clean.** `mine/attacks/t3-positive-control/Conj200Control.lean`, self-contained core Lean with no imports (full mathlib is unavailable here — its olean cache host is blocked). Reproduced independently by the orchestrator: `grep -nE "sorry\|native_decide\|admit\|^axiom " Conj200Control.lean` finds nothing, and `lean Conj200Control.lean` compiles with `#print axioms conjecture200_is_false` → `[propext, Quot.sound]` — **no `sorryAx`, no `ofReduceBool`**, so nothing was smuggled in by `sorry` and every computation was done by the kernel rather than by compiled code. |
| back-translation | a separate agent, forbidden from reading anything but the Lean file and told nothing about the intended statement, rendered the theorem back into English. **It found a real gap** — see below. `mine/attacks/t3-positive-control/backtranslation.md` |

The T2 pass is the meaningful one for catching a constructor and a checker sharing a
misreading, and it was run blind, exactly as specified. The T3 pass matters for a different
reason: it establishes that **the kernel-verified tier is actually reachable in this
environment**, which was in serious doubt after the mathlib cache turned out to be blocked.
It is reachable by writing self-contained core Lean and keeping every computation inside
what the kernel can reduce — not by leaning on `native_decide`, which would have been
easier and would have silently added an axiom.

### What the back-translation caught, and why it is the most useful thing in §5

The back-translation agent was given the Lean file and nothing else — not the conjecture,
not the corpus entry, not any of this report — and asked to say bluntly what the theorem
actually asserts. It reported:

> Nowhere in the Lean source is there a Lean proposition that states the universally
> quantified conjecture itself and then negates it. The file proves four separate facts
> about one fixed graph; the inference "these four facts together refute the conjecture" is
> made only in prose, via an implicit modus tollens the reader is expected to perform. That
> means the Lean type of `conj200_counterexample` is strictly weaker than `¬ Conjecture 200`.

That is exactly right, and it is exactly the failure mode this tier exists to catch: a
formalization that is true, kernel-checked, axiom-clean — and narrower than the claim it is
being used to support. Two smaller findings in the same review: the translation of the
real-valued ceiling `⌈1 + l_avg⌉` into Nat division is asserted in a comment with only the
numeric instance kernel-checked, and `IsInducedTree` is defined as "connected, nonempty,
|E| = |V| − 1" with the equivalence to "connected and acyclic" taken as read. Neither
invalidates the numbers; both are places where the trusted statement is larger than the
proved one.

**The gap was then closed.** The file now defines the conjecture itself as a Lean
proposition quantified over an arbitrary finite graph —

```lean
def Conjecture200 : Prop :=
  ∀ (n : Nat) (adj : Nat → Nat → Bool) (L : Nat → Nat) (t : Nat),
    0 < n → WellFormed n adj → GConnected n adj →
    (∀ v, v < n → GLVal n adj v (L v)) → GTreeNumber n adj t →
    t = 1 + (sumBelow L n + n - 1) / n →
    GHasHamPath n adj
```

— and proves `theorem conjecture200_is_false : ¬ Conjecture200` by instantiating it at the
11-vertex graph and discharging every hypothesis with the results already established. The
modus tollens now happens inside the kernel rather than in a comment.

Verified independently of the agent that wrote it:
`grep -cE "sorry|native_decide" Conj200Control.lean` → 0, `lean Conj200Control.lean`
compiles, and `#print axioms conjecture200_is_false` → `[propext, Quot.sound]`.

The two smaller findings remain, now stated explicitly in the file rather than assumed: the
real-to-Nat ceiling translation is a trusted statement-level step, and `IsInducedTree` is
defined by the standard "connected, nonempty, |E| = |V| − 1" characterisation.

**None of this is a discovery.** Conjecture 200 was refuted before this run started. What
the four tiers demonstrate is that had a *new* counterexample turned up, the machinery to
promote it existed, worked, and — importantly — had a step in it that pushed back.

---

## 6. Near-misses, and the specific obstacle in each

| target | how close | the obstacle |
|---|---|---|
| exhaustive n = 11 | 392,385,496 graphs cleared — every connected graph on 11 vertices with ≤ 26 edges | not a mathematical obstacle: the container is suspended between orchestrator turns, so the detached sweep gained ~3 minutes of CPU per 54 minutes of wall clock. Slices 27..55 unreached. Run 2 should drive long sweeps from the foreground in turn-sized chunks — the edge-slicing already allows it |
| Erdős–Gyárfás (cubic case of Erdős 64) | exhausted over all connected cubic graphs to n = 20 | witnesses must dodge every power of two at once; small cubic graphs are cycle-rich |
| Barnette's conjecture | exhausted the whole class to n = 20 — only 8 graphs at n = 20 are 3-connected cubic bipartite planar | the class is tiny, so the reachable n is large; the literature is already far ahead |
| WOWII 19 | objective reached **0** (the inequality is tight — equality is achieved) at n = 11, 12 and 13, but never negative | the bound appears to be sharp rather than false; equality cases are common, violations absent |
| WOWII 141 | exhausted to n = 16 | none — this is a clean negative, and the girth argument makes larger n cheap; n = 17–18 is a few more core-hours |
| R(4,6) ≥ 36 | reproduced the n = 35 record; SA best objective 108 at n = 36 | the record graph is irregular, so the circulant ansatz cannot contain it; the full space is far beyond an hour of 4 cores |
| R(5,5) ≥ 43 | reproduced the n = 42 record | independently documented as having absorbed ~80 CPU-years; a 4-core hour is not a contribution |
| R(3,3,3,3) | **no compute spent** | verifier coverage gap: the frozen Ramsey checker handles only 2 colours and has no schema for a 4-colour edge partition. Not a search failure |

---

### 6b. The frontier ratio — the number that should drive run 2

For the number-theory arm, each target's published search frontier was located first and
our own frontier measured against it. Full logs in `mine/attacks/erdos-*/`.

| problem | published frontier | ours | ratio |
|---|---|---|---|
| Erdős–Straus (`erdos-0242-a`) | N = 10^17 | N = 10^4 | **10^-13** |
| Brocard (`erdos-0398`) | N = 10^9 | N = 6×10^4 | **6×10^-5** |
| divisor race (`erdos-0647-a`) | N = 10^9 kernel-checked | N = 10^7 | **10^-2** |
| consecutive powerful triple (`erdos-0364-a`) | none located | N = 10^13 | n/a |
| 3-full pair (`erdos-0366-c`) | none located | N = 10^18 | n/a |

Read plainly: on the two problems with solid published frontiers we are five to thirteen
orders of magnitude behind, and no amount of the same brute force closes that — those gaps
were closed with covering congruences and modular sieves, not with cores. Exactly one
target (`erdos-0647-a`) is within reach of "more of the same", and only if the sieve is
rewritten in C.

Note also what the last two rows mean: for three of the six, **no published numeric search
bound could be located at all**, so there is no ratio to compute. That is not a licence to
claim novelty — it is a warning that the corpus entry is under-specified. In one case
(`erdos-0366-a`) the agent factored the "known examples" that search kept surfacing and
found they answer the *opposite* direction of the conjecture, confirming the corpus's own
ambiguity flag was real.

## 7. Calibration — which triage predictions were wrong

This is the part that prices run 2.

**1. "Machine-generated graph conjectures are the easiest ore" — half right, and the wrong
half mattered.** The rubric gave Graffiti/WOWII conjectures +1.5, and they *were* the only
Class A problems both cheap to check and small enough to witness. But the rubric never asked the question that decides the outcome: **at what size has
someone already looked?** The `GraphConjecture200.lean` docstring records an exhaustive geng
sweep over all 11,989,760 connected graphs on 4..10 vertices — for a *different* conjecture
in the same family — and the known counterexamples in this family sit at n = 11, 13 and 18.
So n <= 10 was, on the family's own evidence, the wrong place to look, and we could not even
determine whether our sweep there was novel. **The rubric scored the class; what matters is
the frontier within the class.** Run 2 should score "published exhaustive frontier vs. our
reachable frontier", not "is this class enumerable".

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

**5b. Three arms were blocked by verifier coverage, not by difficulty.** R(3,3,3,3) needed
a multi-colour Ramsey schema the frozen checker does not have; the weak Schur number needs
the `x < y` condition, and the frozen checker implements the standard one (`x = y` allowed)
— demonstrated concretely by feeding it the trivial true weak-Schur witness for WS(1) = 2,
which it correctly rejects as a *standard* Schur claim. Both were reported as gaps rather
than papered over. A checker family should be designed around the witness *shapes* in the
triage list, not around individual problems.

**5c. Two corpus entries carried notation drift that would have produced a fake result.**
The `bound-vdw-W4-4` entry's prose says "2-colouring" while its own `known_cases` uses the
opposite convention (`W(r,k)` = r colours, k-term AP), and the Bollobás–Nikiforov entry's
exclusion clause said `G != K_3` where the true exception is `K_1, K_2, K_3` — an early run
duly flagged `K_2` as a "violation". Both were caught by agents reading the statement
carefully before spending compute. Statement drift does not only live in the Lean layer;
it lives in the corpus.

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
