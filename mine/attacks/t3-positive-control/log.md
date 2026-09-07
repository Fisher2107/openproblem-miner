# T3 positive control — WOWII Conjecture 200

**This is not a new result.** Conjecture 200 of *Written on the Wall II* was already
refuted in the literature. Our search machinery independently rediscovered a
counterexample, and the point of this directory is to demonstrate, end to end, that the
run's T3 tier can produce a kernel-checked Lean witness for a case whose answer is
independently known. Nothing here should be described as a discovery.

The search that found the graph is not in this directory; this directory only certifies
the object. Graph, in graph6: `J^~~u?_C?O?` (11 vertices, 24 edges).

## Files

| file | what it is |
|---|---|
| `Conj200Control.lean` | the whole proof, self-contained, no imports (695 lines) |
| `build.txt` | exact commands + full output + timing, including `#print axioms` |
| `tree_number_crosscheck.py` | external (non-Lean) cross-check of the one unformalised step, gap M1 below |
| `log.md` | this file |

Reproduce:

```
export PATH="$HOME/.elan/bin:$PATH"
cd /home/user/openproblem-miner/mine/attacks/t3-positive-control
time lean Conj200Control.lean
```

52 s wall / 25 s user on this 4-core container. The build is warning-free; its entire
output is the seven `#print axioms` lines.

## What is proved

`conj200_counterexample` (line 669) is a conjunction of four claims about G:

1. **Connected** (`Connected`, `G_connected`, line 198) — every ordered pair of vertices is
   joined by an explicitly exhibited walk (via vertex 0).
2. **l-values** (`∀ v < 11, LVal v (lOf v)`, `l_all`, line 640) — `l(0..10) =
   3,3,3,3,3,2,2,2,1,1,1`, sum 24 (`sum_l`, line 656). Each `LVal v k` is proved in both
   directions: an explicit independent set of `k` neighbours of `v`, and an exhaustive
   `decide` over all 2048 vertex sets showing none that is independent and contained in
   `N(v)` is larger.
3. **tree(G) = ⌈1 + l_avg(G)⌉** (`∃ t, TreeNumber t ∧ t = 1 + (sumBelow lOf 11 + 11 - 1)/11`)
   — `TreeNumber 4` (`G_treeNumber`, line 385): the vertex set `{0,5,6,7}` (bitmask 225)
   induces a tree on 4 vertices, and an exhaustive `decide` over all 2048 vertex sets shows
   no larger one does. The right-hand side is *computed from the l-values proved in (2)*,
   not restated as a literal.
4. **No Hamiltonian path** (`no_ham_path`, line 572) — as instructed, not by brute force
   over permutations (39.9M, hopeless in the kernel) but via the endpoint lemma
   `deg_one_endpoint` (line 530): in any repetition-free list whose consecutive entries are
   adjacent, a vertex with at most one neighbour must be the first or the last entry,
   because an interior occurrence would give it two distinct neighbours. G has three
   vertices of degree 1 (8, 9, 10) and a path has two ends.

`#print axioms` on all of these returns `[propext, Quot.sound]` (and `[propext]` for
`G_connected`). **No `sorryAx`** (nothing is admitted) and **no `ofReduceBool`** (no
`native_decide`; every `decide` was replayed by the Lean kernel). `Classical.choice` does
not appear either.

Exhaustive `decide` searches actually run in the kernel:

* `treeChk_all` — all 2048 vertex sets, tree upper bound. 27.9 s of kernel type-checking.
* 11 × `lChk` — all 2048 vertex sets per vertex, l-value upper bounds. 1.0–2.3 s each.

## Non-vacuity checks (§8 of the file)

A "proof" of a vacuous statement is the failure mode this pipeline exists to catch, so the
file also proves things that would break if the encoding were wrong:

* `whole_graph_card : card 2047 = 11`, `whole_graph_edges : edgeCount 2047 = 24` — the
  bitmask machinery reproduces the vertex and edge counts computed independently outside
  Lean from the `nauty-listg` matrix.
* `cert_rejects_connected : disconCert 225 = false` and
  `cert_accepts_disconnected : disconCert 768 = true` — the disconnection certificate used
  in the tree upper bound is not vacuously true.
* `near_ham_nodup` / `near_ham_chain` — G *does* have a `Nodup`, `Chain' Adj` list through
  10 of its 11 vertices (`8-2-0-7-1-5-3-6-4-10`). So the path machinery is satisfiable by
  real paths of G; what `no_ham_path` rules out is the eleventh vertex, not a broken
  definition.
