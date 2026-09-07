/-
  WOWII Conjecture 200 — Lean 4 POSITIVE CONTROL (self-contained, no imports).

  THIS IS NOT A NEW RESULT.  Conjecture 200 of "Written on the Wall II" was already
  refuted in the literature; this file exists only to demonstrate, end to end, that the
  mining run's T3 tier can produce a kernel-checked witness for a case whose answer is
  independently known.

  The conjecture (informal):
      for every finite simple connected graph G, if tree(G) = ceil(1 + l_avg(G))
      then G has a Hamiltonian path,
  where  l(v)      = independence number of the subgraph induced on the open
                     neighbourhood N(v),
         l_avg(G)  = average of l(v) over all vertices,
         tree(G)   = largest order of an induced subgraph that is a tree.

  The graph G below is on 11 vertices; graph6 `J^~~u?_C?O?`.  Its adjacency matrix, as
  printed by `nauty-listg -a` (rows/columns indexed 0..10), is

        0 0 1 1 1 1 1 1 0 0 0        N(0)  = {2,3,4,5,6,7}
        0 0 1 1 1 1 1 1 0 0 0        N(1)  = {2,3,4,5,6,7}
        1 1 0 1 1 1 1 0 1 0 0        N(2)  = {0,1,3,4,5,6,8}
        1 1 1 0 1 1 1 0 0 1 0        N(3)  = {0,1,2,4,5,6,9}
        1 1 1 1 0 1 1 0 0 0 1        N(4)  = {0,1,2,3,5,6,10}
        1 1 1 1 1 0 0 0 0 0 0        N(5)  = {0,1,2,3,4}
        1 1 1 1 1 0 0 0 0 0 0        N(6)  = {0,1,2,3,4}
        1 1 0 0 0 0 0 0 0 0 0        N(7)  = {0,1}
        0 0 1 0 0 0 0 0 0 0 0        N(8)  = {2}
        0 0 0 1 0 0 0 0 0 0 0        N(9)  = {3}
        0 0 0 0 1 0 0 0 0 0 0        N(10) = {4}

  (`adj_matches_listg` below re-checks the bitmask encoding against this matrix.)
-/

set_option maxRecDepth 100000
set_option linter.unusedVariables false

/-! ## §1  Bounded loop combinators

We roll our own bounded quantifiers as `Nat.rec` folds.  The equation compiler's
structural recursion goes through `brecOn`, whose kernel reduction is quadratic and
measured ~25x slower here; `Nat.rec` reduces linearly. -/

/-- `allBelow f n = true`  iff  `f k = true` for every `k < n`. -/
def allBelow (f : Nat → Bool) (n : Nat) : Bool :=
  Nat.rec (motive := fun _ => Bool) true (fun k ih => f k && ih) n

/-- `anyBelow f n = true`  iff  `f k = true` for some `k < n`. -/
def anyBelow (f : Nat → Bool) (n : Nat) : Bool :=
  Nat.rec (motive := fun _ => Bool) false (fun k ih => f k || ih) n

/-- `sumBelow f n = f 0 + f 1 + ... + f (n-1)`. -/
def sumBelow (f : Nat → Nat) (n : Nat) : Nat :=
  Nat.rec (motive := fun _ => Nat) 0 (fun k ih => f k + ih) n

/-- `orBelow f n = f 0 ||| f 1 ||| ... ||| f (n-1)`. -/
def orBelow (f : Nat → Nat) (n : Nat) : Nat :=
  Nat.rec (motive := fun _ => Nat) 0 (fun k ih => f k ||| ih) n

theorem allBelow_iff (f : Nat → Bool) (n : Nat) :
    allBelow f n = true ↔ ∀ k, k < n → f k = true := by
  induction n with
  | zero => exact ⟨fun _ k hk => absurd hk (by omega), fun _ => rfl⟩
  | succ n ih =>
    show (f n && allBelow f n) = true ↔ _
    rw [Bool.and_eq_true, ih]
    constructor
    · intro h k hk
      by_cases hkn : k < n
      · exact h.2 k hkn
      · have : k = n := by omega
        subst this; exact h.1
    · intro h
      exact ⟨h n (by omega), fun k hk => h k (by omega)⟩

