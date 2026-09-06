# H6 harvest log — literature sweep

## Status of the standard sources

arXiv, OpenAlex, Crossref, Semantic Scholar, DBLP and zbMATH are all blocked at the egress
proxy (confirmed by the previous H6 attempt before this one; not re-probed per instructions).
No direct arXiv bulk API access was attempted in this run.

Reused caches, as instructed:

- `mine/cache/h6_conjectures-arxiv` — clone of `davisrbr/conjectures-arxiv`
  (commit `d2e3afe62098611fabd7236998acc73f64e4b3b7`, 2026-07-12). This turned out to be the
  real payload: it is the working data store of "OpenConjecture", a live pipeline that
  ingests arXiv math announcements, extracts `\begin{conjecture}` blocks from the LaTeX
  source, and labels each one with GPT-5-mini as `real_open_conjecture` /
  `not_real_conjecture` / `uncertain`, plus `interestingness`/`viability` scores. The most
  recent export, `data/exports_month_live_20260712/`, holds a cumulative dump: 4415
  extracted conjecture candidates from 26747 papers (`published_at` between 2025-12-30 and
  2026-07-09), of which 3520 are labeled `real_open_conjecture`. Restricting to categories
  `math.CO`/`math.NT`/`cs.DM` and short (<=~500 char) self-contained statements gave 1563
  candidates, which I hand-triaged (see below) rather than trusting the label alone.
