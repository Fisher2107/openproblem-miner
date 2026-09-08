# erdos-0647-a — Erdős divisor-sum race problem

Agent: A3. No frozen checker exists for this target — nothing here can ship as a result.
Frontier measurement only.

## Statement attacked
Let τ(n) count divisors of n. Is there n > 24 with max_{m<n}(m + τ(m)) <= n + 2 ? True for
n = 24. Erdős offered £25 for a counterexample n > 24 (erdosproblems.com/647).

## Search space / witness
A witness for "yes" is a single n > 24: check requires knowing max_{m<n}(m+τ(m)), i.e. the
running maximum of m+τ(m) over all m below n. Finite and exact given a divisor-count
sieve up to N — no floats, no approximation.

## Published frontier
- Per WebSearch summary: direct sieve search has excluded solutions up to **10^12**
  (uncertified / not kernel-checked).
- A more credible, narrower claim: arXiv:2608.17880 ("A Kernel-Checked Exclusion
  Certificate for Erdős Problem 647", Mian & Siddique, Aug 2026) reports a Lean4-checked
  (axiom closure {propext, Classical.choice, Quot.sound}, no native_decide) exclusion for
  24 < n <= **10^9**, replaying 6,685,922 factorization witnesses. The same source notes
  the 10^12-and-beyond figures (up to ~9.17×10^18) rely on `native_decide` in Lean, i.e.
  sit **outside the trusted proof kernel**. (WebFetch to arxiv.org was blocked by the
  network egress proxy this session; both figures rest on WebSearch snippets, not a
  primary-source fetch — flagged, not independently confirmed. Note also that this paper's
  own description — kernel-checked, Lean4, exact axiom closure — matches this repo's own
  T3 verification bar closely enough to be worth flagging as possibly itself a prior
  mining-system output; treat the 10^9 figure as the more conservative, better-attested
  one of the two published numbers regardless.)
- We use **10^9** (kernel-checked) as the apples-to-apples comparison, since our own
  search is likewise a from-scratch, no-shortcuts direct sieve — the fairer comparison
  is against another from-scratch sieve, not against the un-kernel-checked 10^12/10^18
  figures.

## Our frontier
`tau_race.py`: numpy divisor-count sieve (`tau[d::d] += 1` for d = 1..N) plus a running
max of m+τ(m), scanned for n > 24 with running_max <= n+2.
```
python3 mine/attacks/erdos-0647-a/tau_race.py 10000000
```
N = 10^7: sieve 17.62s, scan 1.85s, **0 hits**. (N=10^6 also tried: 1.65s, 0 hits;
N=10^8 timed out at 120s — the sieve's outer Python loop over d is O(N) regardless of
vectorized inner work, so it does not scale past ~10^7 in the time available.)

## Ratio and verdict
Ratio (vs. kernel-checked 10^9) = 10^7 / 10^9 = **0.01**. Ratio (vs. the uncertified 10^12
figure) = 10^7/10^12 = 1e-5. Either way, roughly 2-5 orders of magnitude short — closer
than the other five targets in this batch, because a plain divisor-count sieve is the
right algorithm here (no cleverer number theory shortcuts the published searches use that
we're missing), it's just a matter of raw throughput (our sieve's outer loop is
unvectorized Python, the actual bottleneck).

**Verdict**: negative (no n found) — matches published result.

## Wall time
~20s of compute total (well within budget); most of the problem's allotted time went to
disambiguating the two conflicting published bounds (kernel-checked vs. not).

## Recommended tractability for run 2
**4/10** — of the six targets this is the best-matched to "throw more of the same
compute at it": a C-optimized or fully-vectorized divisor sieve (no per-d Python loop)
could plausibly reach 10^9-10^10 in an hour on 4 cores, closing most of the gap to the
kernel-checked frontier. Still capped well below any hope of finding a genuine
counterexample if the published near-exhaustive search hasn't.