theorem anyBelow_iff (f : Nat → Bool) (n : Nat) :
    anyBelow f n = true ↔ ∃ k, k < n ∧ f k = true := by
  induction n with
  | zero => exact ⟨fun h => absurd h (by simp [anyBelow]), fun h => by
      obtain ⟨k, hk, _⟩ := h; exact absurd hk (by omega)⟩
  | succ n ih =>
    show (f n || anyBelow f n) = true ↔ _
    rw [Bool.or_eq_true, ih]
    constructor
    · intro h
      cases h with
      | inl h => exact ⟨n, by omega, h⟩
      | inr h => obtain ⟨k, hk, hf⟩ := h; exact ⟨k, by omega, hf⟩
    · intro h
      obtain ⟨k, hk, hf⟩ := h
      by_cases hkn : k < n
      · exact Or.inr ⟨k, hkn, hf⟩
      · have : k = n := by omega
        subst this; exact Or.inl hf

/-! ## §2  The graph G -/

/-- `rowMask u` is the neighbourhood of vertex `u` as a bitmask: bit `v` is set iff
`u` and `v` are adjacent.  Vertices are `0, 1, ..., 10`. -/
def rowMask (u : Nat) : Nat :=
  [252, 252, 379, 631, 1135, 31, 31, 3, 4, 8, 16].getD u 0

/-- Adjacency in G. -/
def Adj (u v : Nat) : Prop := u < 11 ∧ v < 11 ∧ (rowMask u).testBit v = true

/-- Boolean version of `Adj`. -/
def adjB (u v : Nat) : Bool :=
  decide (u < 11) && decide (v < 11) && (rowMask u).testBit v

instance instDecAdj (u v : Nat) : Decidable (Adj u v) :=
  inferInstanceAs (Decidable (u < 11 ∧ v < 11 ∧ (rowMask u).testBit v = true))

theorem adj_iff (u v : Nat) : Adj u v ↔ adjB u v = true := by
  simp [Adj, adjB, and_assoc]

/-- The adjacency matrix exactly as `nauty-listg -a` prints it for `J^~~u?_C?O?`. -/
def listgRow (u : Nat) : List Nat :=
  [[0,0,1,1,1,1,1,1,0,0,0],
   [0,0,1,1,1,1,1,1,0,0,0],
   [1,1,0,1,1,1,1,0,1,0,0],
   [1,1,1,0,1,1,1,0,0,1,0],
   [1,1,1,1,0,1,1,0,0,0,1],
   [1,1,1,1,1,0,0,0,0,0,0],
   [1,1,1,1,1,0,0,0,0,0,0],
   [1,1,0,0,0,0,0,0,0,0,0],
   [0,0,1,0,0,0,0,0,0,0,0],
   [0,0,0,1,0,0,0,0,0,0,0],
   [0,0,0,0,1,0,0,0,0,0,0]].getD u []

/-- The bitmask encoding agrees with the printed adjacency matrix. -/
theorem adj_matches_listg :
    allBelow (fun u => allBelow (fun v =>
      (listgRow u).getD v 0 == (bif adjB u v then 1 else 0)) 11) 11 = true := by
  decide

/-- G is simple: no loops. -/
theorem adj_irrefl_B : allBelow (fun u => !(adjB u u)) 11 = true := by decide

/-- G is undirected. -/
theorem adj_symm_B :
    allBelow (fun u => allBelow (fun v => !(adjB u v) || adjB v u) 11) 11 = true := by decide

theorem adj_symm {u v : Nat} (h : Adj u v) : Adj v u := by
  have hu := h.1
  have hv := h.2.1
  have hB : adjB u v = true := (adj_iff u v).1 h
  have h1 := (allBelow_iff _ _).1 ((allBelow_iff _ _).1 adj_symm_B u hu) v hv
  rw [hB] at h1
  simp at h1
  exact (adj_iff v u).2 h1

theorem adj_lt {u v : Nat} (h : Adj u v) : u < 11 ∧ v < 11 := ⟨h.1, h.2.1⟩

/-! ## §3  Part 1 of the theorem: G is connected -/

