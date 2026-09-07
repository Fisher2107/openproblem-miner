# Back-translation of `Conj200Control.lean`

Produced by reading only `Conj200Control.lean` (plus running `lean` on it and `nauty-listg`
on the graph6 string quoted in its header comment; no other repository file was read).

## 0. Sanity checks performed

- `lean Conj200Control.lean` type-checks with no errors. `#print axioms` on every listed
  theorem reports only `[propext]` or `[propext, Quot.sound]` — no `sorry`, no
  `Classical.choice`, and no `native_decide` (which would have added an
  `Lean.ofReduceBool`/"trust the compiler" axiom). Every numeric claim in the file is
  closed by the kernel's own reduction (`decide` / `decide +kernel`), not by a compiled
  oracle.
- `echo "J^~~u?_C?O?" | nauty-listg -a` reproduces exactly the 11×11 0/1 matrix quoted in
  the file's header comment, confirming the graph6 string names the same graph the file
  hand-encodes as `rowMask`.

## 1. The main theorem, in plain English

The theorem is `conj200_counterexample` (restated with all numbers spelled out, and
proved identically, as `conj200_counterexample_explicit`). It asserts, of one specific,
fixed, 11-vertex graph G (defined by the `rowMask` table, see §3):

> G is connected; for every vertex v of G, the independence number of the subgraph of G
> induced on the open neighbourhood of v equals a specific listed value `lOf v`; the
> largest number of vertices carried by any induced subgraph of G that is a tree equals 4,
> and 4 is exactly the value you get by summing those eleven independence numbers, dividing
> by 11, adding 1, and rounding up; and yet G has no Hamiltonian path (no listing of all 11
> vertices, each used once, with consecutive entries adjacent in G).

