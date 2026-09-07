# erdos-0366-c — consecutive pair of 3-full integers

Agent: A3. No frozen checker exists for this target — nothing here can ship as a result.
Frontier measurement only.

## Statement attacked
Are there any n such that n and n+1 are both 3-full ("cube-full": every prime factor
exponent >= 3)? (erdosproblems.com/366, the "weaker question" variant, also discussed as
Guy's problem B16.)

## Disambiguation note (see erdos-0366-a's log for full detail)
The two small pairs that keep surfacing in secondary sources — (8,9) and (12167,12168) —
were directly factored and are **not** valid witnesses here: 9 = 3^2 and 12168 =
2^3·3^2·13^2 both have a prime with exponent exactly 2, so neither is 3-full. Those pairs
answer a different (reverse-direction, 3-full followed by merely-2-full) question. As far
as we can determine, **no known example of two consecutive 3-full integers has ever been
published** — consistent with erdosproblems.com's framing of this as Erdős's still-open
"weaker question."

## Search space / witness
Cube-full numbers up to N generated directly via the standard k-full parametrization
n = a^3*b^4*c^5 (a,b,c >= 1) — sparse (~O(N^{1/3}) numbers), so this reaches far larger N
than a per-integer sieve. `kfull_gen.py:cubefull_upto(N)`; `run_kfull_checks.py` scans the
sorted set for adjacent integers.

## Published frontier
No explicit numeric search bound located for *this* direction. (The 10^22 bound
reportedly attached to OEIS A060355, per WebSearch, applies to the reverse-direction
pairs (8,9)/(12167,12168) — see disambiguation — not to this question. We deliberately do
not carry that number over as if it applied here.)

## Our frontier
```
python3 mine/attacks/erdos-0366-c/run_kfull_checks.py 1000000000000
```
N = 10^13: 90,619 cube-full numbers generated (0.29s) — scanned for any two consecutive
integers both in the set: **none found**. Total wall (incl. the co-generated powerful set
for the other two problems) 34.03s.

Pushed further, since cube-full generation alone (no need to also generate the much
denser powerful set) is cheap:
```
python3 -c "
from kfull_gen import cubefull_upto
Q = cubefull_upto(10**18)
Qset = set(Q.tolist())
print(any((int(v)+1) in Qset for v in Q))
"
```
N = 10^18: 4,480,253 cube-full numbers generated in 11.01s — **none found** to be
consecutive. This is our reported frontier for this problem: **N = 10^18**.

## Ratio and verdict
No ratio computable — no published numeric frontier located for this exact direction.

**Verdict**: negative (no consecutive 3-full pair found) up to N=10^13 — consistent with
this being a genuinely open question with (as far as located) zero known examples at any
scale, not just a "not yet searched past X" situation.

## Wall time
~1s of the problem's own compute (cube-full generation is very fast, since 3-full numbers
are far sparser than 2-full ones); shared research/code time with 0364-a/0366-a.

## Recommended tractability for run 2
**2/10** — the search itself is cheap and already reaches N=10^18 in ~11s (cube-full
numbers are sparse, ~O(N^{1/3})), so run 2 could push to 10^24+ for a few more seconds
of compute with no algorithmic work required. But there is no published frontier to beat,
and no structural reason (unlike 364-a's residue-class narrowing) to expect a witness at
any particular scale — so "search deeper" has no natural stopping point and no prior-art
target to calibrate against. Worth an hour of pure depth-pushing, not worth designing an
attack around.