/-- `Reach u v`: there is a walk in G from `u` to `v`. -/
inductive Reach : Nat → Nat → Prop
  | refl (u : Nat) : Reach u u
  | step {u v w : Nat} : Adj u v → Reach v w → Reach u w

theorem Reach.trans : ∀ {a b c : Nat}, Reach a b → Reach b c → Reach a c
  | _, _, _, .refl _, h => h
  | _, _, _, .step hadj hr, h => .step hadj (Reach.trans hr h)

/-- G is connected: every vertex is joined to every vertex by a walk. -/
def Connected : Prop := ∀ u, u < 11 → ∀ v, v < 11 → Reach u v

theorem reach_to_zero : ∀ u, u < 11 → Reach u 0 := by
  intro u hu
  match u, hu with
  | 0, _ => exact .refl 0
  | 1, _ => exact .step (show Adj 1 2 by decide) (.step (show Adj 2 0 by decide) (.refl 0))
  | 2, _ => exact .step (show Adj 2 0 by decide) (.refl 0)
  | 3, _ => exact .step (show Adj 3 0 by decide) (.refl 0)
  | 4, _ => exact .step (show Adj 4 0 by decide) (.refl 0)
  | 5, _ => exact .step (show Adj 5 0 by decide) (.refl 0)
  | 6, _ => exact .step (show Adj 6 0 by decide) (.refl 0)
  | 7, _ => exact .step (show Adj 7 0 by decide) (.refl 0)
  | 8, _ => exact .step (show Adj 8 2 by decide) (.step (show Adj 2 0 by decide) (.refl 0))
  | 9, _ => exact .step (show Adj 9 3 by decide) (.step (show Adj 3 0 by decide) (.refl 0))
  | 10, _ => exact .step (show Adj 10 4 by decide) (.step (show Adj 4 0 by decide) (.refl 0))

theorem reach_from_zero : ∀ v, v < 11 → Reach 0 v := by
  intro v hv
  match v, hv with
  | 0, _ => exact .refl 0
  | 1, _ => exact .step (show Adj 0 2 by decide) (.step (show Adj 2 1 by decide) (.refl 1))
  | 2, _ => exact .step (show Adj 0 2 by decide) (.refl 2)
  | 3, _ => exact .step (show Adj 0 3 by decide) (.refl 3)
  | 4, _ => exact .step (show Adj 0 4 by decide) (.refl 4)
  | 5, _ => exact .step (show Adj 0 5 by decide) (.refl 5)
  | 6, _ => exact .step (show Adj 0 6 by decide) (.refl 6)
  | 7, _ => exact .step (show Adj 0 7 by decide) (.refl 7)
  | 8, _ => exact .step (show Adj 0 2 by decide) (.step (show Adj 2 8 by decide) (.refl 8))
  | 9, _ => exact .step (show Adj 0 3 by decide) (.step (show Adj 3 9 by decide) (.refl 9))
  | 10, _ => exact .step (show Adj 0 4 by decide) (.step (show Adj 4 10 by decide) (.refl 10))

theorem G_connected : Connected :=
  fun u hu v hv => (reach_to_zero u hu).trans (reach_from_zero v hv)

/-! ## §4  Vertex sets as bitmasks

A vertex set is encoded by a natural number `m < 2^11 = 2048`: vertex `v` (with `v < 11`)
belongs to the set iff bit `v` of `m` is set.  This is a bijection between the naturals
below 2048 and the subsets of `{0,...,10}`. -/

/-- Vertex `v` belongs to the vertex set encoded by the bitmask `m`. -/
def InMask (m v : Nat) : Prop := m.testBit v = true

instance instDecInMask (m v : Nat) : Decidable (InMask m v) :=
  inferInstanceAs (Decidable (m.testBit v = true))

theorem testBit_big {m u : Nat} (h : m < 2048) (hu : 11 ≤ u) : m.testBit u = false := by
  have h1 : m >>> u = 0 := by
    rw [Nat.shiftRight_eq_div_pow]
    apply Nat.div_eq_of_lt
    calc m < 2048 := h
      _ = 2 ^ 11 := by rfl
      _ ≤ 2 ^ u := Nat.pow_le_pow_right (by omega) hu
  simp [Nat.testBit, h1]

