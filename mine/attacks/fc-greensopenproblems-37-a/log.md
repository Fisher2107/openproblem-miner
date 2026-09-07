# fc-greensopenproblems-37-a — attack log (agent A6)

**No frozen checker exists for this target. Nothing below can ship into
`mine/results/` this run.** Measured-frontier / run-2-recommendation log only.

Selection rationale for all five A6 targets is recorded in
`mine/attacks/fc-greensopenproblems-16-a/log.md`.

## Statement (pinned from Lean)

Source: `mine/cache/formal-conjectures/FormalConjectures/GreensOpenProblems/37.lean`
(namespace `Green37`; Ben Green's Open Problem 37).

```
def IsAPCover (A : Set ℕ) (N k : ℕ) : Prop :=
  ∀ d, 1 ≤ d ∧ d ≤ N → Set.ContainsAP A k d

noncomputable def m (N k : ℕ) : ℕ :=
  sInf { m | ∃ A : Finset ℕ, A.card = m ∧ IsAPCover (A : Set ℕ) N k }

theorem green_37 (N k : ℕ) :
    IsLeast { m | ∃ A : Finset ℕ, A.card = m ∧ IsAPCover (A : Set ℕ) N k } (answer(sorry))
```

In plain terms: for fixed `N` and `k`, `m(N,k)` is the size of the **smallest** subset
`A ⊆ ℕ` such that for **every** common difference `d ∈ {1,...,N}`, `A` contains an
arithmetic progression of length `k` and difference `d` (i.e. `k` terms
`a, a+d, a+2d, ..., a+(k-1)d`, all in `A`, for some starting point `a`). `IsAPCover` and
`m` are fully defined above (`Set.ContainsAP` is a mathlib primitive: `A` contains an
AP of length `k` and common difference `d` iff `∃ a, ∀ i < k, a + i*d ∈ A`). **`N` and
`k` are both free parameters of the theorem** — the Lean statement does not fix them,
so "the" open question is really a two-parameter family `m(N,k)`; the corpus row
(`fc-greensopenproblems-37-a`) targets the base case `green_37` itself (existence of a
minimizer + its value), not one of the four asymptotic-in-`N` variants also in the same
file (`green_37_asymptotic`, `_theta`, `_bigO`, `_littleO`, all explicitly asymptotic
and rejected from this batch for that reason — see the selection log).

To attack this at all requires **fixing** small concrete `(N,k)` pairs, e.g. `(N,k) =
(2,2), (3,2), (2,3), (3,3), (4,2), ...` and computing `m(N,k)` exactly for each — this
was flagged as the necessary first step but not carried out (see below).

## Published frontier

The Lean file's docstring gives no numeric values for any `(N,k)` — it states the
existence question and four asymptotic-behavior questions (as `N → ∞` for fixed `k`),
all `research open`. `mine/corpus/problems.jsonl`'s row for this id has
`current_bounds: {lower: null, upper: null}` and `known_cases: null`. No published
exact value of `m(N,k)` for any concrete `(N,k)` was located this session (no
WebSearch was run for this target before the coordinator's stop instruction arrived;
this is recorded as a gap, not papered over).

## Computation actually run

**None against the actual objective `m(N,k)`.** The only work done this session was a
toolchain check, run to confirm the method ladder's second rung (SAT/ILP) is available
before the coordinator's "stop, write up" instruction landed:

```
$ python3 -c "import pysat; print('pysat ok')"
pysat ok
$ which z3 && z3 --version
/usr/bin/z3
Z3 version 4.8.12 - 64 bit
$ python3 -c "import z3; print(z3.get_version_string())"
ModuleNotFoundError: No module named 'z3'   # (initial state)
$ pip3 install --user z3-solver
Successfully installed z3-solver-5.1.0.0
$ python3 -c "import z3; print(z3.get_version_string())"
5.1.0
```

So: `python-sat` was already available; the `z3` CLI binary was already available but
its Python bindings were not, and were installed successfully this session
(`z3-solver` 5.1.0 via pip). Both are now usable for a SAT/SMT encoding of "does a
size-`m` AP-cover of `{1,...,N}` for difference range `1..N`, AP length `k`, exist" as
a direct boolean/SMT search, per the brief's method ladder (brute-force smallest cases
first, then SAT/ILP). **No such encoding was written or run.**

Total wall time charged: ~5 minutes (toolchain check + statement pinning). 0 minutes
of search compute against `m(N,k)` itself.

## Verdict

**Open, unattacked.** No frozen checker exists for `IsAPCover`/`m`, so this cannot ship
regardless of what a future computation finds.

## Run-2 recommendation

This is a legitimate finite optimization problem and the toolchain is confirmed ready
(`python-sat` and `z3` (CLI + Python bindings) both working as of this session). First
concrete steps for run-2:

1. Fix `k=2` first (the smallest nontrivial AP length — a 2-term "AP of difference d"
   is just any pair `{a, a+d}`) and small `N` (say `N=2..10`); this reduces to a clean
   combinatorial covering problem: choose the smallest `A ⊆ {1,...,M}` (bound `M`
   generously, e.g. `M = N*(k-1)+something`, then verify no smaller `M` helps) such
   that for every `d ≤ N` some pair at distance `d` lies in `A`. This already has a
   textbook flavor (a "difference-covering" / "perfect difference set"-adjacent
   problem) worth a literature check before spending SAT budget — there may be a closed
   form for `k=2` that turns this into a `class B`-style symbolic result instead of a
   pure search.
2. For `k ≥ 3`, encode directly as SAT: variables `x_i` for `i` in a bounded candidate
   range, one clause per `d ∈ {1,...,N}` requiring `∃ a: x_a ∧ x_{a+d} ∧ ... ∧
   x_{a+(k-1)d}` (introduce auxiliary "AP-present" variables per `(a,d)` to keep clause
   count linear), minimize `sum x_i` via a MaxSAT solver (`python-sat`'s RC2) or an ILP
   via `z3`'s `Optimize()`.
3. Do not attempt the four asymptotic variants (`green_37_asymptotic/_theta/_bigO/_littleO`)
   under this attack framing — they ask for a *formula* in `N` (a `class B`/analytic
   target), not a finite witness, and were explicitly excluded from this batch's
   selection for that reason.
