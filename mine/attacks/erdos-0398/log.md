# erdos-0398 — Brocard's problem

Agent: A3. No frozen checker exists for this target — nothing here can ship as a result.
Frontier measurement only.

## Statement attacked
Does n! + 1 = m^2 have integer solutions other than n = 4, 5, 7 (giving m = 5, 11, 71)?
(erdosproblems.com/398, Brocard–Ramanujan problem.)

## Search space / witness
Witness for "yes": a single n (with m = sqrt(n!+1)) outside {4,5,7}. Checkable exactly
with big-integer arithmetic: compute n! exactly, add 1, take integer square root, square
it back, compare. `brocard.py` does this incrementally (running factorial, gmpy2.isqrt).

## Published frontier
Berndt and Galway (2000) report no further solutions for n up to **10^9**, the
widely-cited computational record (per WebSearch summaries of arXiv:2004.09256 and
Wikipedia's "Brocard's problem" page — WebFetch to arxiv.org/wikipedia was blocked by the
network egress proxy this session, so this rests on secondary WebSearch snippets, not a
primary-source fetch). Dabrowski (1996) and Luca (2002) show finiteness of solutions is
implied by the abc conjecture — a conditional, not unconditional, result.

## Our frontier
Incremental exact factorial + gmpy2 integer square root, n = 1..60000:
```
python3 mine/attacks/erdos-0398/brocard.py 60000
```
Result: 103.44s wall, only the three known solutions (4,5), (5,11), (7,71) found, nothing
else. (n=20000 took 8.44s; n=60000 took 103.44s — cost grows faster than linearly, as
expected since multiplying the running factorial by n costs more as its digit count
grows; n! at n=60000 has roughly 260,000 digits.) Did not push further given the
observed superlinear scaling and the shared 45-minute budget across 6 targets.

## Ratio and verdict
Ratio = 6×10^4 / 10^9 = **6e-5**. Our naive incremental-factorial approach is roughly
4-5 orders of magnitude short of the published sieve. The published search almost
certainly does not compute full factorials at all past a certain point — it uses modular
/ quadratic-residue sieving (n!+1 must be a QR mod many small primes simultaneously) to
eliminate the overwhelming majority of n cheaply, reserving the (very rare) exact
big-integer check for survivors. We did not implement that filter; our bottleneck is pure
big-integer multiplication cost, which is the wrong bottleneck to be fighting.

**Verdict**: negative (no counterexample) — matches published result, unsurprising.

## Wall time
~112s of compute total (8.44s + 103.44s runs), well within budget.

## Recommended tractability for run 2
**2/10** — the arithmetic bottleneck (factorial growth) is fundamental to the naive
approach; matching even a small fraction of the published 10^9 frontier requires
implementing modular-sieve prefiltering (checking n!+1 mod small primes for
quadratic-residue status before ever forming the big integer), which is a real
algorithm-engineering task, not something an hour of brute force buys.