theorem inMask_lt {m u : Nat} (hm : m < 2048) (h : InMask m u) : u < 11 := by
  cases Nat.lt_or_ge u 11 with
  | inl h' => exact h'
  | inr h' =>
    rw [InMask, testBit_big hm h'] at h
    exact Bool.noConfusion h

/-- The number of vertices in the vertex set `m`. -/
def card (m : Nat) : Nat := sumBelow (fun v => bif m.testBit v then 1 else 0) 11

/-- The number of edges of G having both endpoints in the vertex set `m`, i.e. the number
of edges of the subgraph of G induced on `m`. -/
def edgeCount (m : Nat) : Nat :=
  sumBelow (fun v => sumBelow (fun u =>
    bif m.testBit u && m.testBit v && adjB u v then 1 else 0) v) 11

/-- `ReachIn m u v`: there is a walk in G from `u` to `v` all of whose vertices lie in the
vertex set `m`; i.e. `u` reaches `v` in the subgraph induced on `m`. -/
inductive ReachIn (m : Nat) : Nat → Nat → Prop
  | refl {u} : u < 11 → InMask m u → ReachIn m u u
  | step {u v w} : u < 11 → InMask m u → Adj u v → ReachIn m v w → ReachIn m u w

/-- The subgraph of G induced on the vertex set `m` is connected. -/
def ConnectedIn (m : Nat) : Prop := ∀ u v, InMask m u → InMask m v → ReachIn m u v

theorem ReachIn.trans {m : Nat} : ∀ {a b c : Nat}, ReachIn m a b → ReachIn m b c → ReachIn m a c
  | _, _, _, .refl _ _, h => h
  | _, _, _, .step h1 h2 hadj hr, h => .step h1 h2 hadj (ReachIn.trans hr h)

theorem reachIn_head {m u w : Nat} (h : ReachIn m u w) : u < 11 ∧ InMask m u := by
  cases h with
  | refl h1 h2 => exact ⟨h1, h2⟩
  | step h1 h2 _ _ => exact ⟨h1, h2⟩

/-- If `C` is closed under taking neighbours inside `m`, no walk inside `m` can leave it. -/
theorem reach_stays {m C : Nat}
    (hcl : ∀ x y, x < 11 → y < 11 → InMask C x → InMask m y → Adj x y → InMask C y)
    {u w : Nat} (h : ReachIn m u w) : InMask C u → InMask C w := by
  induction h with
  | refl _ _ => exact fun hu => hu
  | step hu hum hadj hrest ih =>
    intro hC
    exact ih (hcl _ _ hu hadj.2.1 hC (reachIn_head hrest).2 hadj)

/-! ### A checkable certificate for "the induced subgraph on `m` is disconnected" -/

/-- One round of neighbour expansion of the vertex set `s`, staying inside `m`. -/
def expand (m s : Nat) : Nat :=
  s ||| (orBelow (fun k => bif s.testBit k then rowMask k else 0) 11 &&& m)

/-- The connected component of `u` inside `m` (11 rounds saturate on 11 vertices). -/
def compOf (m u : Nat) : Nat :=
  Nat.rec (motive := fun _ => Nat) (1 <<< u) (fun _ s => expand m s) 11

/-- Some vertex of `m` (the largest one), or `11` if `m` contains no vertex. -/
def someVert (m : Nat) : Nat :=
  Nat.rec (motive := fun _ => Nat) 11 (fun k ih => bif m.testBit k then k else ih) 11

/-- `C` is closed under taking neighbours inside `m`. -/
def closedB (m C : Nat) : Bool :=
  allBelow (fun x => allBelow (fun y =>
    !(C.testBit x) || !(m.testBit y) || !(adjB x y) || C.testBit y) 11) 11

theorem closedB_spec {m C : Nat} (h : closedB m C = true) :
    ∀ x y, x < 11 → y < 11 → InMask C x → InMask m y → Adj x y → InMask C y := by
  intro x y hx hy hCx hmy hadj
  have hb := (allBelow_iff _ _).1 ((allBelow_iff _ _).1 h x hx) y hy
  rw [InMask] at hCx hmy ⊢
  rw [hCx, hmy, (adj_iff x y).1 hadj] at hb
  simpa using hb

/-- A checkable certificate that the subgraph induced on `m` is disconnected: some vertex
`u` of `m` lies in a set `C` closed under neighbours inside `m`, and some vertex of `m`
lies outside `C`. -/
def disconCert (m : Nat) : Bool :=
  m.testBit (someVert m) && (compOf m (someVert m)).testBit (someVert m) &&
    closedB m (compOf m (someVert m)) &&
    anyBelow (fun v => m.testBit v && !((compOf m (someVert m)).testBit v)) 11

theorem not_connectedIn_of_cert {m : Nat} (h : disconCert m = true) : ¬ ConnectedIn m := by
  intro hconn
  rw [disconCert, Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true] at h
  obtain ⟨⟨⟨h1, h2⟩, h3⟩, h4⟩ := h
  obtain ⟨v, hv11, hv⟩ := (anyBelow_iff _ _).1 h4
  rw [Bool.and_eq_true] at hv
  have hvm : InMask m v := hv.1
  have key : InMask (compOf m (someVert m)) v :=
    reach_stays (closedB_spec h3) (hconn _ _ h1 hvm) h2
  rw [InMask] at key
  rw [key] at hv
  simp at hv

/-! ## §5  Part 2 of the theorem: tree(G) = 4

`IsInducedTree m` says that the subgraph induced on the vertex set `m` is a tree.  We use
the standard finite-graph characterisation "nonempty, connected, and with exactly one edge
fewer than it has vertices", which for a finite graph is equivalent to "connected and
acyclic".  (See log.md: this equivalence is a classical theorem that is *not* formalised
here, so it is an assumption built into the encoding of the word "tree".) -/
def IsInducedTree (m : Nat) : Prop :=
  0 < card m ∧ ConnectedIn m ∧ edgeCount m + 1 = card m

