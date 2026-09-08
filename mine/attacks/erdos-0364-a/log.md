# erdos-0364-a — no consecutive triple of powerful numbers (Erdős–Mollin–Walsh)

Agent: A3. No frozen checker exists for this target — nothing here can ship as a result.
Frontier measurement only.

## Statement attacked
There is no n such that n, n+1, n+2 are all "powerful" (2-full: every prime factor
appears with exponent >= 2). (erdosproblems.com/364.)

## Search space / witness
A witness for "false" (conjecture refuted) is a single n with n, n+1, n+2 all powerful —
finite, exactly checkable via prime factorization. Powerful numbers up to N are sparse
(~2.17*sqrt(N) of them) and admit a closed generation: every powerful number equals
a^2*b^3 for some a,b >= 1 (standard characterization). `kfull_gen.py:powerful_upto(N)`
enumerates all (a,b) pairs with a^2*b^3 <= N directly (no sieve over all integers up to
N needed) — the total number of (a,b) pairs summed over b converges to O(sqrt(N)), so
this reaches far larger N than any per-integer sieve could in the same time.

## Published frontier
No explicit brute-force numeric search bound was found via WebSearch for this specific
question (unlike Erdős–Straus or Brocard, the literature here is structural, not a stated
"checked up to N"). What we did find (WebSearch, Beckon 2019, Rose-Hulman Undergrad Math
J., and Chan 2025 INTEGERS papers — WebFetch to arxiv.org/scholar.rose-hulman.edu was
blocked by the network egress proxy this session, so these rest on WebSearch snippets
only): if a triple exists, its smallest term must be ≡ 7, 27, or 35 (mod 36) (Beckon), and
under the abc conjecture only finitely many such triples can exist (conditional, not a
search bound). **No numeric published frontier to ratio against** — this is itself a
calibration finding: the problem was likely triaged partly on the assumption that a
"published frontier" number exists to beat, but for this target the strongest published
statements are structural/conditional, not computational.

## Our frontier
```
python3 mine/attacks/erdos-0364-a/run_kfull_checks.py 10000000000000
```
N = 10^13: 6,840,384 powerful numbers generated (20.06s), checked for any three
consecutive values in the set — **none found** (34.03s total incl. the set-membership
scan). Also ran at N=10^12 (9.09s total, none found).

## Ratio and verdict
No ratio computable (no published numeric frontier located). As a rough proxy: our
generation method is efficient enough (sparse enumeration, not a sieve) that pushing to
N=10^15-10^16 would likely be feasible within another minute or two of budget — we did
not, since the joint 45-minute budget across 6 targets was the binding constraint, and
since without a published number to compare against, additional digits of N add little
to the calibration story.

**Verdict**: negative (no triple found) — consistent with the conjecture.

## Wall time
~35s of compute (dominated by the N=10^13 run); most target time went to WebSearch
attempts to locate a numeric published bound that turned out not to exist.

## Recommended tractability for run 2
**2/10** — not because the search is hard (it's actually cheap, thanks to the sparse
a^2*b^3 enumeration) but because there is no stated frontier to beat and no sign the
answer is reachable by brute force at any N we could hit in an hour; the honest
next step for a real attempt is the structural/abc-conditional route (Beckon's residue
classes), not more search depth. Triage likely overweighted "witness_type: finite-object"
without registering that the search space, while enumerable, has no known density result
suggesting a witness is nearby.
