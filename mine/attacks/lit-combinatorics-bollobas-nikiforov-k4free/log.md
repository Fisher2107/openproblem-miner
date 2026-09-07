# lit-combinatorics-bollobas-nikiforov-k4free

Agent: A5 (recent-literature finite-witness conjectures). **No frozen checker exists for
this target — the mine's verifier (`mine/verify/`) was built and hash-locked before this
entry was selected (`scripts/check-freeze.sh` confirmed VERIFIER INTACT, 40 files, at the
start of this run), and it will not be reopened. Nothing found here can ship as a
`mine/results/` entry in this run. This is exploratory frontier-measurement only.**

## Exact statement (every symbol defined)

Source: arXiv:2603.26379, "The Bollobás-Nikiforov Conjecture for Complete Multipartite
Graphs and Dense K4-Free Graphs" (submitted 2026-03-27, rev. 2026-04-10). Corpus entry:
`mine/corpus/raw/h6_literature.jsonl` id `lit-combinatorics-bollobas-nikiforov-k4free`.

For a graph G with adjacency eigenvalues λ_1(G) ≥ λ_2(G) ≥ ... and m edges, the general
Bollobás-Nikiforov conjecture asserts λ_1²+λ_2² ≤ 2(1-1/ω(G))·m for every G that is not a
complete graph, where ω(G) is the clique number. Specializing to K4-free graphs
(ω(G) ≤ 3, so the bound becomes 2·(2/3)·m = 4m/3):

**Conjecture**: for every K4-free graph G that is not a complete graph, λ_1(G)²+λ_2(G)² ≤ 4m/3.

## Definition correction found during the attack (calibration finding)

The corpus's `statement_nl` restates the exclusion clause as "every K4-free graph G with
G != K_3" — i.e. it excludes only K_3. **This is imprecise.** The general
Bollobás-Nikiforov conjecture (Bollobás & Nikiforov, 2002) excludes *every* complete
graph K_n, not only K_3 — this is because for G=K_n, λ_1=n-1, λ_2=-1, m=n(n-1)/2, ω=n,
giving LHS=(n-1)²+1 and RHS=(n-1)², a violation by exactly 1 for every n≥1 (a known,
intentional exclusion, not a real counterexample). Since K4-free graphs can only be
complete for n≤3 (K_1, K_2, K_3), the correct exclusion set for the K4-free specialization
is {K_1, K_2, K_3}, not {K_3} alone.

**This was caught empirically, not by re-reading the paper**: an initial run using the
corpus's literal "G != K_3" exclusion found a "violation" at n=2 — the single-edge graph
K_2 (g6 `A_`), with λ_1=1, λ_2=-1, m=1, giving LHS=2 > RHS=4/3, margin=+0.667. This is
exactly the well-known trivial complete-graph exception, not a real counterexample; it
disappears once K_1, K_2 are also excluded (matching the general conjecture's actual
convention). Recorded here per the mission's instruction that "if a checker rejects a
witness the witness is wrong" applies equally to the converse: an unexpected witness
passing a poorly-stated checker is a sign the *statement*, not the witness, is off — I
did not silently patch and move on, this is logged as an explicit imprecision found in the
corpus's `statement_nl` for this entry. All results below use the corrected exclusion
{K_1, K_2, K_3}.

## Open-status check

WebSearch (`arXiv 2603.26379 Bollobás-Nikiforov Conjecture Complete Multipartite Graphs
Dense K4-Free Graphs`) confirms: the paper proves the conjecture for all complete
multipartite graphs, and (via a stability argument) for K4-free graphs with m=Ω(n²) as
n→∞ — i.e. only dense K4-free graphs at scale are resolved. The corpus's own
`known_cases` field adds that triangle-free graphs (Lin-Ning-Wu) and regular graphs
(Zhang) are also settled, and flags "the general K4-free case with α(G) ≥ n/3" as the
authors' own stated remaining obstruction. A prior WebSearch by the H6 harvester
(recorded in the corpus entry, query `"Bollobás–Nikiforov conjecture counterexample
computer search small graphs"`) found no reported counterexample search. **Open-status
verdict**: genuinely open in general (small/sparse/non-regular/non-multipartite K4-free
graphs are not covered by the cited partial results), and no prior exhaustive small-graph
search was found — this is fresh territory for brute force.

## Method

Exhaustive generation of every K4-free graph (connected or not — the conjecture
quantifies over every such graph) on n vertices via `nauty-geng -k n` (nauty's native
K4-free filter), for n=2..10. Each graph6 string is decoded to an adjacency matrix by
hand (no networkx dependency in the hot path, for speed at n=10's 2.9M graphs), m is
computed exactly (integer edge count), and λ_1, λ_2 come from `numpy.linalg.eigvalsh`
(double precision). **This is a T0 float screen only** — no exact/interval arithmetic —
since nothing here ships as a result regardless of tier reached; a violation flag uses
tolerance 1e-6 (chosen because IEEE double precision resolves differences of this
magnitude with large margin for graphs this size; any genuine counterexample would show a
gap far above float noise, as the near-miss margins observed below — down at ~1e-14,
pure floating-point roundoff — demonstrate).

Repro:
```
python3 mine/attacks/lit-combinatorics-bollobas-nikiforov-k4free/check.py
```

## Frontier reached

**Every K4-free graph on 2 to 10 vertices, excluding K_1/K_2/K_3: 3,005,075 graphs, zero
violations.** Breakdown:
- n=2..9: 110,443 graphs, 4.0s.
- n=10 alone: 2,894,632 graphs, 187.9s.
- Total wall time: ~192s.

The closest-to-violating margin found at n=10 was `2.1e-14` (essentially exact equality,
floating-point noise) on graph6 string `I?zfF^mz_` (λ_1=6, λ_2≈0, m=27) — a graph
achieving equality in the bound, consistent with the conjecture being tight (not merely
true with slack) for extremal K4-free graphs, matching the paper's own report of
equality-achieving complete-multipartite examples.

## Wall time

Total agent time on this target, including the definition-correction detour: ~13 minutes.

## Verdict

**No counterexample found among all 3,005,075 K4-free graphs on ≤10 vertices** (after
correcting the corpus's incomplete exclusion clause to match the well-known convention).
Positive computational corroboration only — not a proof, and **cannot ship as a
mine/results/ entry** (no frozen checker for this problem; see header). n=10 is a
genuinely exhaustive frontier (not a sample), and the per-graph cost is cheap (eigenvalue
decomposition of small dense matrices), so n=11 (nauty-geng's K4-free count would likely
be tens of millions, unverified here) is the natural next step if this target is revisited
in run-2 — plausibly feasible within a similar few-minutes-per-vertex-count budget, though
growth in graph count could make n=11 take on the order of 30-60 minutes alone by
extrapolation from the n=9→n=10 growth factor (~28x), which was not attempted given the
45-minute cross-target budget for this wave.

## Negative-memory entry

See `mine/memory/negative-a5.jsonl`: exhaustive search up to n=10 found nothing, after
one initial false-positive that turned out to be a mis-stated exclusion clause rather
than a real witness — recorded as a distinct "definitional near-miss" ansatz outcome,
separate from the final "no violation" result.
