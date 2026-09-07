# Attack log — wiki-brouwers-conjecture (agent A4)

## Statement attacked
Brouwer's conjecture: for a graph `G` with `m` edges and Laplacian eigenvalues
`mu_1 >= mu_2 >= ... >= mu_n`, the sum of the `t` largest satisfies
`sum_{i=1}^t mu_i <= m + C(t+1,2)` for every `t` in `1..n`.

**No frozen checker exists for this problem** (`mine/verify/checkers/` has no
`check_brouwer*`, confirmed via `bash scripts/check-freeze.sh` — freeze intact,
40 files, no drift). Nothing found here can ship as a result in this run,
even if a violation had turned up.

## Published verification frontier
- Exhaustive computer check by Brouwer himself: **all graphs with n<=11
  vertices**, no violation found.
  Source: [Brouwer's conjecture — Wikipedia](https://en.wikipedia.org/wiki/Brouwer%27s_conjecture)
  (per WebSearch snapshot; direct wikipedia/arxiv fetch is egress-blocked in
  this sandbox, so this is a secondhand citation, not a fetched primary
  source — flagged accordingly).
- Proved unconditionally for: trees, unicyclic graphs, split graphs, and for
  `t=1,2,3` over all graphs. (Same source.)
- **Major finding, changes the whole calculus for this target**: a 2026
  preprint claims a full proof. Kothari & Tudose, "On Brouwer's Laplacian
  conjecture", arXiv:2606.12197 (submitted 2026-06-10), establish an
  **equivalence between Brouwer's conjecture (all graphs, all t) and the
  Grone–Merris–Bai theorem** (Laplacian spectrum majorized by the conjugate
  degree sequence — proved by Bai, *Trans. AMS* 2011, a long-accepted
  result), and close the remaining gap via split graphs. Multiple
  follow-up preprints from the same window build on it as an established
  result: arXiv:2607.03388 ("The Equality Cases For the Laplacian
  Conjecture of Brouwer" / "On Full Brouwer's Laplacian Conjecture"),
  arXiv:2607.08452 ("Proofs of two conjectures on generalizations of
  Brouwer's Laplacian conjecture"), arXiv:2607.17293 ("Characterizing the
  equality case in Brouwer's inequality for Laplacian eigenvalues").
  As of this run (2026-09), the June 2026 preprint is ~3 months old and I
  found no evidence of journal acceptance or a retraction/refutation —
  it should be treated as **strong but not yet fully vetted** prior art,
  not a certainty. Per repo vocabulary rules, this stays a **candidate**
  proof, not a "proved" fact, until it clears peer review — but it is
  reason enough not to spend serious compute hunting a counterexample here.

## Consequence for this attack
Given a plausible full proof already exists and cites a 15-year-old
accepted majorization theorem as its engine, burning compute on an
exhaustive re-sweep past n=11 is a poor use of budget. I did a **light,
non-exhaustive push** instead: confirm the encoding is right on known
tight cases, then random-sample well past the published n=11 frontier
with float screening + exact sympy recheck on anything that looks close,
purely as a sanity check, not a real search.

## Class enumerated and why
- Exhaustive re-verification of n<=11 was **not attempted** — it's already
  done in the literature (Brouwer's own computation) and re-doing it would
  burn the whole session's compute on a solved problem (n=11 already means
  >10^9 unlabeled graphs; regenerating that from scratch was out of budget
  and out of scope).
- Instead: connected graphs at n=12,14,...,40 (even n only, arbitrary
  choice for coverage spread), sampled via `networkx.gnp_random_graph` at
  p in {0.1,0.2,0.3,0.5,0.7,0.9} (40 samples/n) plus deterministic
  structured extremal-flavoured families per n: star, complete graph,
  Turán graph, a 6-regular random graph (even n), a barbell graph. These
  families were chosen because known tight/near-tight cases for Brouwer's
  conjecture cluster around stars (t=1) and complete/dense regular graphs
  (t=n-1), so they're the most informative places to probe near the
  boundary rather than uniformly at random.
- 568 connected graphs checked total, spanning n=12..40.

## Frontier reached
n=12..40 (sparse, non-exhaustive, random+structured sample), on top of the
published exhaustive n<=11 and the (unverified-by-me) 2026 full-proof
claim.

## Method / exact arithmetic
- `brouwer_screen.py`: T0 float screen via `numpy.linalg.eigvalsh` on the
  dense Laplacian (built by hand, not `networkx.laplacian_matrix`, since
  `scipy` is not installed in this sandbox and that call requires it).
  Flags any `t` where `bound - running_sum < 1e-6`.
  T1 exact recheck via `sympy.Matrix.eigenvals()` (exact algebraic
  eigenvalues, no floats) on any flagged graph, re-testing the same
  inequality with `sp.N(margin) < 1e-9` only as a final numeric readout
  of an otherwise-exact quantity.
  Sanity-tested on `K5` (t=4 equality, tight) and `star_graph(6)` (t=1
  equality, tight) — both correctly identified as **boundary**, not
  violations; `petersen_graph()` and `path_graph(5)` return no
  flags at all, confirming the screen doesn't over-fire.
- `brouwer_sample.py`: driver for the n=12..40 sample described above.

## Wall time
- Encoding + sanity checks: ~3 min.
- Sample sweep (568 graphs, n=12..40): 4.3s (`brouwer_sample.py` run,
  timestamped 2026-09-07 04:07:19–04:07:24 UTC in this environment).
- Literature search (WebSearch, several queries): ~10 min.

## Verdict
**No violation found.** Every flagged case in the sample sweep was a known
extremal family (star at t=1, complete/dense regular graph at t=n-1)
sitting exactly at the boundary (`margin` sympy-exact 0), not a violation.
This is consistent with — not new evidence against — the conjecture, and
also consistent with the 2026 proof claim. **Not exhaustive**: this is a
sparse random probe past n=11, not a sweep; a genuine counterexample at
n=12+ of low degree/measure-zero structure could still be missed by
random sampling. Given the strength of the prior-art proof claim, I do
not recommend spending run-2 budget on further exhaustive search here.

**No frozen checker exists for this problem, so nothing found here — even
a genuine violation — could ship as a result in this run.**

## Run-2 recommendation
**Tractability: 1/10.** The honest bottleneck is not compute, it's that
the conjecture now has a credible 2026 proof reducing it to an
already-published theorem (Grone–Merris–Bai). Run 2's best use of a slot
here is a **literature-verification task**, not a search: get a domain
expert or formal-methods pass to check the Kothari–Tudose argument (or
watch for its journal acceptance / a refutation), and only reopen this as
a search target if that proof is refuted.