/-- `tree(G) = k`: some induced subgraph on `k` vertices is a tree, and no induced
subgraph that is a tree has more than `k` vertices. -/
def TreeNumber (k : Nat) : Prop :=
  (∃ m, m < 2048 ∧ IsInducedTree m ∧ card m = k) ∧
  (∀ m, m < 2048 → IsInducedTree m → card m ≤ k)

/-- For every vertex set `m`: either it has at most 4 vertices, or it does not have
`|V| - 1` edges, or it is certifiably disconnected. -/
def treeChk (m : Nat) : Bool :=
  decide (card m ≤ 4) || !(decide (edgeCount m + 1 = card m)) || disconCert m

theorem treeChk_all : allBelow treeChk 2048 = true := by decide +kernel

theorem tree_upper : ∀ m, m < 2048 → IsInducedTree m → card m ≤ 4 := by
  intro m hm ht
  cases Nat.lt_or_ge 4 (card m) with
  | inr h => omega
  | inl h =>
    have hb := (allBelow_iff _ _).1 treeChk_all m hm
    rw [treeChk] at hb
    have e1 : decide (card m ≤ 4) = false := by simp; omega
    have e2 : decide (edgeCount m + 1 = card m) = true := by simp [ht.2.2]
    rw [e1, e2] at hb
    simp at hb
    exact absurd ht.2.1 (not_connectedIn_of_cert hb)

/-- The vertex set `{0,5,6,7}` (bitmask 225) induces a tree: the star with centre 0. -/
theorem mem225 : ∀ u, InMask 225 u → u = 0 ∨ u = 5 ∨ u = 6 ∨ u = 7 := by
  intro u h
  have hu : u < 11 := inMask_lt (by omega) h
  revert h
  match u, hu with
  | 0, _ => exact fun _ => Or.inl rfl
  | 1, _ => exact fun h => absurd h (by decide)
  | 2, _ => exact fun h => absurd h (by decide)
  | 3, _ => exact fun h => absurd h (by decide)
  | 4, _ => exact fun h => absurd h (by decide)
  | 5, _ => exact fun _ => Or.inr (Or.inl rfl)
  | 6, _ => exact fun _ => Or.inr (Or.inr (Or.inl rfl))
  | 7, _ => exact fun _ => Or.inr (Or.inr (Or.inr rfl))
  | 8, _ => exact fun h => absurd h (by decide)
  | 9, _ => exact fun h => absurd h (by decide)
  | 10, _ => exact fun h => absurd h (by decide)