* `adj_matches_listg` — inside Lean, the bitmask table `rowMask` is re-checked against the
  adjacency matrix `listgRow` transcribed from `nauty-listg -a`. `build.txt` additionally
  re-diffs *both* literals against live `nauty-listg` output from outside Lean.

## Where my Lean might not match the informal statement

Read this section adversarially; it is the part that matters. Ordered by how much I think
each could bite.

### M1 — "tree" is encoded as *connected and |E| = |V| − 1*, not *connected and acyclic*

`IsInducedTree` (line 321) is `0 < card m ∧ ConnectedIn m ∧ edgeCount m + 1 = card m`. The
informal statement says a tree is "connected and acyclic". **The file never defines
"cycle" and never proves that the two characterisations agree.** That classical
finite-graph theorem is imported as an unformalised assumption inside the encoding of the
word "tree". This is the one place where the Lean is a paraphrase rather than a
transcription.

Direction by direction:

* *Witness side* (there is an induced tree on 4 vertices): `{0,5,6,7}` has 4 vertices and 3
  edges (`witness_card_edges`) and is connected (`conn225`), and one can read off `rowMask`
  that 5, 6, 7 are pairwise non-adjacent, so it is the star K(1,3) — visibly acyclic. Low
  risk.
* *Upper-bound side* (no induced tree on ≥ 5 vertices): I prove that no vertex set of ≥ 5
  vertices is simultaneously connected and of edge count |V| − 1. If the classical
  equivalence somehow failed, an induced tree with a different edge count could slip
  through. It cannot, classically — but the step is not machine-checked.

**External cross-check of exactly this gap** (T1-level, outside Lean):
`tree_number_crosscheck.py` recomputes tree(G) under the literal definition — acyclicity by
repeated leaf-stripping, which empties a graph iff it is a forest — and compares the two
families of induced trees.

```
$ python3 tree_number_crosscheck.py
tree(G), literal 'connected and acyclic' : 4
tree(G), 'connected and |E| = |V| - 1'   : 4
the two families of induced trees agree  : True (91 induced trees)
witness 225 = {0,5,6,7} is acyclic       : True
```

So for *this* graph the substitution provably changes nothing — but that check runs in
Python, not in the Lean kernel, so gap M1 stands as an unformalised step in the T3 witness.

Why I did not do it literally: proving "no cycle exists" needs cycle-as-list machinery plus
a pigeonhole argument for `Nodup` lists over an 11-element vertex set, or (for the upper
bound) an exhibited cycle in every connected ≥5-vertex induced subgraph. I judged that too
expensive for the time available and chose to flag it here instead of hiding it. If this
were a real result rather than a control, this gap should be closed before shipping.

### M2 — vertex sets are natural-number bitmasks below 2048

"For every induced subgraph" becomes "for every `m < 2048`". This is a bijection with the
subsets of `{0,…,10}`: `card` and `edgeCount` read only bits 0–10, so masks ≥ 2048 denote
nothing new, and `inMask_lt` (line 222) proves a mask below 2048 contains only vertices
< 11. Faithful, but it is an encoding a reader has to accept.

### M3 — connectivity is walk-reachability

`Reach` (line 157) and `ReachIn` (line 240) are inductively defined walk relations;
`ConnectedIn m` (line 245) says every pair of vertices of `m` is joined by a walk all of
whose vertices lie in `m`. The usual definition uses paths, but walks and paths reach
exactly the same vertices, so the relation is the same; and in the direction where I assert
connectivity (`G_connected`, `conn225`) I exhibit concrete walks, which is the strong
direction. `Reach` is written as a directed relation; G's adjacency is proved symmetric
(`adj_symm_B`, line 140), and `G_connected` does not rely on that anyway — it proves
`Reach u 0` and `Reach 0 v` separately.

### M4 — `IsHamPath` is *weaker* than "Hamiltonian path", deliberately

`IsHamPath l` (line 512) is `Nodup l ∧ Chain' Adj l ∧ (∀ v < 11, v ∈ l)`. It does **not**
require `l.length = 11` and does **not** require entries to be < 11. Every genuine
Hamiltonian path of G satisfies it, so `¬ ∃ l, IsHamPath l` implies "G has no Hamiltonian
path": the weakening is in the safe direction. (`Nodup` plus "every vertex occurs" already
forces each vertex to occur exactly once; and an entry ≥ 11 could not be adjacent to
anything, so it cannot occur in a chain of length ≥ 2.) A back-translator should check the
direction of this weakening rather than the wording.

