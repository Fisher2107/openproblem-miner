# fc-greensopenproblems-16-a — attack log (agent A6)

**No frozen checker exists for this target (nor for any A6 target — see "Read this
first" in the A6 brief). Nothing below can ship into `mine/results/` this run, no
matter what it finds.** This is a measured-frontier / run-2-recommendation log only.

## Selection rationale (applies to all five A6 targets)

A6 was asked to pick the five most attackable `fc-oeis-*` / `fc-greensopenproblems-*`
entries out of 336 such rows in `mine/corpus/problems.jsonl`, preferring statements
about a concrete finite computation or specific small constant over an asymptotic
claim, with `fc-greensopenproblems-16-a` and `fc-wikipedia-SnakeInTheBox` pinned by
the brief.

Ranked by corpus `tractability` (computed via `grep`/`python3 -c` over
`mine/corpus/problems.jsonl`, reproducible with:
`python3 -c "import json; [print(json.loads(l)['tractability'], json.loads(l)['id']) for l in open('mine/corpus/problems.jsonl') if json.loads(l)['id'].startswith(('fc-oeis-','fc-greensopenproblems-'))]" | sort -rn | head -40`),
the top of the pool is:

```
5.5  fc-greensopenproblems-31-f   class=C witness=none
5.5  fc-greensopenproblems-5-b    class=A witness=finite-object
5.5  fc-wikipedia-SnakeInTheBox   class=C witness=numeric-bound   <- pinned by brief
5.0  fc-greensopenproblems-16-a   class=A witness=finite-object   <- pinned by brief
5.0  fc-greensopenproblems-37-a   class=C witness=numeric-bound
5.0  fc-greensopenproblems-54     class=C witness=none
4.5  fc-greensopenproblems-19-a / 35-a / 35-b / 58
4.5  fc-oeis-113257-a/b, 116150, 53067, 70518, 71532-d, 86766-c
```

Chosen: **fc-greensopenproblems-16-a, fc-wikipedia-SnakeInTheBox** (pinned),
**fc-oeis-116150, fc-oeis-102847, fc-greensopenproblems-37-a**.

Rejected, with reasons (each read from its own Lean file in
`mine/cache/formal-conjectures/FormalConjectures/`):

- `fc-greensopenproblems-5-b` (tract. 5.5) — largest product-free subset of
  `SL2(F_p)`, quantified **over all primes p**; the open question is the asymptotic
  growth rate, not a value at one small `p`. A per-`p` brute force is possible in
  principle but the statement itself is asymptotic-in-`p`, which the brief says to
  deprioritize relative to a fixed small constant. Rejected for shape, not tractability.
- `fc-greensopenproblems-31-f` (tract. 5.5) — "for every finite abelian group `G`,
  does a Sidon subset of size `0.01 sqrt(|G|)` exist" — universally quantified over an
  infinite family of groups; refuting it means finding *some* bad group, which is an
  unbounded search over group order and structure, not a small finite computation.
  Asymptotic in character.
- `fc-greensopenproblems-54` (tract. 5.0) — statement is about Gaussian measure on
  compact convex sets in `R^n`; continuous/measure-theoretic, no finite witness or
  enumerable class in sight. Not finite-computation-shaped at all.
- `fc-oeis-113257-a/b`, `fc-oeis-53067`, `fc-oeis-70518`, `fc-oeis-86766-a/c`,
  `fc-oeis-107247` — all "next term" OEIS problems similar in shape to the two chosen
  OEIS targets, but each needs an extra, non-trivial definition pinned down first
  (a "base-exponent transform", "nonacci numbers", a concatenation convention with an
  admitted OEIS-side offset ambiguity, or — for 70518 — squarefreeness, which needs
  full factorization rather than a cheap primality test). Passed over in favor of the
  two OEIS targets whose recurrence is closed-form and already exactly reproduced by
  Lean `test`-category theorems in the cited file, i.e. lowest risk of mis-pinning the
  statement.
- `fc-oeis-71532-d`, `fc-oeis-115366` — both ask for a numerical constant in an
  asymptotic (`~ C log(n)^2`, a limiting ratio); not a specific small constant to
  compute exactly, and exact evaluation would need arbitrary-precision floor of an
  irrational power tower — excluded as asymptotic-shaped and float-risky.
- `fc-greensopenproblems-19-a/35-a/35-b/58/21-b`, `fc-oeis-102847`'s neighbors, etc. —
  lower-tractability or required more setup than the five chosen within the ~45 min
  total budget.

`fc-greensopenproblems-37-a` was picked over the remaining 4.5-tractability OEIS rows
specifically for *methodological* diversity: it is the one target in the batch that is
a genuine finite combinatorial-optimization problem (smallest AP-cover set), matching
the brief's SAT/ILP-first ladder, rather than a third "grind primality tests on a
recurrence" target.

## Statement (pinned from Lean)

Source: `mine/cache/formal-conjectures/FormalConjectures/GreensOpenProblems/16.lean`
(namespace `Green16`), lines as follows.

```
def SolutionFree (A : Finset ℕ) : Prop :=
  ∀ x ∈ A, ∀ y ∈ A, ∀ z ∈ A, ∀ w ∈ A,
    [x, y, z, w].Nodup → x + 3 * y ≠ 2 * z + 2 * w

noncomputable def f (N : ℕ) : ℕ :=
  sSup {k : ℕ | ∃ A : Finset ℕ, A ⊆ Icc 1 N ∧ SolutionFree A ∧ A.card = k}

theorem green_16 (N : ℕ) :
    ∃ A : Finset ℕ, A ⊆ Icc 1 N ∧ SolutionFree A ∧
      A.card = answer(sorry) ∧
      MaximalFor (fun B => B ⊆ Icc 1 N ∧ SolutionFree B) Finset.card A
```

In plain terms: `f(N)` is the size of the **largest** subset `A` of `{1,...,N}` such
that no 4 *pairwise-distinct* elements `x,y,z,w ∈ A` satisfy `x + 3y = 2z + 2w`. Every
symbol is defined in the excerpt above; `N` and the coefficients `(1,3,2,2)` are fixed
by the statement — there is no free parameter left unpinned. The open question is:
what is `f(N)` (equivalently, an explicit maximal witness `A`), for a given `N`.

Published bounds, same file (Ben Green's Open Problem 16, citing Ruzsa and
Schoen–Sisask):

- Lower: `f(N) ≫ N^{1/2}` (Ruzsa 1993).
- Upper: `f(N) ≪ N · exp(-c (log N)^{1/7})` for some `c > 0` (Schoen–Sisask 2016).
- Conjectured matching lower bound `f(N) ≫ N · exp(-c (log N)^{1/7})` — open.

No exact value of `f(N)` for any concrete `N` is recorded anywhere in the cited Lean
file or corpus row (`current_bounds: {lower: null, upper: null}` in
`mine/corpus/problems.jsonl`), so this is a genuinely open finite-computation target:
find `f(N)` and a maximal witness set for the smallest tractable `N`.

## Computation actually run

**None.** A6's ~45-minute wall budget was reallocated by the coordinator mid-run
(explicit instruction: "close out the OEIS/Green's-list arm now ... do not start new
searches") before a SAT/ILP encoding of `f(N)` could be built and run for this target.
No brute force, no SAT/ILP call, no local search was executed against `green_16` this
session. This is an honest zero, not a disguised negative result: the arm was not
started, so there is nothing to report as a failed ansatz beyond "not attempted."

Wall time spent on this target this session: ~10 minutes (reading/pinning the Lean
statement and cross-checking the corpus row); 0 minutes of actual search compute.

## Verdict

**Open, unattacked.** No frozen checker exists for `green_16` (nothing under
`mine/verify/` covers `SolutionFree`/`f`), so even a full brute-force result for small
`N` could not ship as a `mine/results/` entry this run regardless.

## Run-2 recommendation

This is the single best run-2 target among all five A6 picks: `witness_type:
finite-object`, `witness_check_cost: poly` (checking `SolutionFree A` for a candidate
`A` is a 4-nested-loop `O(|A|^4)` check, cheap for small `N`), and no exact value is
published for *any* `N`, so even `f(10)` would be new information relative to the
corpus. Concrete next steps for run-2:

1. Write a poly-time checker for `SolutionFree A` (trivial — the definition above is
   already exactly that), and a small-`N` exhaustive search (`N` up to ~15–20 by brute
   force over subsets, or better, by branch-and-bound / ILP for `N` up to ~60–100:
   maximize `|A|` subject to, for all distinct `x,y,z,w ∈ A`, `x+3y != 2z+2w`).
2. Encode as an ILP or a MaxSAT instance directly (`python-sat`/`z3`, both installed —
   see `mine/attacks/fc-greensopenproblems-37-a/log.md` for the toolchain check run
   this session) with one boolean variable per element of `{1,...,N}` and one clause
   per violating 4-tuple; this is the natural first rung of the method ladder in
   `MISSION.md` P4.
3. Before spending compute, build the required checker so a computed witness could at
   least be *tier-0/T1 screened* even though it cannot ship without a `mine/verify/`
   entry (which is frozen and out of scope for A6 to add).
