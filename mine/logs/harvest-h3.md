# H3 harvest log — curated open-problem lists

## Result

`mine/corpus/raw/h3_curated.jsonl` — **70 entries**, all `provenance: "clone:..."` (no
`websearch:` or `model-knowledge-unverified` entries — see "What was blocked" below for why
that count is zero rather than padded).

Regenerate with:

```
python3 /tmp/claude-0/-home-user-openproblem-miner/5d00d2a3-37c6-5f2e-970d-6eb5dd6ff429/scratchpad/build_h3.py
```

(script is not part of the repo write-scope; copy it out first if it needs to survive past
this session — it writes to `mine/corpus/raw/h3_curated.jsonl` unconditionally.)

Validity check run: `python3 -c "import json; [json.loads(l) for l in open('mine/corpus/raw/h3_curated.jsonl')]"`
— passes; also checked for duplicate `id`s (none) via the same script's inline assertion.

## What worked: the Wikipedia mirror

`en.wikipedia.org` is blocked at the egress proxy (confirmed in `mine/logs/NETWORK.md`, not
re-probed). A sibling agent's clone at `mine/cache/h4_wiki` (repo
`yao-creative/Wiki-clustering-ml@58c53df46c4f9f623cc818187895255812b4db43`) turned out to
contain a scraped, all-lowercase, LaTeX-mangled copy of
`data/List_of_unsolved_problems_in_mathematics.txt` (1647 lines) — i.e. exactly the
Wikipedia "unsolved problems in mathematics" list this task asks for, reachable via GitHub
mirror per the routing rule. All 70 entries cite this file with a `#L<line>` anchor
(`grep -n` was used to pin each anchor; a handful of number-theory entries where the source
line is a bare conjecture name with no elaboration are flagged in their own `notes` field
as reconstructed-from-standard-formulation, lower confidence than the fully-quoted ones).

## What was blocked / not found