### M5 — `Chain'`, `Nodup`, `firstOf`, `lastOf` are hand-rolled

No mathlib is available, so these are defined from scratch (lines 488–507). They are the
standard definitions, and §8 shows they are satisfiable by an actual 10-vertex path of G —
which is what would catch, say, a reversed adjacency in `Chain'`.

### M6 — the ceiling, and where `n = 11` and `sumL = 24` come from

`⌈1 + l_avg(G)⌉` is rendered over ℕ as `1 + (sumBelow lOf 11 + 11 - 1) / 11`, per the task
brief. Two elementary arithmetic facts are used but not formalised: `⌈a/b⌉ = (a+b-1)/b`
for truncating ℕ division with `b > 0`, and `⌈1 + x⌉ = 1 + ⌈x⌉` because 1 is an integer.
With `sumL = 24, n = 11` this is `1 + 34/11 = 1 + 3 = 4`. The literal `11` for the number
of vertices is part of the encoding (the vertex set is *defined* to be `{0,…,10}`); it is
cross-checked only by `whole_graph_card : card 2047 = 11`. `l_avg` itself is never defined
as a rational.

### M7 — the file proves facts about a graph, not "the conjecture is false"

The last step — "these four facts contradict WOWII Conjecture 200" — is a human reading of
the conjecture's English text, which is reproduced verbatim in the file header and was
taken from the task brief, not re-fetched from the source. If the published statement
carries side conditions (order bounds, minimum degree, a convention that K(1) is not
counted for tree(G), closed instead of open neighbourhoods in l(v)), the graph may not
refute *that* statement. Since Conjecture 200 is already known-refuted in the literature,
this control was never load-bearing for the mine's output; for a genuinely new result this
step would need a prior-art and statement-provenance check of its own.

## What fought me

* **No mathlib.** The Lean toolchain cache host is blocked by the egress proxy, so
  `lake exe cache get` cannot run and `Mathlib.Data.Real.Basic` was not among the 1293
  pre-built modules. Everything is written against the bare Lean 4 prelude: bounded
  quantifiers, `Nodup`, `Chain'`, `firstOf`/`lastOf`, and the whole finite-set layer are
  hand-rolled. This is also why vertex sets are bitmasks: no `Finset`, no `Fintype`.
* **Missing core tactics.** `by_contra` is not available without mathlib (replaced by
  `Nat.lt_or_ge` + `cases`), and neither are `fin_cases`/`interval_cases` (replaced by
  `match u, hu with` over the eleven literals).
* **Kernel reduction speed was the binding constraint, and the fix was structural.**
  Functions defined by the equation compiler's structural recursion reduce through
  `brecOn`, which builds a `below` tuple at each step; a 2048-iteration fold with an
  11-step inner loop took ~25 s wall that way. The same loop written directly as `Nat.rec`
  took ~1 s — about a 25× difference. Every loop in the file is therefore a `Nat.rec` fold
  (`allBelow`, `anyBelow`, `sumBelow`, `orBelow`), reflected into Prop-level bounded
  quantifiers by `allBelow_iff` / `anyBelow_iff`. This also sidesteps
  `Nat.decidableBallLT`, whose well-founded definition I did not want to make the kernel
  chew on.
* **Ordering the checks mattered.** `treeChk` (line 332) tests `card ≤ 4` first, then the
  edge count, and only then computes a connected component and its closure. `Bool.or`
  short-circuits under kernel whnf, so the expensive part runs for the 229 vertex sets that
  survive the first two tests instead of all 2048. Without that ordering the tree bound was
  minutes, not 28 s.
* `decide +kernel` is used for the twelve heavy searches so the work is done once (kernel)
  instead of twice (elaborator, then kernel).
* `ReachIn.trans` initially failed termination checking because `m` was bound inside the
  `∀`; fixing `m` as a parameter before the match made the structural recursion go through.

## Honest scope statement

Parts 1–4 are all proved, with no `sorry` and no `native_decide`. The single substantive
gap between the English statement and the Lean statement is **M1** (tree = connected +
|E| = |V| − 1 rather than connected + acyclic); **M6** contributes two lines of
unformalised ceiling arithmetic; **M7** is the usual gap between "facts about an object"
and "refutation of a published claim". Everything else in the list above is an encoding
choice that I believe is faithful, but they are listed so that the back-translation agent
can check them rather than take my word for it.