- `mine/cache/h6_open-research-problems` — clone of the `open-research-problems` repo
  (commit `4506cceb...`). Checked both LaTeX files (`collection/problems-collection.tex`,
  `talentos-2025-26/NovosTalentos.tex`): every `\begin{conjecture}`/`\begin{problem}` block
  in `problems-collection.tex` is commented out (draft/abandoned numerical-semigroups notes
  on Wilf's conjecture, a 1978 conjecture anyway — out of the 2021-2026 window even if it
  weren't commented out), and `NovosTalentos.tex` has none at all. **This clone yielded
  nothing usable.**
- Old `mine/cache/h6_scripts/h6_query.py` (left by the killed prior attempt) confirmed the
  sqlite `conjectures_month_live_20260712.sqlite` backs the same data as the JSONL exports;
  I worked directly against the JSONL exports instead of re-running it.

## What I did

1. Joined `real_conjectures_gpt-5-mini.jsonl` (labels) against `conjectures.jsonl` (LaTeX
   `body_tex`, arXiv category/id) and `papers.jsonl` (abstracts), both from
   `data/exports_month_live_20260712/`, on `conjecture_id`/`arxiv_id`.
2. Filtered to `math.CO`/`math.NT`/`cs.DM`, `label == real_open_conjecture`, and statement
   length <=~500 chars (a proxy for "self-contained in under 5 lines").
3. Manually read `body_tex` + paper abstract for every entry I considered, because the LLM
   labeling pipeline demonstrably mis-tags some already-proved theorems as open conjectures
   when a paper conjectures something and then partially proves it in the same paper (see
   calibration note below) — I did **not** trust `label=real_open_conjecture` at face value.
4. Wrote `statement_nl` myself from the LaTeX + abstract, defining every symbol; dropped
   candidates where the extracted `body_tex` referenced paper-internal notation
   (`num_B(n,x)`, `N_r(n)`, "diamond rank", Ekedahl-Oort/automorphic-representation jargon,
   graph notation like a `triplestar`) that I could not pin down exactly from the snippet
   alone. Roughly half of everything I looked at closely was dropped for this reason.
5. Cross-checked the final list against `mine/corpus/raw/h2_formal.jsonl` (803 entries,
   DeepMind formal-conjectures corpus) by keyword grep. Found one real duplicate: Dean's
   conjecture (arXiv:2605.02731) is already in h2 (`fc-DeanCycles-a`/`-b`), already correctly
   narrowed to the k=5 residual case — **dropped from this file** to avoid duplication.
6. Ran 5 WebSearch queries (budget was ~15) to independently corroborate "what's actually
   still open" for the highest-value entries, since arXiv abstracts alone sometimes obscure
   exactly which residual case survives a paper's partial proof:
   - `Graham's rearrangement conjecture 1971 computer verification small primes`
   - `Bollobás–Nikiforov conjecture counterexample computer search small graphs`
   - `Pilz conjecture symmetric difference A Δ 2A Δ nA cardinality n`
   - `"recursively differentiable quasigroups" recursive MDS code q=14 q=18 open`
   - `"reflective" "dihedral" Ramsey numbers alternating path monotone path star arxiv 2607.06817`
   All five returned useful, on-topic results (arXiv/Springer/ResearchGate pages), confirming
   web search itself is not blocked even though direct arXiv fetches are assumed blocked.
   The last query (dihedral Ramsey numbers) is why entries `lit-*-computation-small-*-ramsey`
   are **absent**: I could not pin down the paper's precise definitions of `P^alt`, `S^sc`,
   `P^mon`, `C^mon` from search snippets alone, so I dropped all four candidates from that
   paper rather than guess at graph-family notation.

## Result

`mine/corpus/raw/h6_literature.jsonl`: **30 entries**, all valid JSON (checked via
`json.loads` per line, script: `python3 -c "import json; [json.loads(l) for l in
open('mine/corpus/raw/h6_literature.jsonl')]"`), all unique `id`s, all
`provenance: "clone:davisrbr/conjectures-arxiv@d2e3afe62098611fabd7236998acc73f64e4b3b7:..."`
citations (every entry traces to one arXiv preprint via that clone's extracted LaTeX +
metadata; no `websearch:` or `model-knowledge-unverified` entries were needed — the clone
alone, read carefully, cleared the ≥30 target). `witness_type`: 25 `finite-object`, 5
`numeric-bound`, 0 `none` — I was stingy with `finite-object` per instructions and only used
it where the object really is a finite combinatorial structure (a graph, a set, a coloring);
number-theoretic congruence/sign-law entries got `numeric-bound` instead since the "witness"
there is really an integer computation, not a discrete combinatorial object.

Regeneration: `python3 /tmp/claude-0/-home-user-openproblem-miner/5d00d2a3-37c6-5f2e-970d-6eb5dd6ff429/scratchpad/build_corpus.py`
(rewrites `mine/corpus/raw/h6_literature.jsonl` from scratch; the script embeds every
`statement_nl` etc. verbatim, so it is reproducible without re-reading the clone, though the
provenance line still points at the clone commit for audit).

## Witness-shape ratio (calibration datum)

Two different counts, because they measure different things:

**A. Heuristic keyword scan of the full 1563-candidate CO/NT/DM pool** (regex over
`plain_text`, before any manual reading — this is what the mission's bias section asks to
report "roughly"):
- "extremal-exact-value" pattern (`=<number>`, "is exactly N"): 552/1563 (35%) — but this
  regex badly over-matches; most of these are inequality bounds with a numeric constant
  (e.g. "≤ 4m/3"), not literal "the extremal value is exactly v" statements. Treat this
  number as an upper bound on the true count, not a real estimate.
- "forall + graph" pattern: 37/1563 (2%) — also an undercount, since most graph-universal
  statements don't literally contain the word "graph" near "for all" in the truncated text.
- "no-config-exists" pattern ("there is no X"): 4/1563 (0.3%) — genuinely rare in this pool;
  most conjectures in the wild are stated as upper/lower bounds, not nonexistence claims.
- Everything else ("other"): 869/1563 (56%) — dominated by asymptotic statements
  (Θ(n), o(1), "sufficiently large"), analytic/algebraic-geometry statements with no finite
  witness (automorphic representations, Newton polygons, Galois representations), and
  statements with undefined-in-snippet notation.

**B. Manual classification of the final 30 shipped entries** (this is the number I actually
trust):
- exact extremal value/formula at a specific n or in closed form (`ex(Q8,C4)=680`,
  `m(k,k)=(k^(k-1)+k-1)^2`, `mpd(P_m)=6`, the H(4,3) threshold=18, `f_2(k)=3k^2`, circular
  chromatic index formula, the cross-intersecting-3-graph bound=100): **7/30 (23%)**
- "no configuration of size n has property P" (the two Monochromatic-k-in-a-row entries,
  stated over a finite torus, exactly the mission's second bias bullet): **2/30 (7%)**
- "sequence a(n) satisfies R for all n" (Legendre-weakening sequence, mock-theta sign law,
  overpartition congruence): **3/30 (10%)**
- "every X in an enumerable class satisfies inequality Y" (chromatic/spectral/domination-style
  bounds — the D-coloring pair, Bollobás-Nikiforov, claw-free-cubic domination/packing,
  even-hole-free χ-bound, median eigenvalues, saturation-vs-harmonic-index, chi_2 planar
  coloring, the log-concavity/chromatic-polynomial-derivative sign conjecture, the
  depth-of-symbolic-power equality, dominating-set-sequence unimodality): **11/30 (37%)**
- "exists a construction/ordering for every n in an enumerable class" (Pilz's 1-2-3
  conjecture, the doubly-saturated-Ramsey circulant family, the min-modulus multiset-sum
  optimality claim, the recursive-quasigroup-code existence conjecture, Graham's
  rearrangement conjecture, and the two completely-independent-spanning-trees
  outerplanar-disc conjectures): **7/30 (23%)**

Net read: once you actually read the papers instead of keyword-matching, "no configuration
exists" statements are rare in practice (2/30) but the mission's other three bias bullets
(exact extremal value, sequence recurrence, universal inequality) are all well represented
and roughly balanced (23%/10%/37%), plus a large "existence of a construction for every n"
bucket (23%) that the original bias list didn't name explicitly but is just as
finite-witness-friendly as "no configuration exists" — a witness there is one explicit
construction, checkable directly, rather than a refuting counterexample.

## Calibration / honest caveats

- **The LLM-labeling pipeline is not fully trustworthy for "still open."** At least two
  entries I kept (`lit-combinatorics-cross-intersecting-mkk-formula`,
  `lit-numbertheory-pilz-1-2-3-conjecture`) are flagged in their own `notes` field as
  possibly already resolved in full or in large part by the very paper the conjecture was
  extracted from — the paper states the conjecture, then proves it for all sufficiently
  large parameters, and the LLM labeler apparently didn't always downgrade these to
  `not_real_conjecture`. I did not silently drop these (they're legitimate `id`s and I
  recorded exactly why residual doubt exists) but any triage agent should re-verify open
  status against the source PDF before spending an attack budget.
- **One 1998-era conjecture snuck in via a 2026 paper** —
  `lit-combinatorics-recursive-quasigroup-code-q14-q18` is Couselo-Gonzalez-Markov-Nechaev
  1998, not itself a 2021-2026 conjecture, but the *residual open cases* (q=14, q=18) are
  exactly current as of a 2026 paper that just resolved q=26, and each remaining case is
  its own small finite existence question — kept because the entry point (which cases are
  STILL open) is thoroughly current, unlike Wilf's conjecture in the discarded
  open-research-problems clone which is neither current nor still a live line of attack in
  what I found.
- **Half of everything I read closely got dropped**, mostly for imprecision risk (couldn't
  pin down paper-internal notation from the extracted snippet alone) rather than lack of
  interesting content — e.g. four Ramsey-number formulas from arXiv:2607.06817 (a genuinely
  great SAT-solver-friendly paper) were dropped solely because I could not confirm the exact
  meaning of `P^alt`, `S^sc`, `P^mon`, `C^mon` from the abstract/websearch alone. A follow-up
  agent with arXiv or HTML access to that one paper could very likely recover 4 more strong
  entries by fetching its Definitions section.
- No `model-knowledge-unverified` entries were needed; every entry traces to the clone.