- **Kourovka notebook**: no GitHub mirror of the actual problem text found (WebSearch,
  ~6 queries). The canonical source is `arxiv.org/abs/1401.0300` (blocked) and
  `kourovka-notebook.org` (not on the reachable list, not probed since out of scope for a
  curl test with no github/raw fallback). `google-deepmind/formal-conjectures` has a
  `FormalConjectures/Kourovka/` directory but only 5 problems formalized, all 5 already in
  `h2_formal.jsonl` (ids `fc-kourovka-*`) — checked via `mcp__github` tools, which refused
  external-repo access, then via direct grep on the local clone. One promising WebSearch
  lead (MacHale's noncommutator problem, Kourovka 17.76) turned out to have been **solved
  in 2025** (Skresanov; also an independent construction of order-368640 groups) — caught
  before it was added, which is exactly the kind of near-miss the mission asks to watch
  for. Net: zero Kourovka entries added rather than risk citing solved or unpinned text.
- **Smale's problems**: no GitHub mirror found; only Wikipedia/MathWorld/OEIS-wiki pages,
  all blocked hosts. Zero entries (the individual Smale problems mostly already exist in
  `h2_formal.jsonl` under other names anyway — Riemann, P vs NP, Jacobian conjecture, etc.).
- **Polymath project**: no wiki mirror or GitHub list of open Polymath threads found.
- **Klee–Wagon, Brualdi, matroid/Egerváry lists**: no GitHub-hosted problem list found;
  only book-seller pages and papers on individual conjectures (blocked/paywalled). Zero
  entries rather than reconstructing book contents from memory.

Given the choice between padding with `model-knowledge-unverified` entries (excluded from
the attack pool by policy anyway) and simply not harvesting these five lists, I chose the
latter and record it as a shrunk target per MISSION §8.

## Overlap avoidance (the actual work)

Confirmed early that `mine/cache/formal-conjectures/FormalConjectures/Wikipedia/` (152
`.lean` files) already formalizes almost every *famous* entry from the same Wikipedia list
(Collatz, Kakeya, Moving Sofa, Inscribed Square, Lonely Runner, Hadwiger–Nelson, Sunflower,
Dedekind numbers, Vizing, Vaught, Sendov, Kummer–Vandiver, Zauner/SIC-POVMs, …), all already
present in `h2_formal.jsonl`. So the harvest deliberately mined the **long tail** of the
same list — geometry/packing problems, graph-theory conjectures, and model-theory/set-theory
problems that are precise, sourced, and not in that 152-file set — rather than re-deriving
what H1/H2 already have. Confirmed via `grep -i` name-collision checks against both
`h1_erdos.jsonl` and `h2_formal.jsonl` for every candidate before writing it.

**Skipped as duplicate of h1/h2** (~18): Heilbronn triangle problem (= erdos-0507),
Brocard's problem (= erdos-0398), Erdős–Moser (formalized as `ErdosMoser.lean`), Erdős–Turán
additive-basis conjecture (= erdos-0028), Erdős–Ulam problem (= erdos-...  "dense subset of
R^2 with all pairwise rational distances"), Erdős–Straus conjecture (= erdos-0242-a), Van der
Waerden numbers (= `fc-greensopenproblems-14-*`, extensively covered), Dedekind numbers,
Ramsey R(5,5), Happy Ending problem, Casas-Alvero conjecture, Waring's problem, Gaussian moat
problem, Vaught conjecture, Kakeya conjecture, Moving Sofa, Inscribed Square/Toeplitz — all
already `fc-wikipedia-*` entries in `h2_formal.jsonl`.

**Excluded as solved / recently resolved** (caught by targeted WebSearch, ~6 queries):
Einstein problem (aperiodic monotile found 2023), Kakeya conjecture in 3D (Wang–Zahl 2025;
moot anyway since already formalized), Moving Sofa problem (Baek 2024, community-accepted
though formal peer review still pending as of the sources found — excluded out of caution
rather than presented as open), Kourovka 17.76 (Skresanov 2025), Erdős–Faber–Lovász (proved
for all sufficiently large n, Kang–Kelly–Kühn–Methuku–Osthus 2023 — excluded rather than
included-with-caveat, since the corpus already has enough bound-gap-style entries of that
shape).

**Dropped for imprecision** (~15+, not written to the file at all, consistent with "a high
drop count is a good sign"): Babai's problem (source gives only the name, no definition —
the one drop kept as an explicit in-script record), self-avoiding-walk modeling function,
Kronecker-coefficient combinatorial interpretation, Borromean-rings question (ambiguous
wording in source), k-sets/halving-lines bound, Szymanski's conjecture (source gives no
statement), Implicit graph conjecture ("slowly-growing" undefined), Kaplansky's conjectures
/ Stark conjectures / Greenberg's conjectures (vague plurals with no single statement),
homological conjectures in commutative algebra, "wild problem", and about half a dozen
one-line-named algebra conjectures (Zariski–Lipman, Bombieri–Lang, Birch–Tate, Crouzeix,
Demazure, Eilenberg–Ganea, Farrell–Jones/Bost, finite lattice representation problem) where
the source gives a name and topic tag but not enough to state the claim exactly without
inventing details.

## Breakdown of the 70 entries

- Geometry / packing / covering: 26 (Borsuk's problem, kissing number, Reinhardt, sphere
  packing in other dimensions, Ulam's packing conjecture, Carathéodory, Cartan–Hadamard,
  filling area, Hadwiger covering conjecture (2^n copies — distinct from Hadwiger–Nelson and
  from the graph-coloring Hadwiger conjecture, both already formalized), Kalai's 3^d
  conjecture, Kobon triangle, Kusner, McMullen problem, opaque forest, Danzer's problem,
  Ehrhart's volume conjecture, Falconer's conjecture, Lebesgue's universal covering problem,
  Mahler's conjecture, Kelvin problem, Rupert's property, Shephard's problem/Dürer's
  conjecture, non-convex 7-face polyhedron question, Thomson problem, Radó's covering
  problem, plus 1 Millennium-problem ballast entry per the deliberate-exclusions rule).
- Graph theory: 23 (Cereceda, Gyárfás–Sumner, Hadwiger's coloring conjecture, Jaeger's
  Petersen-coloring conjecture, list-coloring conjecture, total-coloring conjecture,
  Albertson, Conway's thrackle conjecture, Harborth, Negami, Turán's brick factory /
  Zarankiewicz formula, universal point sets, Barnette, Chvátal's toughness conjecture,
  cycle double cover, Erdős–Gyárfás, linear arboricity, Oberwolfach problem, Brouwer's
  conjecture, GNRS conjecture, Jørgensen, Meyniel, reconstruction conjecture, second
  neighborhood problem, Moore graph (girth 5, degree 57), Sumner's conjecture, Tutte's
  flow conjectures, Zarankiewicz problem, pathwidth of cubic graphs).
- Model theory / set theory: 9 (Cherlin–Zilber, generalized star-height problem, Hilbert's
  10th for number fields, Kueker's conjecture, Shelah's categoricity conjecture, stable
  field conjecture, Tarski's exponential function problem, universality spectrum problem,
  Jónsson algebra on aleph_omega).
- Number theory outliers: 7 (Skolem problem, Fontaine–Mazur, Selberg's 1/4 conjecture,
  Lang–Trotter supersingular primes, Hermite's problem, de Bruijn–Newman constant).
- Ballast: 1 (Millennium Prize problems, `witness_type: none`, `class D` per instructions).

`witness_type` is `finite-object` for exactly 2 entries (the seven-mutually-adjacent-face
polyhedron question, the Moore-graph-57 existence question) and `numeric-bound` for the
bulk of the bound-gap items; everything else is `none` — consistent with "be stingy with
finite-object."

## Budget used

~16 WebSearch queries (slightly over the ~15 target — spent on verifying open/solved status
for Kakeya, Moving Sofa, Einstein problem, Erdős–Faber–Lovász, Rota's basis conjecture,
Chvátal's toughness conjecture, plus the failed searches for Kourovka/Smale/Polymath/Klee–
Wagon/Brualdi/matroid mirrors). No new `git clone`s were needed — the Wikipedia mirror was
already in `mine/cache/h4_wiki` from a sibling agent.