theorem conn225 : ConnectedIn 225 := by
  have h0 : ∀ u, InMask 225 u → ReachIn 225 u 0 := by
    intro u h
    rcases mem225 u h with rfl | rfl | rfl | rfl
    · exact .refl (by decide) (by decide)
    · exact .step (by decide) (by decide) (show Adj 5 0 by decide) (.refl (by decide) (by decide))
    · exact .step (by decide) (by decide) (show Adj 6 0 by decide) (.refl (by decide) (by decide))
    · exact .step (by decide) (by decide) (show Adj 7 0 by decide) (.refl (by decide) (by decide))
  have h1 : ∀ v, InMask 225 v → ReachIn 225 0 v := by
    intro v h
    rcases mem225 v h with rfl | rfl | rfl | rfl
    · exact .refl (by decide) (by decide)
    · exact .step (by decide) (by decide) (show Adj 0 5 by decide) (.refl (by decide) (by decide))
    · exact .step (by decide) (by decide) (show Adj 0 6 by decide) (.refl (by decide) (by decide))
    · exact .step (by decide) (by decide) (show Adj 0 7 by decide) (.refl (by decide) (by decide))
  exact fun u v hu hv => (h0 u hu).trans (h1 v hv)

theorem G_treeNumber : TreeNumber 4 :=
  ⟨⟨225, by omega, ⟨by decide, conn225, by decide⟩, by decide⟩, tree_upper⟩

/-! ## §6  Part 3 of the theorem: the l-values and their sum

`l(v)` is the independence number of the subgraph induced on the open neighbourhood `N(v)`.
Since that subgraph is *induced*, a set of vertices of `N(v)` is independent in it exactly
when it is independent in G, so `l v = k` says: some `k`-element set of pairwise
non-adjacent neighbours of `v` exists, and no larger one does. -/

/-- Every vertex of the set `m` is a neighbour of `v`, i.e. `m ⊆ N(v)`. -/
def SubNbhd (v m : Nat) : Prop := ∀ u, u < 11 → InMask m u → Adj v u

/-- The vertices of the set `m` are pairwise non-adjacent. -/
def Indep (m : Nat) : Prop :=
  ∀ u w, u < 11 → w < 11 → InMask m u → InMask m w → u ≠ w → ¬ Adj u w

/-- `LVal v k` says `l(v) = k`. -/
def LVal (v k : Nat) : Prop :=
  (∃ m, m < 2048 ∧ SubNbhd v m ∧ Indep m ∧ card m = k) ∧
  (∀ m, m < 2048 → SubNbhd v m → Indep m → card m ≤ k)

def subNbhdB (v m : Nat) : Bool := allBelow (fun u => !(m.testBit u) || adjB v u) 11

def indepB (m : Nat) : Bool :=
  allBelow (fun u => allBelow (fun w =>
    !(m.testBit u) || !(m.testBit w) || decide (u = w) || !(adjB u w)) 11) 11

theorem subNbhd_iff (v m : Nat) : SubNbhd v m ↔ subNbhdB v m = true := by
  rw [subNbhdB, allBelow_iff]
  constructor
  · intro h u hu
    cases hb : m.testBit u with
    | false => simp [hb]
    | true =>
      have hA := (adj_iff v u).1 (h u hu hb)
      simp [hb, hA]
  · intro h u hu hm
    have hb := h u hu
    rw [InMask] at hm
    rw [hm] at hb
    simp at hb
    exact (adj_iff v u).2 hb

