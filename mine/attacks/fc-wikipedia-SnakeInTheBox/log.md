# fc-wikipedia-SnakeInTheBox — attack log (agent A6)

**No frozen checker exists for this target. Nothing below can ship into
`mine/results/` this run.** Measured-frontier / run-2-recommendation log only.

Selection rationale for all five A6 targets is recorded in
`mine/attacks/fc-greensopenproblems-16-a/log.md` (this target was pinned directly by
the A6 brief, so no ranking argument was needed for it specifically).

## Statement (pinned from Lean)

Source: `mine/cache/formal-conjectures/FormalConjectures/Wikipedia/SnakeInTheBox.lean`
(namespace `SnakeInBox`).

```
def Hypercube (n : ℕ) : SimpleGraph (Finset (Fin n)) :=
  fromRel fun a b => (a ∆ b).card = 1

def IsSnakeInGraphOfLength {V} [DecidableEq V] (G : SimpleGraph V) (G' : Subgraph G)
    (k : ℕ) : Prop :=
  G'.IsInduced ∧ ∃ u v, ∃ (P : G.Walk u v), P.IsPath ∧ G' = P.toSubgraph ∧ P.length = k

noncomputable def LongestSnakeInGraph {V} [DecidableEq V] (G : SimpleGraph V) : ℕ :=
  sSup {k | ∃ (S : Subgraph G), IsSnakeInGraphOfLength G S k}

noncomputable def LongestSnakeInTheBox (n : ℕ) : ℕ := LongestSnakeInGraph <| Hypercube n
```

In plain terms: `Hypercube n` is the graph on subsets of `{0,...,n-1}` (equivalently,
length-`n` bit-strings) where two vertices are adjacent iff their symmetric difference
has exactly one element (the standard `n`-cube graph `Q_n`). A **snake** is an
*induced* path (`G'.IsInduced`: the only edges of `Q_n` between vertices of the path
are the path's own edges — no chords). `LongestSnakeInTheBox n` is the length (edge
count) of the longest such induced path in `Q_n`. Every symbol is defined above; `n` is
the only free parameter, fixed to `9` in the open theorem.

Open theorem in the same file:

```
theorem snake_dim_nine : LongestSnakeInTheBox 9 = answer(sorry) := by sorry
theorem snake_dim_nine_lower_bound : 190 ≤ LongestSnakeInTheBox 9 := by sorry
```

## Published frontier (source: the cited Lean file itself, which states these as
`category research solved` / `category research open` facts with the references
`Wikipedia: Snake-in-the-box`, `Wikipedia: Hypercube graph` at the top of the file)

- `n = 0..8`: exact values **known and solved**: `0, 1, 2, 4, 7, 13, 26, 50, 98`
  (`theorem snake_small_dimensions`, `map LongestSnakeInTheBox (range 9) = [0,1,2,4,7,13,26,50,98]`).
- `n = 9`: **open**. Best known lower bound is **190**
  (`theorem snake_dim_nine_lower_bound : 190 ≤ LongestSnakeInTheBox 9`). This matches
  the well-known published record for the 9-cube snake-in-the-box problem (search
  literature going back to Kautz 1958, with the current record established by later
  computer search — the Lean file cites Wikipedia's Snake-in-the-box article as the
  source for this number; not independently re-derived here, see below).
- General upper bound for all `n`, from the same file:
  `LongestSnakeInTheBox n ≤ 1 + 2^(n-1) * (6n) / (6n + (1/(6*sqrt6)) * sqrt(n))`
  — for `n=9` this evaluates to a bound in the low-to-mid hundreds (an asymptotic-style
  bound, not tight; not evaluated exactly here since no computation was run this
  session, see below).

## Computation actually run

**None.** As with the other four A6 targets, the coordinator's mid-run message
("close out the OEIS/Green's-list arm now ... do not start new searches") landed
before any brute-force, SAT, or local-search attempt on `Q_9` induced-path search was
started. No candidate snake beyond the cited literature value of 190 was constructed
or checked this session.

This is worth stating plainly because the A6 brief itself flagged this target as
**"a well-attacked problem where a 4-core hour is unlikely to move the record"** — the
honest expectation going in was that this arm's deliverable would be "measure the gap,
don't move it," and in the event the gap was not even measured computationally this
session; only the published frontier (already present verbatim in the cited Lean file)
is recorded here.

Wall time spent: ~5 minutes (reading and pinning the Lean statement). 0 minutes of
search compute.

## Verdict

**Open, unattacked, no improvement attempted.** No frozen checker exists for
`LongestSnakeInTheBox`/`IsSnakeInGraphOfLength` (nothing under `mine/verify/` covers
induced-path/snake predicates on hypercube graphs), so even a new record-length witness
for `n=9` could not ship as a `mine/results/` entry this run regardless of whether one
had been found.

## Run-2 recommendation

Follow the brief's own caution: this is one of the most heavily computer-searched
combinatorial records in recreational/combinatorial graph theory (decades of dedicated
snake-in-the-box search programs, some using symmetry reduction, SAT solvers, and
distributed search, specifically targeting `n=9` and `n=10`). A generic 4-core-hour
SAT/local-search attempt in run-2 is very unlikely to beat 190 and should be scoped as
**"measure how close a naive SAT/local-search encoding gets to 190 in a fixed budget,"
not "attempt to break the record."** Concrete next steps if run-2 spends time here:

1. Build a poly-time checker first: given an explicit vertex sequence in `{0,1}^9`,
   check (a) consecutive vertices differ in exactly one bit (Hamming distance 1), (b)
   all vertices distinct (path), (c) no non-consecutive pair of vertices is at Hamming
   distance 1 (induced — no chords). This is `O(k^2 * 9)` for a claimed snake of length
   `k`, cheap.
2. Encode "does an induced path of length `k` exist in `Q_9`" as SAT (one boolean per
   (position, vertex) pair, standard path + no-chord constraints) and binary-search `k`
   upward from a warm start at `k=190` using a known snake as a seed, purely to see how
   many additional steps a local search / SAT-guided perturbation can add within budget
   — log every improvement over 190 explicitly, per the brief's instruction, and stop
   honestly at the first flat plateau.
3. Do **not** spend budget re-deriving `n=0..8` (already closed, `by sorry` only
   because the Lean proof itself is `sorry`-stubbed, not because the values are in
   doubt) — that would not move the open frontier and the brief's 70/20/10 split
   (A+C/B/D) argues for spending on the open `n=9` case only.
