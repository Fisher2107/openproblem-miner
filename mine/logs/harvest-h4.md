# H4 harvest log — numerical bound tables (Class C seam)

Agent: H4. Resuming a run killed by rate limit partway through. Reused clones already
on disk at `mine/cache/h4_*` (mathbases, wiki, AutoRamsey, RamseyTheoryRL, r55research)
per instructions — **no re-cloning was done**. No prior output file existed; the JSONL
below was built from scratch.

Write scope respected: only `mine/corpus/raw/h4_bounds.jsonl`, `mine/cache/h4_*`
(read-only use), and this file were touched. No writes to `mine/verify/`,
`mine/results/`, `mine/attacks/`, `mine/corpus/problems.jsonl`, or any other cluster's
raw file. No git commit/push/checkout was run.

## What was read first

- `mine/corpus/SCHEMA.md` — the exact per-entry schema.
- `mine/logs/NETWORK.md` — confirms combinatorics.org, users.cecs.anu.edu.au (McKay),
  oeis.org, neilsloane.com, mathworld.wolfram.com, en.wikipedia.org, and
  www.openproblemgarden.org are all EGRESS_BLOCKED. These were **not** re-probed, per
  instructions that a previous agent already confirmed the blocks.

## What was actually in the pre-existing clones

- `mine/cache/h4_mathbases/_databases/small-ramsey.md` and `erichs-packing-center.md` are
  just YAML front-matter pointers to combinatorics.org / packomania — no numeric table
  content, so not directly citable for numbers.
- `mine/cache/h4_wiki/data/` turned out to be a general ~1400-page Wikipedia text-dump
  (leftover from an earlier cluster's harvest, not curated for this cluster's families).
  Of direct relevance: `Ramsey's_theorem.txt`. Its numeric R(r,s)-grid table (r,s<=10)
  did **not** survive the wikitext-to-text extraction (the table markup was dropped), so
  it could not be cited for the grid values — only the prose-embedded values (R(3,3)=6,
  R(4,4)=18, R(4,5)=25, and the R(5,5) in [43,48] sentence) survived as quotable text.
  No van der Waerden / Schur / Zarankiewicz / crossing-number / cage / kissing-number /
  Turán / Heilbronn / Costas / Sidon / hat-guessing / zero-forcing pages exist in this
  dump at all — it is simply the wrong corpus for those families.