Nowhere in the Lean source is there a Lean proposition that states the universally
quantified conjecture itself ("for every connected graph G, if tree(G) = ⌈1+l_avg(G)⌉ then
G has a Hamiltonian path") and then negates it. The file proves four separate facts about
one fixed graph; the inference "these four facts together refute the conjecture" is made
only in prose (the file's comments), via an implicit modus tollens the reader is expected
to perform. That's a legitimate way to falsify a universal claim, but it means the Lean
type of `conj200_counterexample` is strictly weaker than "¬ Conjecture 200" — it is the raw
material for that conclusion, not the conclusion itself, encoded as a term.

## 2. Every definition, unfolded

- **`rowMask u`** — a hard-coded lookup table (`List.getD`, default `0`) giving, for each
  `u < 11`, a bitmask whose bit `v` records adjacency `u~v`. This *is* the graph: an
  11-vertex labelled graph with a fixed, literal adjacency table, not a general graph
  parameter.
- **`Adj u v`** — `u < 11 ∧ v < 11 ∧ (rowMask u).testBit v = true`. Adjacency, with both
  endpoints explicitly required to be below 11 (redundant with `rowMask`'s `getD 0`
  default for out-of-range `u`, but stated again here).
- **`adj_matches_listg`** (kernel-checked) ties `rowMask`'s bit encoding to the literal
  0/1 matrix `nauty-listg -a` printed for `J^~~u?_C?O?`; I independently reran that
  command and it matches.
- **`adj_irrefl_B`, `adj_symm_B`, `adj_symm`** — G has no self-loops and is symmetric
  (undirected), each checked by `decide`. Note: these facts are proved as *separate*
  lemmas about the fixed `rowMask` table; "G is simple" is not itself a conjunct inside
  `conj200_counterexample`'s stated type. It's true, and it's proved, but you have to go
  read `adj_irrefl_B`/`adj_symm_B` to see it — the main theorem's type doesn't say it.
- **`Reach` / `Connected`** — `Reach u v` is "there is a walk (finite sequence of edges,
  repeats allowed) from u to v". `Connected := ∀ u v < 11, Reach u v`. This is the
  ordinary, weakest notion of graph connectivity — nothing stronger (2-connectivity,
  Hamiltonian-connectivity, etc.) is implied or claimed.
- **`InMask m v`** — vertex `v` belongs to the "vertex set" encoded by bitmask `m`
  (`m.testBit v`). A vertex set is any `m : Nat`; by convention `m < 2048 = 2^11` is
  supposed to hold everywhere a vertex set is meant, so that no bit ≥ 11 is set — but this
  bound is *not* baked into `InMask` itself, only supplied as a side hypothesis at each
  call site (see the "subtly off" section below for what depends on this).
- **`card m`** — popcount of `m` restricted to bit-positions `0..10` (`sumBelow` over 11).
  Number of vertices in the coded set. Correctly ignores garbage in higher bits if `m`
  happens to be ≥ 2048 (it just never looks there).
- **`edgeCount m`** — for `v` from 0 to 10, sums over `u < v` whether `u,v ∈ m` and
  `u~v`. Because the inner bound is `u < v` (strict), each edge of the induced subgraph is
  counted exactly once, not twice and not zero times. This is the number of edges of the
  subgraph of G induced on the vertex set `m`.
- **`ReachIn m u v`** — a walk from `u` to `v` that never leaves `m`: every constructor
  (`refl`, `step`) demands the *current* vertex be `< 11` and `InMask m`, so by induction
  every vertex touched by the walk, including both endpoints, is forced to lie in `m`.
  Correct formalization of "reachable inside the induced subgraph."
- **`ConnectedIn m`** — `∀ u v, InMask m u → InMask m v → ReachIn m u v`. Notice this
  quantifies over *all* naturals `u, v`, not `u, v < 11` — unlike `SubNbhd`/`Indep` below,
  which do carry an explicit `< 11` bound in their own definition. If `m` had a bit set at
  some position ≥ 11 (only possible if the `m < 2048` convention were violated), then
  `ConnectedIn m` would in fact become *false* (that vertex could never reach even itself,
  since `ReachIn.refl` demands `u < 11`), so the definition is self-consistent, but it
  relies on an external `m < 2048` hypothesis at every use site to mean what you'd expect;
  it does not enforce that bound on its own the way the other set-predicates do. Vacuously
  true for `m = 0` (empty vertex set) — no `u` satisfies `InMask 0 u`, so an "empty
  induced subgraph" counts as (vacuously) connected under this definition. That's caught
  downstream by `IsInducedTree` requiring `0 < card m`.
- **`disconCert m` / `not_connectedIn_of_cert`** — a decidable, checkable *certificate*
  that `ConnectedIn m` fails (exhibits a bit-mask "component" `C` closed under neighbours
  inside `m`, containing some vertex of `m`, but missing some other vertex of `m`). Sound
  (proved: cert true ⇒ ¬ConnectedIn), used only to justify the exhaustive tree-number
  search; the certificate mechanism was itself checked non-vacuous (`cert_rejects_connected`,
  `cert_accepts_disconnected`).
- **`IsInducedTree m := 0 < card m ∧ ConnectedIn m ∧ edgeCount m + 1 = card m`.** This
  *defines* "tree" as "nonempty, connected, and has exactly (vertices − 1) edges." The
  file's own comment admits explicitly that the classical equivalence between this and
  "connected and acyclic" is **not proved anywhere in the file** — it's an unformalized,
  if standard, fact baked silently into what the word "tree" means here. If you were
  distrustful of that equivalence in general, this file gives you no proof of it, only an
  assertion in a comment.
- **`TreeNumber k`** — `(∃ m < 2048, IsInducedTree m ∧ card m = k) ∧ (∀ m < 2048,
  IsInducedTree m → card m ≤ k)`. This pins `k` down to *exactly* the true maximum order
  of an induced tree (existence of a witness attaining `k`, and a hard upper bound), not
  merely "some tree has ≥ k vertices" or "k is *an* upper bound." Good match to "largest
  order... that is a tree."
- **`SubNbhd v m := ∀ u < 11, InMask m u → Adj v u`** — every vertex of `m` is a neighbour
  of `v` (`m ⊆ N(v)`). Because `Adj v v` is always false (irreflexivity), if `v ∈ m` held,
  `SubNbhd v m` would be unsatisfiable — so "`v ∉ m`" is enforced *implicitly*, through
  irreflexivity, rather than stated. Also note `SubNbhd`/`Indep`/`LVal` never require
  `v < 11` themselves; only the outer use (`l_all : ∀ v < 11, LVal v (lOf v)`) restricts
  `v` to actual vertices of G. `LVal` for an out-of-range `v ≥ 11` is not obviously
  meaningless, but it is never exercised that way in this file.
- **`Indep m`** — pairwise non-adjacency among the (in-range) members of `m`. Standard
  independent-set predicate; vacuously true for `m` of size 0 or 1.
- **`LVal v k`** — `(∃ m < 2048, SubNbhd v m ∧ Indep m ∧ card m = k) ∧ (∀ such m, card m ≤
  k)`. Exactly "the independence number of G restricted to N(v) equals k" (max, not merely
  "some independent subset of size k exists"), matching the "open neighbourhood" claim,
  since independence is checked in G but only ever applied to subsets of `N(v)`, and
  induced subgraphs preserve non-adjacency, so "independent in G" and "independent in
  G[N(v)]" coincide for subsets of N(v).
- **`Chain' R l` / `Nodup l`** — custom (not `List.Nodup`/`List.Chain'` from anywhere
  imported — this file has zero imports) reimplementations of "consecutive entries related
  by R" and "no repeats." They behave as expected.
- **`IsHamPath l := Nodup l ∧ Chain' Adj l ∧ (∀ v < 11, v ∈ l)`.** An ordinary
  **Hamiltonian path** (open walk visiting every vertex exactly once, consecutive entries
  adjacent) — *not* a Hamiltonian cycle; there is no requirement that the first and last
  entries of `l` be adjacent. The theorem `no_ham_path` therefore rules out Hamiltonian
  paths specifically (which is what the conjecture, per the header comment, is about); it
  says nothing directly about Hamiltonian cycles (though the nonexistence of a path
  obviously implies the nonexistence of a cycle too, that's not what's stated).
- **`lOf v`** — another hard-coded lookup table, `[3,3,3,3,3,2,2,2,1,1,1]`, asserted (via
  `l_all`/`l_0`..`l_10`) to equal the true `LVal` for each vertex.
- The closed-form `t = 1 + (sumBelow lOf 11 + 11 - 1) / 11` (Nat truncating division) is
  claimed by a comment to equal `⌈1 + l_avg(G)⌉` for the real/rational average
  `l_avg(G) = (Σ l(v))/11`. This identity (`⌈a/b⌉ = (a+b-1)/b` for naturals, and `⌈1+x⌉ =
  1+⌈x⌉`) is **standard but not itself proved as a Lean lemma anywhere in this file** —
  only the single numeric instance (`4 = 1 + (24+10)/11`) is checked by `decide`. The
  file never constructs a real or rational number at all; "l_avg" as a mathematical object
  is purely a comment-level gloss on a hard-coded natural-number formula.

## 3. The object being asserted about

An 11-vertex, 24-edge, simple, connected, undirected, labelled graph (vertices 0–10),
hard-coded via `rowMask`, cross-checked against `nauty-listg -a` output for graph6 string
`J^~~u?_C?O?`. Degree sequence: deg(0)=deg(1)=6, deg(2)=deg(3)=deg(4)=7, deg(5)=deg(6)=5,
deg(7)=2, deg(8)=deg(9)=deg(10)=1 (sum 48 = 2·24, consistent with `whole_graph_edges = 24`
and `whole_graph_card = 11`).

Structure (worked out from the bitmasks, not stated by the file):
- {2,3,4} form a triangle; each of 2,3,4 is adjacent to all of {0,1,5,6}.
- {0,1} are **false twins**: identical neighbourhood `{2,3,4,5,6,7}`, but 0 and 1 are *not*
  adjacent to each other.
- {5,6} are also false twins: identical neighbourhood `{0,1,2,3,4}`, not adjacent to each
  other.
- Between the two twin pairs, {0,1} and {5,6} form a complete bipartite `K_{2,2}`.
- Vertex 7 is a degree-2 pendant-ish vertex attached only to {0,1}.
- Vertices 8, 9, 10 are **leaves** (degree 1), pendant off 2, 3, 4 respectively.

The three leaves 8, 9, 10 are exactly what `no_ham_path` exploits: each has a unique
neighbour, so by `deg_one_endpoint` each can only occur as the first or last entry of any
path — but a path has only two "end slots," and there are three such vertices, a direct
contradiction (the classical "≥3 leaves ⇒ no Hamiltonian path" argument). This is a clean,
correct, minimal argument, not a computational brute force over the exponentially many
vertex orderings.

## 4. What this theorem does NOT say

- It does **not** state the general conjecture as a Lean proposition and refute it in
  Lean; it proves four separate facts about one fixed graph, and the "this refutes
  Conjecture 200" step lives only in comments/documentation, not in any theorem's type.
- It does **not** compute or verify, in Lean, that its closed-form natural-number formula
  `1 + (Σl(v) + 10) / 11` actually equals `⌈1 + l_avg(G)⌉` for the real number `l_avg(G)`;
  that translation is asserted in prose and only checked for the specific numbers 24 and
  11.
- "Connected" means only the weakest standard notion (a walk exists between every pair of
  vertices) — it does **not** assert 2-connectivity, biconnectivity, or anything about
  edge/vertex-connectivity numbers.
- "Tree" (`IsInducedTree`) is **defined**, not derived, as "connected, nonempty, and
  edges = vertices − 1." The file's own comment flags that the equivalence to "connected
  and acyclic" is assumed, not proved here.
- `LVal v k` computes the independence number of the **open** neighbourhood `N(v)` (v
  itself excluded) — but that exclusion is a side-effect of `Adj v v` being false, not an
  explicit `v ∉ m` clause. It also does **not** itself require `v < 11`; only the outer
  application (`l_all`) does.
- `IsHamPath` is about **Hamiltonian paths**, not cycles. Nonexistence of a Hamiltonian
  path is a strictly weaker/different claim than nonexistence of a Hamiltonian cycle
  (though here it happens to also rule out cycles as a corollary, that corollary is not
  separately stated).
- `TreeNumber k` is not merely "there exists a tree of order k" — it is an exact
  max-characterization (existence of a size-k tree *and* an upper bound of k on every
  induced tree). Good, but worth noting since a careless reading of "TreeNumber 4" alone
  (without the `∀`-clause) would only mean "≥4", not "=4".
- Nothing in the file asserts or checks that this is the *unique* minimal
  counterexample, that it appears in prior literature, or anything about other graphs;
  scope is strictly these four facts about this one graph.
- I cannot verify, from this file alone, whether "average of l(v) over all vertices" (with
  denominator = the number of vertices, 11) matches whatever normalization the original
  WOWII Conjecture 200 actually uses (e.g., average over vertices of positive degree, or
  some weighted average) — the header comment asserts this reading but I was told not to
  check any external source, so I cannot confirm it against the source text.

## 5. Where the Lean looks subtly off (or at least worth a second look)

- **`ConnectedIn`'s quantifier is unbounded** (`∀ u v, InMask m u → ...`, no `u,v < 11`),
  unlike `SubNbhd`/`Indep`, which do carry that bound explicitly. It happens to be
  self-consistent (an out-of-range bit in `m` would make `ConnectedIn m` outright false,
  via `ReachIn.refl`'s own `u < 11` requirement) as long as the ambient `m < 2048`
  convention is honoured by every caller, which it is in this file — but the definition
  itself doesn't enforce or even mention that bound, making it stylistically inconsistent
  with its sibling definitions and a plausible spot for a future edit to introduce a bug
  if someone relaxes the `m < 2048` hypothesis without checking `ConnectedIn`'s behavior.
- **The real-number-to-nat-formula translation for `⌈1+l_avg(G)⌉` is entirely
  comment-level.** Nowhere is there a Lean lemma of the shape `∀ a b, 0 < b → (a+b-1)/b =
  ⌈(a:ℚ)/b⌉` (or similar) proved and then instantiated; only the bare numeric identity `4
  = 1 + (24+10)/11` is `decide`d. This is mathematically unimpeachable for this one
  instance, but a reader hoping the Lean itself certifies the *general* nat-ceiling
  identity, not just this one arithmetic fact, will not find that here.
- **"G is simple" is proved but not asserted inside the main theorem's type.** A reader
  who reads only `conj200_counterexample`'s statement (not the surrounding file) has no
  direct guarantee, from that type alone, that G has no loops or is undirected — those
  facts live in the separately-proved (and separately named) `adj_irrefl_B`/`adj_symm_B`.
- **The tree-of-order-≤4 upper bound (`tree_upper`) is an honest, complete, kernel-checked
  case split over all 2^11 = 2048 vertex subsets** (`treeChk_all : allBelow treeChk 2048 =
  true`, and this compiled under `lean` with no `sorry`/`native_decide`), so despite being
  a "does every case satisfy a disjunction" style argument, it is not merely plausible —
  it is machine-verified for literally every subset, not sampled or asserted.
- No use of `native_decide` anywhere — every `decide`/`decide +kernel` is checked by the
  trusted kernel, which matters for a T3-tier check that's specifically supposed to guard
  against unearned trust in a checker.
- I found no `≤` used where `<` looks intended, no obviously-wrong bit-index, and no
  mismatched loop bound; `edgeCount`'s `u < v` inner bound, `card`'s 11-bound, and the
  `2048 = 2^11` mask bound are all consistent with an 11-vertex graph. The one place I'd
  flag as "loose" rather than "wrong" is the `ConnectedIn` quantifier bound noted above.