theorem indep_iff (m : Nat) : Indep m ↔ indepB m = true := by
  rw [indepB, allBelow_iff]
  constructor
  · intro h u hu
    rw [allBelow_iff]
    intro w hw
    cases hbu : m.testBit u with
    | false => simp [hbu]
    | true =>
      cases hbw : m.testBit w with
      | false => simp [hbw]
      | true =>
        cases hEq : decide (u = w) with
        | true => simp [hEq]
        | false =>
          have hne : u ≠ w := by simpa using hEq
          have hnot := h u w hu hw hbu hbw hne
          have h2 : adjB u w = false := by
            cases hab : adjB u w with
            | false => rfl
            | true => exact absurd ((adj_iff u w).2 hab) hnot
          simp [h2]
  · intro h u w hu hw hmu hmw hne hadj
    have hb := (allBelow_iff _ _).1 (h u hu) w hw
    rw [InMask] at hmu hmw
    have hd : decide (u = w) = false := by simp [hne]
    rw [hmu, hmw, hd, (adj_iff u w).1 hadj] at hb
    simp at hb

/-- For every vertex set `m`: if `m ⊆ N(v)` and `m` is independent then `|m| ≤ k`. -/
def lChk (v k : Nat) (m : Nat) : Bool :=
  !(subNbhdB v m) || !(indepB m) || decide (card m ≤ k)

theorem lVal_of {v k mw : Nat} (hw : mw < 2048) (h1 : subNbhdB v mw = true)
    (h2 : indepB mw = true) (h3 : card mw = k)
    (hall : allBelow (lChk v k) 2048 = true) : LVal v k := by
  refine ⟨⟨mw, hw, (subNbhd_iff v mw).2 h1, (indep_iff mw).2 h2, h3⟩, ?_⟩
  intro m hm hs hi
  have hb := (allBelow_iff _ _).1 hall m hm
  rw [lChk, (subNbhd_iff v m).1 hs, (indep_iff m).1 hi] at hb
  simpa using hb