- `mine/cache/h4_LinXueyuanStdio_AutoRamsey/your_target.md` **did** contain a genuinely
  useful hand-maintained Ramsey-number reference table (R(4,6)=36-40, R(5,6)=59-85,
  R(5,5)=43-48 as of that file's writing).
- `mine/cache/h4_arthaschan_r55research/docs/ADVISOR-MEETING-MATERIAL.md` contained a more
  recently updated table with R(5,5) at 43-46 (citing arXiv:2409.15709, Angeltveit &
  McKay 2024) and R(6,6) at 102-165, explicitly annotated by the repo's own author as
  "完全无望" (completely hopeless) for their GNN-filtered gluing method — a direct,
  first-party negative signal worth preserving.
- `mine/cache/h4_aLehav_RamseyTheoryRL` confirmed (via its own README) that R(4,6) and
  R(5,5) are its two active machine-search targets — useful as `prior_attempts` evidence,
  not as a source of new numbers.
- **Internal inconsistency flagged, not resolved**: `arthaschan/r55research`'s own
  `docs/DIRECTION-13-RESEARCH-PLAN.md` quotes R(4,6) as 35-41, while `your_target.md` in
  the *other* repo (and the same repo's own README-adjacent docs) says 36-40. Recorded
  in the corpus entry's `notes`, not silently resolved.

Given the clones covered only the Ramsey-number family, **15 WebSearch queries** were
used to cover the other requested families (van der Waerden, Schur/weak Schur,
Zarankiewicz, crossing numbers, cages, kissing numbers, Turán density, hat-guessing,
Costas arrays). Every websearch-sourced entry's `notes` field carries the literal
synthesized-answer text the tool returned, since that text is what actually contained the
quotable numbers (the underlying arXiv/journal PDFs themselves are on blocked or
unfetchable hosts — arxiv.org is EGRESS_BLOCKED per NETWORK.md, so the WebSearch tool's
own returned text is the only quotable artifact, not a page WebFetch could re-read).
Sidon/B_h[g] sets and zero-forcing numbers were searched but **no query surfaced a clean
current-record numeric pair** (only asymptotic growth-rate results) — these two families
were dropped rather than forcing weak entries. Heilbronn's triangle problem was also
dropped for the same reason: its current record is a gap between two *growth exponents*
(Ω(1/n²) vs O(n^{-8/7-1/2000})), not a lower/upper pair of a single quantity, and forcing
it into `current_bounds:{lower,upper}` would have manufactured a false-precision number.

## Result

**19 entries**, all valid JSONL (verified with the required `python3 -c "import json; ..."`
check), no duplicate ids.

By provenance:
| provenance type | count |
|---|---|
| `clone:...` | 4 |
| `websearch:...` | 15 |
| `model-knowledge-unverified` | 0 |

The 4 clone-backed entries (all Ramsey numbers, all from repos already on disk) are the
strongest-grounded in the file. The 15 websearch entries are grounded in the WebSearch
tool's returned synthesized text (which itself cites and quotes its source papers) rather
than a page this agent could refetch and re-quote directly, since the underlying arXiv/
journal hosts are blocked — this is a real, structurally-forced weaker link than the
clone entries, and is called out per-entry in `notes` and again here rather than papered
over.

## Ranked-by-smallest-witness table

"Smallest witness" = the estimated bit-size (or equivalent) of the single finite object
that would improve the record by one, as derived in each entry's `notes` field. Kissing
numbers (continuous sphere-packing configurations) and the Turán density (an asymptotic
construction family, not a finite object at all) are not bit-comparable to the rest and
are listed at the bottom, unranked, rather than force-fit into the ordering.

| rank | id | witness size (est.) | 4-core nauty+z3+SAT, ~1hr: plausible? |
|---|---|---|---|
| 1 | `bound-costas-N32` | ~118 bits (a permutation of 32) | **No.** Tiny witness, but the 32! search space has already been hit hard by Costas-specific algorithms (Welch/Lempel/Golomb + dedicated exhaustive/heuristic search per Drakakis's survey); a generic 1hr/4-core job won't out-search purpose-built tools that already failed here. |
| 2 | `bound-cr-K13` | ~460 bits (a 13-vertex rotation system) | **No.** Needs specialized "good drawing" enumeration/realizability tooling, not a generic SAT/nauty pipeline; a decade of dedicated papers only narrowed it to 2 candidate values. |
| 3 | `bound-ramsey-R4-6` | 630 bits (36-vertex adjacency) | **No.** Already the explicit, dedicated target of two ML/RL search projects in this very cluster (RamseyTheoryRL, AutoRamsey-adjacent work) with no success; a generic tool is unlikely to beat purpose-built loops that ran far longer. |
| 4 | `bound-ramsey-R5-5` | 903 bits (43-vertex adjacency) | **No, decisively.** The 2024 record needed ~80 CPU-years; this is the most heavily-mined target in the whole cluster (see `prior_attempts`). |
| 5 | `bound-zarankiewicz-z32` | ~1024 bits (32x32 biadjacency matrix) | **No, but closest call among the "hard" ones.** Literature already frames this exact problem as SAT-native (a paper titled "An attack on Zarankiewicz's problem through SAT solving" surfaced in search); witness is cleanly poly-checkable. But Afzaly-McKay already spent serious dedicated compute reaching exactly this frontier without cracking it, so a generic 1hr/4-core run is unlikely to finish the job outright, though it is the best candidate here for a SAT encoding to make *partial* progress. |
| 6 | `bound-vdw-W4-4` | ~1049 bits (a length-1049 2-colouring) | **Maybe / best true candidate for a full "yes."** Van der Waerden lower-bound search is a mature, well-documented SAT-friendly domain (many papers report single-machine, hours-scale improvements of exactly this kind); extending the known 1048-length witness by a SAT/local-search restart is plausible in an hour on 4 cores. |
| 7 | `bound-schur-S6` | ~1388 bits (a 537-length 6-colouring) | **Maybe.** Same SAT-native family as Heule's S(5) proof, but S(6) is known to be dramatically harder; a from-536 local-search restart might buy one more integer, might not. |
| 8 | `bound-weakschur-WS6` | ~1673 bits | **Maybe, lower confidence than S(6).** Already had a dedicated 2022 improvement, so the cheap gains may already be taken. |
| 9 | `bound-ramsey-R5-6` | 1711 bits (59-vertex adjacency) | **No.** Larger vertex count than R(4,6), which itself already resisted dedicated search; no reason a generic tool succeeds here where it hasn't on the easier case. |
| 10 | `bound-hatguess-K44` | ~2048 bits (a strategy table over 8 vertices) | **Yes — most confident "yes" on this list.** The state space (8 vertices, tiny alphabet) is genuinely small and is exactly the kind of discrete combinatorial game a SAT/CSP encoding handles well; settling HG(K4,4) in {3,4,5} is plausible within an hour on 4 cores. |
| 11 | `bound-ramsey-R3333` | 2550 bits (51-vertex 4-colouring) | **Maybe — the other real "sleeper" candidate.** This record has stood since the 1970s, i.e. pre-dates modern SAT solvers entirely; a fresh SAT/nauty attempt genuinely might not have been tried on this specific target since. |
| 12 | `bound-ramsey-R6-6` | 5151 bits (102-vertex adjacency) | **No, decisively.** The source repo itself labels this "completely hopeless" for its own (more sophisticated, GNN-assisted) tooling. |
| 13 | `bound-cage-k3g14` | ~9600 bits (a ~380-vertex cubic graph) | **No.** Needs specialized cage-construction machinery (voltage-graph lifts, algebraic methods), not generic nauty+SAT. |
| 14 | `bound-ramsey-R444` | ~12880 bits (128-vertex 3-colouring) | **No.** Even the 2026 upper-bound paper needed novel dedicated recursive techniques, not brute force; the search space here dwarfs everything else on this list. |
| — | `bound-kissing-d9` .. `d12` | not bit-comparable (continuous sphere configurations) | **No.** Requires SDP/LP optimization (Cohn-Elkies-style machinery) or lattice theory, categorically outside the given nauty/SAT/discrete toolkit. |
| — | `bound-turan-k4-3uniform` | not a finite object (asymptotic construction family) | **No.** Requires flag-algebra SDP computation; wrong tool class entirely, and the quantity itself isn't a finite witness. |

**Honest bottom line for a prospective attack wave**: only `bound-hatguess-K44` earns a
real "yes," with `bound-vdw-W4-4` and `bound-ramsey-R3333` as the two "maybe, worth a
try" picks (one because the domain is SAT-native and mature, the other because the
record predates SAT solvers entirely). Everything else on this list has already
absorbed more dedicated compute/expertise than a 4-core/1-hour generic run can plausibly
beat, and the kissing-number and Turán-density entries are the wrong *type* of problem
for the given toolkit regardless of compute.

## Regeneration

```
python3 -c "import json; [json.loads(l) for l in open('mine/corpus/raw/h4_bounds.jsonl')]"
```

The entries were generated by a one-off script (not checked in, per write-scope) that
combined the pre-existing clone greps above with 15 WebSearch queries; see this log's
"What was actually in the pre-existing clones" section for the exact clone paths/lines,
and each entry's own `provenance` field for the corresponding query/URL.
