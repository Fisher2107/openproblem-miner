# lit-numbertheory-overpartition-congruence-mod7

Agent: A5. **No frozen checker exists for this target — the mine's verifier
(`mine/verify/`) was built and hash-locked before this entry was selected, and will not
be reopened. Nothing found here can ship as a `mine/results/` entry in this run. This is
exploratory frontier-measurement only.**

## Exact statement (every symbol defined)

Source: arXiv:2603.08510, "New Ramanujan-type congruences for overpartitions modulo 11
and 13" (Xuan Ling Wei, 2026-03-09). Corpus entry: `mine/corpus/raw/h6_literature.jsonl`
id `lit-numbertheory-overpartition-congruence-mod7`.

The overpartition function pbar(n) counts overpartitions of n (partitions of n in which
the first occurrence of a part may be overlined), with generating function
```
sum_{n>=0} pbar(n) q^n = prod_{k>=1} (1+q^k)/(1-q^k)
```
**Conjecture**: pbar(2^4 * (56n+k)) ≡ 0 (mod 7) for all n >= 0 and all k in {11, 43, 51}.

## Open-status check

WebSearch (`arXiv 2603.08510 Ramanujan-type congruences overpartitions modulo 11 13`)
confirms: the paper proves two congruences unconditionally (mod 11 and mod 13) and
explicitly *conjectures* analogous congruences for moduli 7, 17, 19, 23 — this mod-7
family (k in {11,43,51}) is one of those stated-open conjectures, matching the corpus's
framing exactly. Direct arXiv fetch is blocked at this environment's egress proxy
(confirms the harvest log's finding again); relied on the WebSearch snippet plus the
corpus entry's own extracted `notes` field, which independently states the same thing.
**Open-status verdict**: genuinely stated as conjectural in the source paper, not a
mislabel.

## Method

Exact integer arithmetic throughout (arbitrary-precision Python ints; pbar(m) is computed
exactly as an integer, then reduced mod 7 — no premature reduction, no floats anywhere).
`overpartition_coeffs(M)` computes the power-series coefficients of
`prod_{k=1}^{M} (1+q^k)/(1-q^k)` truncated at q^M via the standard two-pass-per-k
partition-DP recurrence: `(1+q^k)` is a finite polynomial multiply (top-down, in place,
knapsack order) and `1/(1-q^k)` is the unbounded-coin partition recurrence (ascending, in
place). Independently sanity-checked against the first 10 known values of OEIS A015128
(the overpartition sequence, 1,2,4,8,14,24,40,64,100,154 — a fixed reference sequence, not
something I derived from this same code) before trusting any congruence result; the code
halts with an explicit failure if that sanity check does not pass.

Repro:
```
python3 mine/attacks/lit-numbertheory-overpartition-congruence-mod7/check.py
```

## Frontier reached

M=15000 (i.e. pbar(0..15000) computed exactly). This covers n=0..16 for all three
residues k in {11,43,51} (49 total (n,k) pairs, since m=16(56n+k) exceeds 15000 once
n>=17). Wall time: 48.6s (dominated by the O(M^2) DP with big-int coefficients that grow
to ~130-digit numbers by m~15000).

## Wall time

Total agent time on this target: ~7 minutes (mostly the single 48.6s run plus write-up).

## Verdict

**No counterexample found** for n=0..16, k in {11,43,51} (49 checks, all pbar(m) ≡ 0 mod
7 exactly as conjectured). Positive computational corroboration only — not a proof, and
**cannot ship as a mine/results/ entry** (no frozen checker for this problem; see header).
The DP is O(M^2) with growing big integers, so pushing much past M~30000-50000 would need
either a smarter algorithm (this paper's own likely uses a modular-forms/eta-quotient
argument, not brute DP) or working mod 7 throughout with fixed-width machine integers
(would give a large constant-factor speedup and let M reach the hundred-thousands within
the same wall-clock budget — recommended for run-2 if this specific target is revisited).

## Negative-memory entry

See `mine/memory/negative-a5.jsonl`: brute-force search for a counterexample up to
M=15000 found nothing; not a flat/stuck arm, a genuine (partial) corroboration of an
already-correctly-labeled open conjecture.