-- witnesses: {5,6,7} for v=0,1;  {0,1,8} for v=2;  {0,1,9} for v=3;  {0,1,10} for v=4;
--            {0,1} for v=5,6,7;  {2},{3},{4} for v=8,9,10.
theorem l_0  : LVal 0  3 := lVal_of (mw := 224)  (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_1  : LVal 1  3 := lVal_of (mw := 224)  (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_2  : LVal 2  3 := lVal_of (mw := 259)  (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_3  : LVal 3  3 := lVal_of (mw := 515)  (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_4  : LVal 4  3 := lVal_of (mw := 1027) (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_5  : LVal 5  2 := lVal_of (mw := 3)    (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_6  : LVal 6  2 := lVal_of (mw := 3)    (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_7  : LVal 7  2 := lVal_of (mw := 3)    (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_8  : LVal 8  1 := lVal_of (mw := 4)    (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_9  : LVal 9  1 := lVal_of (mw := 8)    (by omega) (by decide) (by decide) (by decide) (by decide +kernel)
theorem l_10 : LVal 10 1 := lVal_of (mw := 16)   (by omega) (by decide) (by decide) (by decide) (by decide +kernel)

/-! ## §7  Part 4 of the theorem: G has no Hamiltonian path -/

/-- `Chain' R l`: consecutive entries of `l` are related by `R`. -/
inductive Chain' (R : Nat → Nat → Prop) : List Nat → Prop
  | nil : Chain' R []
  | single (a : Nat) : Chain' R [a]
  | cons {a b : Nat} {l : List Nat} : R a b → Chain' R (b :: l) → Chain' R (a :: b :: l)

/-- `Nodup l`: no entry of `l` occurs twice. -/
inductive Nodup : List Nat → Prop
  | nil : Nodup []
  | cons {a : Nat} {l : List Nat} : a ∉ l → Nodup l → Nodup (a :: l)

def firstOf : List Nat → Option Nat
  | [] => none
  | a :: _ => some a

def lastOf : List Nat → Option Nat
  | [] => none
  | [a] => some a
  | _ :: t => lastOf t

theorem lastOf_cons_cons (x y : Nat) (t : List Nat) :
    lastOf (x :: y :: t) = lastOf (y :: t) := rfl

/-- `l` is a Hamiltonian path of G: its entries are pairwise distinct, consecutive entries
are adjacent, and every vertex of G occurs in it. -/
def IsHamPath (l : List Nat) : Prop :=
  Nodup l ∧ Chain' Adj l ∧ (∀ v, v < 11 → v ∈ l)

/-- If every neighbour of `v` equals `w`, then `v` has at most one neighbour. -/
theorem uniq_nbr {v w : Nat}
    (hb : allBelow (fun z => !(adjB v z) || decide (z = w)) 11 = true) :
    ∀ x y, Adj v x → Adj v y → x = y := by
  intro x y hx hy
  have h1 := (allBelow_iff _ _).1 hb x hx.2.1
  have h2 := (allBelow_iff _ _).1 hb y hy.2.1
  rw [(adj_iff v x).1 hx] at h1
  rw [(adj_iff v y).1 hy] at h2
  simp at h1 h2
  omega

/-- **The endpoint lemma.**  A vertex with at most one neighbour can only occur as the
first or the last entry of a path: at an interior position it would have two distinct
neighbours in the list. -/
theorem deg_one_endpoint {v : Nat} (huniq : ∀ x y, Adj v x → Adj v y → x = y) :
    ∀ l : List Nat, Chain' Adj l → Nodup l → v ∈ l →
      firstOf l = some v ∨ lastOf l = some v := by
  intro l
  induction l with
  | nil => intro _ _ hv; exact absurd hv (by simp)
  | cons x t ih =>
    intro hc hn hv
    cases t with
    | nil =>
      left
      cases hv with
      | head => rfl
      | tail _ h => exact absurd h (by simp)
    | cons y t' =>
      have hxy : Adj x y := by cases hc with | cons h _ => exact h
      have hcy : Chain' Adj (y :: t') := by cases hc with | cons _ h => exact h
      have hxn : x ∉ y :: t' := by cases hn with | cons h _ => exact h
      have hny : Nodup (y :: t') := by cases hn with | cons _ h => exact h
      cases Nat.decEq v x with
      | isTrue hvx => left; rw [firstOf, hvx]
      | isFalse hvx =>
        have hvt : v ∈ y :: t' := by
          cases hv with
          | head => exact absurd rfl hvx
          | tail _ h => exact h
        cases ih hcy hny hvt with
        | inr h => right; rw [lastOf_cons_cons]; exact h
        | inl h =>
          have hvy : v = y := by
            have : some v = some y := by rw [← h]; rfl
            exact Option.some.inj this
          cases t' with
          | nil => right; rw [lastOf_cons_cons, hvy]; rfl
          | cons z t'' =>
            exfalso
            have hyz : Adj y z := by cases hcy with | cons h _ => exact h
            have h1 : Adj v x := by rw [hvy]; exact adj_symm hxy
            have h2 : Adj v z := by rw [hvy]; exact hyz
            have hxz : x = z := huniq x z h1 h2
            exact hxn (by rw [hxz]; exact List.Mem.tail _ (List.Mem.head _))

theorem no_ham_path : ¬ ∃ l : List Nat, IsHamPath l := by
  intro h
  obtain ⟨l, hn, hc, hall⟩ := h
  have e8 := deg_one_endpoint (uniq_nbr (v := 8) (w := 2) (by decide)) l hc hn (hall 8 (by omega))
  have e9 := deg_one_endpoint (uniq_nbr (v := 9) (w := 3) (by decide)) l hc hn (hall 9 (by omega))
  have e10 := deg_one_endpoint (uniq_nbr (v := 10) (w := 4) (by decide)) l hc hn (hall 10 (by omega))
  -- three vertices of degree 1, but a path has only two endpoints
  have key : ∀ (o : Option Nat) (p q : Nat), o = some p → o = some q → p = q := by
    intro o p q h1 h2
    rw [h1] at h2
    exact (Option.some.inj h2).symm
  rcases e8 with a | a <;> rcases e9 with b | b <;> rcases e10 with c | c
  · exact absurd (key _ _ _ a b) (by decide)
  · exact absurd (key _ _ _ a b) (by decide)
  · exact absurd (key _ _ _ a c) (by decide)
  · exact absurd (key _ _ _ b c) (by decide)
  · exact absurd (key _ _ _ b c) (by decide)
  · exact absurd (key _ _ _ a c) (by decide)
  · exact absurd (key _ _ _ a b) (by decide)
  · exact absurd (key _ _ _ a b) (by decide)
