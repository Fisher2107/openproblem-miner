# erdos-0242-a — Erdős–Straus conjecture

Agent: A3 (Erdős finite-witness number theory, Class A/D). No frozen checker exists for
this target — nothing here can ship as a result. This is a frontier measurement only.

## Statement attacked
For every integer n > 2, do there exist distinct positive integers 1 <= x < y < z with
4/n = 1/x + 1/y + 1/z? (erdosproblems.com/242, Erdős–Straus conjecture.)

## Search space / what a witness looks like
A counterexample witness is a single n > 2 together with a *proof* that no (x,y,z) exists
— that is not finite-checkable directly. What *is* finite-checkable is confirmation for a
given n: a triple (x,y,z). If x is taken to be the smallest denominator, the complete
range for x is n/4 < x <= 3n/4 (forced by 1/x < 4/n and 1/x >= (4/n)/3). For each x, the
remaining fraction e/M = (4x-n)/(nx) must decompose as 1/y+1/z; this decomposition is
completely characterized by divisor pairs of M^2 (via (py-q)(pz-q)=q^2 after reducing
e/M=p/q). Two methods used here:
1. **Fast sufficient test** (`erdos_straus.py`): for each x, check only whether e | M
   directly (an exact single unit fraction), splitting the result via 1/w =
   1/(w+1)+1/(w(w+1)) into two more. This is a real, exactly-checked witness whenever it
   fires (verified against the closed form 4abc = n(bc+ac+ab)), but it never fires for
   n ≡ 1 (mod 4) — confirmed empirically: every unresolved n up to 5000 was ≡1 mod 4.
2. **Complete case analysis** (`erdos_straus_full.py`): for the residual n ≡ 1 mod 4, full
   divisor-pair decomposition (not just the e|M special case) over the *entire* x-range,
   giving a real completeness guarantee for those n (not just a heuristic).

## Published frontier
- N = 10^17: Sander / Elsholtz-style sieve with a "complete" set of covering congruences,
  arXiv:1406.6307 ("The Erdős-Straus conjecture: New modular equations and checking up to
  N=10^17"), building on Swett's earlier N=10^14. This is the credible, widely-cited
  figure (also given on Wikipedia's Erdős–Straus conjecture page, per WebSearch summary —
  WebFetch to en.wikipedia.org and arxiv.org was blocked by the network egress proxy in
  this session, so this citation rests on WebSearch snippets, not a primary-source fetch;
  flagged as a limitation, not asserted as independently verified).
- A 2025/2026 preprint (arXiv:2509.00128, "Further verification and empirical evidence for
  the Erdős-Straus conjecture") claims empirical bounds extended to roughly 10^18 and
  spot-checks near 10^17, 10^52, 10^131 — treated here as lower-confidence (single/few
  author preprint, not the same standing as the peer-reviewed 10^17 sieve), so 10^17 is
  used as the reported published frontier.

## Our frontier
Both methods combined give a **fully verified, complete-proof** frontier of **N = 10,000**
(every n in [3, 10000] has an exactly-checked witness triple):
- n ≢ 1 mod 4, up to 10,000: resolved instantly by the fast sufficient test (`erdos_straus.py`).
- n ≡ 1 mod 4, up to 10,000: resolved by the complete divisor-pair search
  (`erdos_straus_full.py`); took 52.16s for n=1 mod 4 up to 10,000 alone. Pushing to
  30,000 timed out at 90s wall (some individual n in that class have very large inner
  divisor-pair ranges) — this is the honest wall we hit, not a resource choice.

Repro:
```
python3 mine/attacks/erdos-0242-a/erdos_straus_full.py 10000   # n=1 mod 4, 52.16s
python3 -c "
from erdos_straus import find_witness
print([n for n in range(3,10001) if n%4!=1 and find_witness(n) is None])
"   # -> [] , all resolved
```

## Ratio and verdict
Ratio = 10^4 / 10^17 = **1e-13**. Our naive-but-complete search is thirteen orders of
magnitude short of the published frontier. The gap is entirely algorithmic: the
published record relies on a small set of covering congruences (Mordell/Yamamoto-style)
that resolve almost all n in O(1) per n, reserving brute force for a vanishing residual
set; we only implemented the crudest sufficient test plus a genuinely-complete but
polynomial(n)-cost fallback for the hard residue class, which is why our wall is at
10^4, not higher.

**Verdict**: negative (no counterexample), fully expected — matches published result.
Nothing shippable; recorded purely as a frontier/ratio datum.

## Wall time
~55s of actual compute (52s complete search + a few seconds fast-path), plus WebSearch
research time. Well within the 45-minute joint budget.

## Recommended tractability for run 2
**1/10** — this class needs the covering-congruence machinery of the actual published
searches to make any dent; naive per-n search is off by 13 orders of magnitude, and doing
better requires substantial number-theoretic engineering (a project in itself, not a spare
attack-agent hour), not "faster code."
