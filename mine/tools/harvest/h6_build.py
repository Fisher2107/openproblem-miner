#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds mine/corpus/raw/h6_literature.jsonl from clone:davisrbr/conjectures-arxiv
(and manual dedupe against h2_formal.jsonl, which we checked separately).

Provenance base for every entry pulled from the conjectures-arxiv clone:
  clone:davisrbr/conjectures-arxiv@d2e3afe62098611fabd7236998acc73f64e4b3b7:
    data/exports_month_live_20260712/real_conjectures_gpt-5-mini.jsonl#conjecture_id=<id>
  (cross-referenced against data/exports_month_live_20260712/conjectures.jsonl#id=<id>
   for the LaTeX body_tex / arxiv metadata, same commit)
"""
import json

PROV_BASE = "clone:davisrbr/conjectures-arxiv@d2e3afe62098611fabd7236998acc73f64e4b3b7:data/exports_month_live_20260712/"

def prov(cid):
    return (f"{PROV_BASE}real_conjectures_gpt-5-mini.jsonl#conjecture_id={cid} "
            f"(cross-ref {PROV_BASE}conjectures.jsonl#id={cid})")

entries = []

def add(**kw):
    entries.append(kw)

# 1 -----------------------------------------------------------------
add(
 id="lit-combinatorics-mono-k-row-exactly2",
 source="arXiv:2606.12880 (Monochromatic k in a row)",
 url="http://arxiv.org/abs/2606.12880v1",
 provenance=prov(3820),
 statement_nl=(
  "Fix an integer k that is a positive multiple of 3, and work on the k x k discrete "
  "torus (Z/kZ)^2. A 'line' is either an axis-parallel line (a full row {(x,y0): x in Z/kZ} "
  "for fixed y0, or a full column {(x0,y): y in Z/kZ} for fixed x0) or a diagonal line "
  "(a full diagonal {(x, x+c) mod k : x in Z/kZ} or anti-diagonal {(x, c-x) mod k : x in Z/kZ} "
  "for fixed c in Z/kZ); there are 4k such lines in total, each of size k. "
  "Conjecture: for every k in 3*N, there is no subset A of (Z/kZ)^2 such that every one of "
  "these 4k lines meets A in exactly 2 points."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-no-finite-object",
 witness_type="finite-object",
 witness_check_cost="cheap (fixed k: brute-force/SAT search over subsets of a k^2-point torus, or an ILP with 4k exact-count constraints)",
 known_cases=None,
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=(
  "Paper states this as a restatement of the general Z^2 density conjecture D(k,Z^2); the "
  "paper proves D(k,Z^2)=1-2/k whenever 3 does not divide k and determines D(3,Z^2), d(3,Z^2) "
  "exactly, so k divisible by 3 is exactly the residual open family. No exhaustive computer "
  "search for a counterexample is claimed in the abstract; websearch turned up no independent "
  "verification (query: not run, budget spent on higher-priority checks)."
 ),
 notes=(
  "Self-contained reformulation of Conjecture D(k,Z^2) restricted to k in 3N, taken verbatim "
  "from the paper's own \\ref{conj:D(k,Z2)} restatement. Finite per fixed k, ideal SAT/ILP target: "
  "increase k and search for a 2-regular-on-every-line subset. Companion to lit-combinatorics-mono-k-row-atleast2 "
  "(same paper, relaxed inequality version with a size cap)."
 ),
)

# 2 -----------------------------------------------------------------
add(
 id="lit-combinatorics-mono-k-row-atleast2",
 source="arXiv:2606.12880 (Monochromatic k in a row)",
 url="http://arxiv.org/abs/2606.12880v1",
 provenance=prov(3821),
 statement_nl=(
  "Same setup as lit-combinatorics-mono-k-row-exactly2 (k a positive multiple of 3, the 4k "
  "axis-parallel and diagonal lines of the k x k torus (Z/kZ)^2). Conjecture: for every such k, "
  "there is no subset A of (Z/kZ)^2 with |A| <= 2k+2 such that every line meets A in at least 2 points."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-no-finite-object",
 witness_type="finite-object",
 witness_check_cost="cheap (|A|<=2k+2 bounds the search space directly; brute-force/SAT over subsets up to size 2k+2 of a k^2-point torus)",
 known_cases=None,
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="Same paper/section as lit-combinatorics-mono-k-row-exactly2; no independent computer search found.",
 notes=(
  "Explicit size bound (|A|<=2k+2) makes this the more tractable of the pair: a witness is a "
  "small, explicitly bounded subset, so SAT/ILP encodings scale far better than for the unbounded "
  "'exactly 2' version. \\ref{conj:ult} in the source."
 ),
)

# 3 -----------------------------------------------------------------
add(
 id="lit-combinatorics-cross-intersecting-3graphs-100",
 source="arXiv:2606.01817 (On the product of cross-intersecting families with maximal covering number)",
 url="http://arxiv.org/abs/2606.01817v1",
 provenance=prov(4199),
 statement_nl=(
  "A k-graph on a ground set V is a family of k-element subsets of V. Two families F (a k-graph) "
  "and G (an l-graph) are cross-intersecting if A cap B != empty-set for every A in F and B in G. "
  "The covering number tau(F) is the minimum size of a set S subset V that meets every member of F. "
  "Conjecture: suppose F and G are cross-intersecting 3-graphs (3-uniform hypergraphs, ground set "
  "size unrestricted) with tau(F) = tau(G) = 3, and suppose F and G share no common edge (F cap G "
  "= empty-set, as families). Then the maximum possible value of |F| * |G| over all such pairs is exactly 100."
 ),
 statement_formal=None,
 quantifier_shape="exists-construction-plus-upper-bound",
 witness_type="finite-object",
 witness_check_cost=(
  "moderate: a witness against the upper bound is one explicit pair (F,G) with |F|*|G|>100 and the "
  "stated properties (finite, checkable by brute force once a ground-set-size bound is fixed, but "
  "covering-number/cross-intersection checks over 3-graphs blow up combinatorially -- flag as "
  "potentially expensive for anything beyond small ground sets)"
 ),
 known_cases="Same paper proves (unrestricted, i.e. without F∩G=∅) that m(3,3)=|F||G|_max=121 (their Th. 1.7); this entry's F∩G=∅ variant with value 100 is a distinct, apparently still-open sub-claim.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="None found; this is a brand-new (2026) problem. Recommend fetching the full paper text (source blocked here) to confirm which direction (existence of a matching construction, or the upper bound) is the open part.",
 notes="Precise combinatorial definitions given in the paper's own abstract (k-graph, cross-intersecting, covering number tau), so this is fully self-contained modulo confirming ground-set-size is genuinely unbounded in the extremal problem.",
)

# 4 -----------------------------------------------------------------
add(
 id="lit-combinatorics-cross-intersecting-mkk-formula",
 source="arXiv:2606.01817 (On the product of cross-intersecting families with maximal covering number)",
 url="http://arxiv.org/abs/2606.01817v1",
 provenance=prov(4198),
 statement_nl=(
  "With m(k,l) as defined in lit-combinatorics-cross-intersecting-3graphs-100 (the maximum of "
  "|F||G| over cross-intersecting pairs where F is a k-graph with covering number l and G is an "
  "l-graph with covering number k): conjecture that for all integers k >= 2, m(k,k) = (k^(k-1) + k - 1)^2."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-exact-value",
 witness_type="finite-object",
 witness_check_cost="moderate for small k (search for a cross-intersecting pair beating the claimed value), grows fast with k",
 known_cases="Paper's own Th. 1.6 proves this for all k > k0 (threshold k0 not given in the extracted snippet) and Th. 1.7 proves m(3,3)=121, matching the formula at k=3.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes=(
  "CAUTION -- likely already (mostly) resolved in the source paper itself: the abstract says the "
  "exact value is established for k>k0 and separately for k=3, so any genuinely open residual is at "
  "most a small finite window of k (possibly just k=2, or k in [4,k0)). This entry is included for "
  "completeness/audit but the labeling pipeline may have mis-tagged an already-proved theorem as an "
  "open conjecture. Do not attack without first fetching the full paper to pin the exact value of k0 "
  "and confirm which k, if any, remain unproved."
 ),
)

# 5 -----------------------------------------------------------------
add(
 id="lit-combinatorics-multiset-partition-dim-prism",
 source="arXiv:2607.07407 (Multiset Partition Dimension of Graphs)",
 url="http://arxiv.org/abs/2607.07407v1",
 provenance=prov(4479),
 statement_nl=(
  "For a graph G and a vertex v, and an ordered partition Pi = {S_1,...,S_t} of V(G), the multiset "
  "distance vector of v with respect to Pi is the multiset r(v|Pi) = { d(v,x) : x in S_i, for each i }, "
  "i.e. for each part S_i we record the multiset of distances from v to every vertex of S_i (not just "
  "the minimum distance, unlike the classical partition dimension). Pi is a multiset resolving "
  "partition if the vectors r(v|Pi) are pairwise distinct over all v in V(G). The multiset partition "
  "dimension mpd(G) is the minimum number of parts in such a partition. Let P_m be the prism graph on "
  "2m vertices (the Cartesian product of a cycle C_m with an edge K_2, i.e. two disjoint m-cycles with "
  "corresponding vertices joined by a 'rung' edge). Conjecture: for every m >= 8, mpd(P_m) = 6."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-exact-value",
 witness_type="finite-object",
 witness_check_cost="cheap: for a fixed m, P_m has 2m vertices; brute-force or ILP search over partitions into 5 parts (to refute) or exhibit a valid 6-part partition (to confirm) is fully mechanical",
 known_cases=None,
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="Very clean finite-witness target: refute by finding some m>=8 with mpd(P_m)!=6 (either a 5-part multiset resolving partition, refuting mpd<=5 is impossible under the conjecture, or showing 6 parts is insufficient). Multiset partition dimension is a brand-new (this same paper's) invariant -- definition reconstructed carefully from the abstract; verify against the paper's Definition 1.x before committing a checker.",
)

# 6 -----------------------------------------------------------------
add(
 id="lit-combinatorics-ex-q8-c4",
 source="arXiv:2603.29127 (New Lower Bounds for C4-Free Subgraphs of the Hypercubes Q6, Q7, and Q8)",
 url="http://arxiv.org/abs/2603.29127v2",
 provenance=prov(1386),
 statement_nl=(
  "Let Q_8 be the 8-dimensional hypercube graph (vertex set {0,1}^8, edges between strings "
  "differing in exactly one coordinate; 256 vertices, 1024 edges). Let ex(Q_8, C_4) denote the "
  "maximum number of edges in a subgraph of Q_8 that contains no 4-cycle (C_4) as a subgraph. "
  "Conjecture: ex(Q_8, C_4) = 680."
 ),
 statement_formal=None,
 quantifier_shape="exact-value-single-instance",
 witness_type="finite-object",
 witness_check_cost=(
  "expensive: Q_8 has 1024 edges, so an exhaustive certificate that no 681-edge C4-free subgraph "
  "exists is an ILP/SAT search over a huge space; the paper itself only reports 1076 independent "
  "simulated-annealing searches failing to find 681 edges, not a proof -- flag as NP-hard-flavored "
  "(Zarankiewicz-type extremal subgraph problem)"
 ),
 known_cases="ex(Q_8,C4)>=680 is proved (explicit 680-edge construction, certified by exhaustive enumeration of all 1792 four-cycles of Q_8); ex(Q_6,C4)=132 is fully settled by ILP.",
 current_bounds={"lower": 680, "upper": None},
 class_=None,
 tractability=None,
 prior_attempts=(
  "Paper already ran a two-phase simulated-annealing search with Aut(Q_8)-based diversification "
  "and an ILP formulation (used successfully to close Q_6); 1076 independent runs at 681 edges never "
  "achieved zero C4 violations. This is a real, reported negative computational signal for a "
  "counterexample (i.e. finding 681+ edges), which raises confidence in the lower bound being tight "
  "but is not a proof of the matching upper bound."
 ),
 notes="Code/data at https://github.com/minamominamoto/c4free-hypercube (per abstract) -- worth cloning directly for a warm start rather than re-deriving from scratch. Attacking the upper bound (proving <=680) via SAT/ILP is the natural next step given the authors' own tooling.",
)

# 7 -----------------------------------------------------------------
add(
 id="lit-numbertheory-pilz-1-2-3-conjecture",
 source="arXiv:2607.00934 (On the Extended 1-2-3 Conjecture of Pilz)",
 url="http://arxiv.org/abs/2607.00934v1",
 provenance=prov(4736),
 statement_nl=(
  "For a finite set A of positive integers and a positive integer c, write c*A = {c*a : a in A}. "
  "For finite A subset N and n in N, let A Delta (2*A) Delta ... Delta (n*A) denote the iterated "
  "symmetric difference of the n sets A, 2*A, 3*A, ..., n*A (X Delta Y = (X\\Y) union (Y\\X)). "
  "Pilz's conjecture: for every finite A subset N and every n in N, |A Delta (2*A) Delta ... Delta (n*A)| >= n."
 ),
 statement_formal=None,
 quantifier_shape="forall-finite-sets-and-integers",
 witness_type="finite-object",
 witness_check_cost="cheap for a fixed candidate (A,n): the symmetric difference and its cardinality are computed directly; the hard part is the unbounded search over all finite A for each n",
 known_cases="Known true when A={1,...,k}; proved for all sufficiently large n by this very paper (2026); the 2024 paper arXiv:2409.15075 already gave a sumset-version partial result.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="Websearch (query: 'Pilz conjecture symmetric difference A Δ 2A Δ nA cardinality n') confirms this paper resolves the conjecture 'for all sufficiently large n' -- meaning small n (below whatever threshold the paper proves) is the genuinely open residual and the natural attack target.",
 notes="A counterexample would be a specific small finite A and small n with |A Δ 2A Δ ... Δ nA| < n -- fully finite, brute-force checkable per (A,n) pair once a search bound on |A| and max element of A is fixed (heuristic, not exhaustive, unless a structural bound on minimal counterexamples is derived).",
)

# 8 -----------------------------------------------------------------
add(
 id="lit-combinatorics-doubly-saturated-r3t-circulant",
 source="arXiv:2604.21187 (Doubly Saturated Ramsey Graphs: A Case Study in Computer-Assisted Mathematical Discovery)",
 url="http://arxiv.org/abs/2604.21187v1",
 provenance=prov(1939),
 statement_nl=(
  "A graph G is R(3,t)-good if it contains neither a triangle (K_3) nor an independent set of size "
  "t. G is doubly saturated (with respect to this property) if adding any missing edge creates a "
  "triangle or removing any existing edge creates an independent set of size t (i.e. G is edge-"
  "maximal and edge-minimal simultaneously for the R(3,t)-good property). For a positive integer t "
  "and a set of distances D subset {1,...,floor(n/2)}, the circulant graph on n vertices {0,...,n-1} "
  "with distance set D has an edge between i and j iff |i-j| mod n is in D or n - (|i-j| mod n) is in D. "
  "Conjecture: for every odd t >= 17, the circulant graph on 5t-10 vertices with distance set "
  "[t-4,t-3] union [t+1, (3t-9)/2] union {(3t-5)/2} union {2t-4} is doubly saturated R(3,t)-good."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-explicit-construction",
 witness_type="finite-object",
 witness_check_cost=(
  "NP-hard-flavored in general (checking 'no clique of size 3, no independent set of size t' and "
  "edge-(maximal+minimal)-ness is a clique/independent-set decision problem) but the graph is an "
  "explicit circulant on only 5t-10 vertices, so for any fixed t this is a concrete, finite, "
  "fully-automatable SAT/direct check (the paper itself already uses SAT solving for this family)"
 ),
 known_cases="Paper answers a 1982 question of Grinstead and Roberts by exhibiting this family via SAT-solving plus LLM-generated code, and reports Lean-formalized correctness proofs for some cases.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="The source paper is itself SAT-solver-driven and reports Lean formalization attempts for parts of the construction -- strong signal of active machine verification already underway; check the paper's own Lean artifacts before re-deriving a checker from scratch.",
 notes="If a genuinely 'open' residual remains here (rather than fully proved for all odd t>=17 in-paper), it is likely restricted to small odd t just above 17 where the SAT solver time out; needs the full paper to confirm the exact open range.",
)

# 9 -----------------------------------------------------------------
add(
 id="lit-numbertheory-legendre-weakening-sequence",
 source="arXiv:2602.22502 (Weakening the Legendre Conjecture)",
 url="http://arxiv.org/abs/2602.22502v1",
 provenance=prov(138),
 statement_nl=(
  "Define the sequence of primes q_1, q_2, q_3, ... by q_1 = 2, and for n >= 1, let q_(n+1) be the "
  "least prime strictly exceeding q_n^2. Conjecture: q_(n+1) < (q_n + 1)^2 for all n >= 1."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-sequence",
 witness_type="numeric-bound",
 witness_check_cost="cheap for small n (standard primality testing / prime-finding, e.g. sympy.nextprime), but q_n grows doubly-exponentially so only the first handful of n are feasible before the search for 'the least prime exceeding q_n^2' becomes astronomically expensive",
 known_cases="Distinct from (but motivated by) the classical Legendre conjecture (a prime between every n^2 and (n+1)^2), which is already tracked in this mine's corpus via mine/corpus/raw/h2_formal.jsonl (fc-wikipedia-LegendreConjecture). This is a self-referential sequence variant, not a duplicate.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="None found beyond the source paper; this is closely related to Mills' prime-representing-constant literature (paper explicitly applies its results to Mills-type constants), which has a long history of computational study of nearby sequences.",
 notes="A counterexample is a single n with q_(n+1) >= (q_n+1)^2 -- purely a finite arithmetic check once q_n is computed, so the whole entry is exactly the 'sequence a(n) satisfies R for all n' shape the mission prioritizes, limited in practice only by how many terms of q_n are computationally reachable.",
)

# 10 -----------------------------------------------------------------
add(
 id="lit-combinatorics-d-coloring-general-bound",
 source="arXiv:2606.06831 (Proper edge coloring with rainbow diamonds)",
 url="http://arxiv.org/abs/2606.06831v1",
 provenance=prov(4045),
 statement_nl=(
  "A diamond is the graph K_4 minus one edge (two triangles sharing an edge, 4 vertices, 5 edges). "
  "For a graph G, a D-coloring is a proper edge coloring of G (adjacent edges get different colors) "
  "such that every diamond subgraph of G is rainbow (its 5 edges all receive distinct colors). The "
  "D-chromatic index chi'_D(G) is the minimum number of colors used by a D-coloring of G. Let Delta "
  "be the maximum degree of G. Conjecture: for every graph G, chi'_D(G) <= (1/2)*Delta^2 + (1/2)*Delta."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-bound",
 witness_type="finite-object",
 witness_check_cost="moderate: computing chi'_D(G) exactly is an NP-hard-flavored coloring problem in general (generalizes edge coloring), but is brute-forceable / SAT-encodable for small graphs and small Delta",
 known_cases="Paper proves the weaker chi'_D(G) <= (9/16)*Delta^2 + (1/2)*Delta unconditionally, and verifies this conjectured tighter bound by hand for Delta <= 5.",
 current_bounds={"lower": None, "upper": "(9/16)*Delta^2 + (1/2)*Delta (proved)"},
 class_=None,
 tractability=None,
 prior_attempts="Authors verified Delta<=5 by hand (not stated as exhaustive computer search); Delta>=6 is open.",
 notes="A counterexample is any graph G (search small Delta=6,7,... first, since Delta<=5 already checked) with chi'_D(G) exceeding Delta^2/2+Delta/2 -- a finite SAT/ILP edge-coloring search per candidate G. See also the companion planar-graph-restricted conjecture lit-combinatorics-d-coloring-planar-bound from the same paper.",
)

# 11 -----------------------------------------------------------------
add(
 id="lit-combinatorics-d-coloring-planar-bound",
 source="arXiv:2606.06831 (Proper edge coloring with rainbow diamonds)",
 url="http://arxiv.org/abs/2606.06831v1",
 provenance=prov(4046),
 statement_nl=(
  "Using the D-coloring / D-chromatic index chi'_D(G) defined in lit-combinatorics-d-coloring-general-bound "
  "(minimum colors in a proper edge coloring making every diamond, i.e. K_4-minus-an-edge subgraph, rainbow): "
  "conjecture that for every planar graph G with maximum degree Delta >= 4, "
  "chi'_D(G) <= 9 if Delta=4; chi'_D(G) <= 10 if Delta=5; chi'_D(G) <= 2*Delta-1 if Delta >= 6."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-bound-caselist",
 witness_type="finite-object",
 witness_check_cost="moderate: planar-graph generation (e.g. via plantri) plus a SAT/ILP D-coloring check per candidate is fully automatable for small vertex counts",
 known_cases=None,
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="Sharper, planar-restricted companion to lit-combinatorics-d-coloring-general-bound; the explicit small-Delta case split (9, 10, 2Delta-1) is unusually attack-friendly because each case gives a concrete integer target to try to beat with a planar counterexample generated by plantri/nauty.",
)

# 12 -----------------------------------------------------------------
add(
 id="lit-combinatorics-h43-spectral-threshold-18",
 source="arXiv:2604.19854 (Improving the Even-Size Threshold in Spectral Extrema for H(4,3)-Free Graphs)",
 url="http://arxiv.org/abs/2604.19854v1",
 provenance=prov(1966),
 statement_nl=(
  "For a graph G, let rho(G) denote its spectral radius (the largest eigenvalue of its adjacency "
  "matrix), and let e(G) = m be its number of edges. The 'fish graph' H(4,3) is the small graph "
  "formed by gluing a 4-cycle and a triangle along a shared edge (per the paper's terminology for "
  "the Brualdi-Hoffman-Turan problem; verify the exact 5-vertex structure against the source before "
  "use). For even m, let rho'(m) be the largest root of x^4 - m*x^2 - (m-2)*x + m/2 - 1 = 0. It is a "
  "known theorem (Zheng-Zhang) that every H(4,3)-free graph of even size m >= 38 without isolated "
  "vertices satisfies rho(G) <= rho'(m). This paper lowers the unconditional threshold to m>=24, and "
  "exhibits an explicit obstruction family showing no theorem of this form can hold for m < 18. "
  "Conjecture: the sharp threshold is exactly m = 18, i.e. every H(4,3)-free graph of even size m >= 18 "
  "without isolated vertices satisfies rho(G) <= rho'(m)."
 ),
 statement_formal=None,
 quantifier_shape="exact-threshold-value",
 witness_type="finite-object",
 witness_check_cost="cheap once graphs of a given (small, even) edge count m are enumerated (e.g. via nauty/geng with a fixed edge count) and rho(G) computed by standard linear algebra -- fully mechanical for the residual m in {18,20,22}",
 known_cases="Proved for m>=24; proved impossible to extend below 18 (explicit obstruction family); the paper 'records computational evidence' that 18 is exactly right but does not close m in {18,20,22}.",
 current_bounds={"lower": 18, "upper": 24},
 class_=None,
 tractability=None,
 prior_attempts="Paper already reports computational evidence supporting m=18 exactly -- worth requesting/reproducing their computation before an independent search.",
 notes="Extremely narrow residual gap (only 3 even values of m need checking: 18, 20, 22), making this one of the most immediately attackable entries in this batch -- exhaustively enumerate H(4,3)-free graphs of each of these edge counts (bounded search since 'without isolated vertices' and a fixed small edge count strongly bounds vertex count) and compare rho(G) to rho'(m).",
)

# 13 -----------------------------------------------------------------
add(
 id="lit-combinatorics-claw-free-cubic-domination-packing",
 source="arXiv:2606.29199 (Improved Domination-Packing Bounds in Claw-Free Cubic Graphs and Unit Disk Graphs)",
 url="http://arxiv.org/abs/2606.29199v1",
 provenance=prov(4867),
 statement_nl=(
  "For a graph G, the domination number gamma(G) is the minimum size of a dominating set (a set S "
  "such that every vertex not in S has a neighbor in S). The packing number rho(G) is the maximum "
  "size of a set of vertices that are pairwise at distance at least 3. G is claw-free if it has no "
  "induced K_{1,3}; G is cubic if every vertex has degree exactly 3; G is bridgeless if it has no "
  "cut-edge. Conjecture: for every bridgeless claw-free cubic graph G, gamma(G) <= (5/4) * rho(G)."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-bound",
 witness_type="finite-object",
 witness_check_cost="expensive per candidate (both gamma(G) and rho(G) are NP-hard to compute exactly in general) but perfectly tractable for small cubic graphs via ILP/exhaustive search, and cubic graphs are efficiently enumerable with nauty/geng --connected --degree constraints",
 known_cases="Paper proves the weaker gamma(G) <= (7/4)*rho(G) + 5/6 unconditionally for this class, and exhibits an infinite family with gamma(G) = (5/4)*rho(G) exactly (showing 5/4 would be tight if true).",
 current_bounds={"lower": None, "upper": "(7/4)*rho(G) + 5/6 (proved)"},
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="Tightness example already known (ratio exactly 5/4 is attained), which is a strong prior signal that the bound, if true, is sharp -- a natural next step for an attack agent is to nauty-enumerate small bridgeless claw-free cubic graphs and check the ratio never exceeds 5/4.",
)

# 14 -----------------------------------------------------------------
add(
 id="lit-combinatorics-bollobas-nikiforov-k4free",
 source="arXiv:2603.26379 (The Bollobás-Nikiforov Conjecture for Complete Multipartite Graphs and Dense K4-Free Graphs)",
 url="http://arxiv.org/abs/2603.26379v1",
 provenance=prov(1496),
 statement_nl=(
  "For a graph G with adjacency eigenvalues lambda_1(G) >= lambda_2(G) >= ... and m edges: the "
  "Bollobas-Nikiforov conjecture (general form) asserts lambda_1(G)^2 + lambda_2(G)^2 <= 2*(1 - "
  "1/omega(G))*m for every G != K_n, where omega(G) is the clique number. Specializing to K_4-free "
  "graphs (omega(G) <= 3, so the right-hand side becomes 2*(2/3)*m = 4m/3): conjecture that for "
  "every K_4-free graph G with G != K_3, lambda_1(G)^2 + lambda_2(G)^2 <= 4*m/3."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-bound",
 witness_type="finite-object",
 witness_check_cost="cheap: lambda_1, lambda_2 and m are all computable in polynomial time for any concrete graph (standard linear algebra), so this is one of the least computationally expensive witnesses in the batch",
 known_cases="Verified for triangle-free graphs (Lin-Ning-Wu) and for regular graphs (Zhang); this paper proves it for all complete multipartite graphs and (via a stability result) for K4-free graphs with m = Omega(n^2) as n -> infinity; the general K4-free case with alpha(G) >= n/3 is explicitly flagged by the authors as the remaining obstruction to a Hoffman-bound approach.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="Websearch (query: 'Bollobás–Nikiforov conjecture counterexample computer search small graphs') found no reported counterexample search; all located results are partial-proof papers, not refutation attempts -- genuinely fresh territory for an exhaustive small-graph check.",
 notes="Extremely cheap per-graph check makes this an excellent target for a brute-force sweep over all K4-free graphs up to some vertex count via nauty/geng, computing the top two adjacency eigenvalues and comparing to 4m/3.",
)

# 15 -----------------------------------------------------------------
add(
 id="lit-combinatorics-min-modulus-multiset-sum",
 source="arXiv:2607.08366 (Minimum modulus for the unique multiset-sum problem)",
 url="http://arxiv.org/abs/2607.08366v1",
 provenance=prov(4435),
 statement_nl=(
  "Fix an integer n >= 2. A set A = {a_0 < a_1 < ... < a_(n-1)} of n distinct residues in Z_N is "
  "'valid mod N' if the all-ones multiset {a_0,...,a_(n-1)} (each element taken once) is the only "
  "size-n multiset drawn (with repetition allowed) from A whose elements sum to p := sum_i a_i "
  "(mod N). The paper proves that for the super-increasing set A = {2^k - 1 : 0 <= k <= n-1}, the "
  "least N for which A is valid mod N is exactly N_min(n) = 2^n - 2^floor(log2 n). Conjecture: for "
  "every n >= 2 and every N < 2^n - 2^floor(log2 n), no set of n residues (not just the super-"
  "increasing one) is valid mod N -- i.e. the super-increasing set attains the least valid modulus "
  "over all size-n sets."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-no-smaller-example",
 witness_type="finite-object",
 witness_check_cost=(
  "moderate: for fixed n and N, checking whether ANY size-n subset of Z_N is valid mod N requires "
  "searching over all C(N,n) candidate sets and, for each, all multisets of size n summing to the "
  "right residue -- exponential in the worst case but fully finite and exhaustively checkable for "
  "small n, N"
 ),
 known_cases="The super-increasing-set direction (N_min(n)=2^n-2^floor(log2 n) achieved by that specific set) is proved and machine-checked in Lean 4/Mathlib for all n (https://github.com/jarfo/min-modulus per the paper). Only the 'no set does better' universal claim is conjectural.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="The matching achievability direction is already Lean-verified (strong existing formalization to build on); no claim of an exhaustive search over ALL size-n sets for the optimality direction.",
 notes="A counterexample is a triple (n, N, A) with N < 2^n-2^floor(log2 n) and A a valid-mod-N set of size n -- fully finite per (n,N), and n can be kept very small (n=2,3,4,...) for a first brute-force sweep. The existing Lean repo is a strong scaffold to extend rather than starting a checker from scratch.",
)

# 16 -----------------------------------------------------------------
add(
 id="lit-numbertheory-mock-theta-rho-sign-law",
 source="arXiv:2606.27902 (Sign law for Ramanujan's third order mock theta function rho(q))",
 url="http://arxiv.org/abs/2606.27902v1",
 provenance=prov(4213),
 statement_nl=(
  "Ramanujan's third-order mock theta function rho(q) is defined by the series "
  "rho(q) = sum_{m>=0} q^(2m(m+1)) / [(1+q+q^2)(1+q^3+q^6)...(1+q^(2m+1)+q^(4m+2))] "
  "= sum_{n>=0} r(n) q^n (this defines the integer coefficients r(n)). Conjecture: the strict sign "
  "law r(n) > 0 when n = 0 (mod 3), and r(n) < 0 when n = 1 or 2 (mod 3), holds for every n >= 21."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-sign-pattern",
 witness_type="numeric-bound",
 witness_check_cost="cheap: r(n) is a coefficient of an explicit q-series product/quotient, computable exactly via power-series arithmetic (e.g. sympy/sage) to any desired n in polynomial time",
 known_cases="Paper proves r(3n)>0, r(3n+1)<0, r(3n+2)<0 for all SUFFICIENTLY LARGE n via a Rademacher-type asymptotic expansion, but does not pin down the exact cutoff; the conjecture asserts the sign law already holds from n=21 onward.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="A counterexample is a single n>=21 with the 'wrong' sign of r(n) -- purely a finite power-series coefficient computation, one of the cheapest checks in this batch; a natural first move is to just compute r(21..N) for large N and confirm/refute directly (the asymptotic proof suggests the sign law should be easy to confirm computationally for a wide range, turning this into a search for the true cutoff if 21 itself is wrong).",
)

# 17 -----------------------------------------------------------------
add(
 id="lit-numbertheory-overpartition-congruence-mod7",
 source="arXiv:2603.08510 (New Ramanujan-type congruences for overpartitions modulo 11 and 13)",
 url="http://arxiv.org/abs/2603.08510v1",
 provenance=prov(933),
 statement_nl=(
  "The overpartition function p-bar(n) counts the overpartitions of n (partitions of n in which the "
  "first occurrence of a part may be overlined), with generating function sum_n p-bar(n) q^n = "
  "prod_{k>=1} (1+q^k)/(1-q^k). Conjecture: p-bar(2^4 * (56n+k)) = 0 (mod 7) for all n >= 0 and all "
  "k in {11, 43, 51}."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-congruence",
 witness_type="numeric-bound",
 witness_check_cost="cheap: p-bar(m) is computable exactly for any concrete m via the standard generating-function/partition-counting recurrences (polynomial time in m, e.g. via sympy or a direct DP)",
 known_cases="Paper proves two related congruences modulo 11 and 13 unconditionally; the mod-7 statement (for k in {11,43,51}) is explicitly flagged in the abstract as conjectural, alongside analogous conjectures for moduli 17, 19, 23 (not extracted here -- see the source for the full family).",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="A counterexample is a single (n,k) pair with p-bar(2^4*(56n+k)) not divisible by 7 -- exact integer arithmetic, no floating point, fully mechanical to check for as many n as desired.",
)

# 18 -----------------------------------------------------------------
add(
 id="lit-combinatorics-median-eigenvalue-bound",
 source="arXiv:2603.27434 (Bounds on median eigenvalues of graphs of bounded degree)",
 url="http://arxiv.org/abs/2603.27434v1",
 provenance=prov(1441),
 statement_nl=(
  "For a graph G on n vertices with adjacency eigenvalues lambda_1(G) >= ... >= lambda_n(G), the "
  "median eigenvalues are lambda_ceil(n/2)(G) and lambda_(floor(n/2)+1)(G) (a single value when n is "
  "odd). The average degree of G is 2|E(G)|/n. Conjecture: for every real number d >= 2, every "
  "median eigenvalue of every finite graph of average degree at most d has absolute value at most "
  "sqrt(d-1)."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-bound",
 witness_type="finite-object",
 witness_check_cost="cheap: median eigenvalues are computable by standard linear algebra for any concrete finite graph",
 known_cases="Proved for every integer maximum-degree d>=3 that median eigenvalues are <= sqrt(d-1) (upper direction) unconditionally; the matching lower bound (-sqrt(d-1)) is proved except for finitely many d -- specifically the paper resolves it when the graph is triangle-free, when d-1 is a perfect square, or when d>=75, leaving only a bounded set of exceptional d (roughly d<75, non-perfect-square d-1, non-triangle-free graphs) as the genuinely open residual for Mohar's original open problem.",
 current_bounds={"lower": None, "upper": "resolved for d>=75 or d-1 a perfect square or triangle-free"},
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="Because the residual open range of d is small and explicit (bounded above by 75, with two easy-to-check exclusions), an attack agent should first enumerate the finitely many remaining integer d and search bounded-average-degree graphs for a median eigenvalue below -sqrt(d-1).",
)

# 19 -----------------------------------------------------------------
add(
 id="lit-combinatorics-chromatic-poly-log-concave-derivative",
 source="arXiv:2603.07510 (On a conjecture concerning the property of chromatic polynomials with negative variable)",
 url="http://arxiv.org/abs/2603.07510v1",
 provenance=prov(957),
 statement_nl=(
  "For a graph G of order n, let P(G,x) be its chromatic polynomial (the number of proper colorings "
  "of G with x colors, as a polynomial in x). Conjecture (Dong-Ge-Gong-Ning-Ouyang-Tay, 2021): the "
  "k-th derivative d^k/dx^k ( ln[ (-1)^n P(G,x) ] ) < 0 holds for every graph G, every integer k >= 2, "
  "and every real x in (-infinity, 0)."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-and-reals-inequality",
 witness_type="finite-object",
 witness_check_cost=(
  "moderate: for a FIXED graph G and k, ln[(-1)^n P(G,x)] is an explicit elementary function of x "
  "whose k-th-derivative sign on (-infinity,0) can in principle be certified by exact symbolic/interval "
  "methods (e.g. Sturm-sequence-style real-root counting on the derivative's numerator after clearing "
  "denominators), avoiding floating point; flag as symbolically nontrivial for large k"
 ),
 known_cases="This paper (arXiv:2603.07510) proves the conjecture for all k>=2 and all x <= -10*Delta*k, where Delta is the maximum degree of G -- so the open residual is the bounded window x in (-10*Delta*k, 0) for each G.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="A counterexample is a specific (G,k,x) with x in the bounded residual window (-10*Delta*k,0) and the derivative sign wrong -- finite in G if search is restricted to small graphs, and finite in x once restricted to the known-open window; genuinely a 2021-origin conjecture with active 2026 partial progress, so check for even more recent partial resolutions before spending an attack budget.",
)

# 20 -----------------------------------------------------------------
add(
 id="lit-numbertheory-graham-rearrangement",
 source="arXiv:2602.15797 (On Graham's rearrangement conjecture)",
 url="http://arxiv.org/abs/2602.15797v1",
 provenance=prov(316),
 statement_nl=(
  "Graham's rearrangement conjecture (1971): for every prime p and every subset S subset Z_p \\ {0}, "
  "there is an ordering s_1, s_2, ..., s_|S| of the elements of S such that all |S| partial sums "
  "s_1, s_1+s_2, ..., s_1+s_2+...+s_|S| (taken mod p) are pairwise distinct."
 ),
 statement_formal=None,
 quantifier_shape="forall-primes-and-subsets-exists-ordering",
 witness_type="finite-object",
 witness_check_cost="cheap for a fixed (p,S): checking one candidate ordering is O(|S|); finding a valid ordering (or certifying none exists) by brute force over |S|! orderings is only feasible for small |S|, but SAT/CP encodings scale much further",
 known_cases=(
  "Bedert-Kravitz: holds for |S| <= exp((log p)^(1/4)). This paper (2602.15797) extends the proof to "
  "|S| <= p^(1-alpha) for any fixed alpha in (0,1) with |S| large relative to alpha, giving (combined "
  "with prior work) a complete resolution for all SUFFICIENTLY LARGE primes p."
 ),
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=(
  "Websearch (query: \"Graham's rearrangement conjecture 1971 computer verification small primes\") "
  "confirms the above proof-coverage picture but surfaces no report of an exhaustive computer search "
  "for a counterexample among small primes; classical (1971) origin, so any prior small-p verification "
  "would likely be folklore rather than published -- worth checking OEIS/mathoverflow before spending "
  "budget."
 ),
 notes="The genuinely open residual is: small (non-'sufficiently large') primes p, together with subset sizes |S| in the gap between exp((log p)^(1/4)) and p^(1-alpha) -- both endpoints depend on unspecified thresholds in the cited papers, so the practical attack is a direct SAT/backtracking search over small p and all S subset Z_p\\{0} looking for one S with no valid ordering.",
)

# 21 -----------------------------------------------------------------
add(
 id="lit-combinatorics-recursive-quasigroup-code-q14-q18",
 source="arXiv:2604.01105 (On the Construction of Recursively Differentiable Quasigroups and an Example of a Recursive [4,2,3]_26-Code)",
 url="http://arxiv.org/abs/2604.01105v1",
 provenance=prov(1280),
 statement_nl=(
  "A recursive [4,2,3]_q-code is a code of length 4, dimension 2, minimum distance 3 over an "
  "alphabet of size q built recursively from a recursively differentiable quasigroup of order q "
  "(Couselo-Gonzalez-Markov-Nechaev, 1998; see the source paper for the full recursive/quasigroup "
  "definitions). Conjecture (Couselo-Gonzalez-Markov-Nechaev, 1998): for every q not in {2, 6}, "
  "there exists a complete recursive [4,2,3]_q-code."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-exists-construction",
 witness_type="finite-object",
 witness_check_cost="moderate: verifying a candidate construction for one q is a finite, mechanical algebraic check (verify the quasigroup/orthogonality and code-distance properties); finding one is a nontrivial finite search over quasigroups of order q",
 known_cases="Verified in all cases except q in {14, 18, 26, 42}; q=42 resolved in 2008 (Markov-Nechaev-Skazhenik-Tveritinov); q=26 resolved by this very paper (2026). Websearch confirms q=14 and q=18 are the only remaining open cases.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="Websearch (query: '\"recursively differentiable quasigroups\" recursive MDS code q=14 q=18 open') confirms q in {14,18} is exactly the current open residual as of this paper's publication (2026); this is a 1998-origin conjecture with a strong 26-year history of case-by-case resolution, a strong positive tractability signal (each case is a self-contained finite construction search).",
 notes="Only two integer instances (q=14, q=18) remain -- about as narrow a residual as this harvest found. Attack = explicit search for a recursively differentiable quasigroup of order 14 or 18 (or a proof of nonexistence), following the same perfect-cyclic-Mendelsohn-design method the source paper used for q=26.",
)

# 22 -----------------------------------------------------------------
add(
 id="lit-combinatorics-even-hole-free-chi-bound",
 source="arXiv:2602.04403 (The optimal chromatic bound for even-hole-free graphs without induced seven-vertex paths)",
 url="http://arxiv.org/abs/2602.04403v1",
 provenance=prov(675),
 statement_nl=(
  "A graph is even-hole-free if it has no induced cycle of even length >= 4. For a graph G, chi(G) "
  "is the chromatic number and omega(G) the clique number. Conjecture (general chi-boundedness "
  "conjecture for even-hole-free graphs): for every even-hole-free graph G, chi(G) <= ceil( (5/4) * omega(G) )."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-bound",
 witness_type="finite-object",
 witness_check_cost="expensive per candidate in general (computing chi(G) exactly is NP-hard) but fully brute-force/SAT-checkable for small graphs, and even-hole-freeness is checkable in polynomial time",
 known_cases="This paper (2602.04403) proves the bound for the subclass of even-hole-free graphs with no induced 7-vertex path, extending Karthick-Maffray's earlier result for no induced 6-vertex path; the fully general even-hole-free case (no path restriction) remains open.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="Well-studied structural graph-coloring conjecture with a documented sequence of partial resolutions (6-vertex-path-free, then 7-vertex-path-free); no claim of an exhaustive small-graph computer search for a counterexample in the fully general case was found.",
 notes="A counterexample would be an even-hole-free graph G (not restricted to short induced paths) with chi(G) > ceil(5/4 * omega(G)) -- brute-forceable via nauty/geng plus a SAT-based chromatic-number solver on small even-hole-free graphs.",
)

# 23 -----------------------------------------------------------------
add(
 id="lit-combinatorics-saturation-harmonic-index-deg4",
 source="arXiv:2606.15761 (Sharp bounds between the saturation number and the harmonic index)",
 url="http://arxiv.org/abs/2606.15761v3",
 provenance=prov(3702),
 statement_nl=(
  "The saturation number mu*(G) of a graph G is the minimum cardinality of a maximal matching (a "
  "matching that cannot be extended by adding another disjoint edge). The harmonic index is "
  "H(G) = sum over edges uv in E(G) of 2/(deg(u)+deg(v)). Conjecture: every connected graph of "
  "maximum degree at most 4 satisfies mu*(G) <= H(G)."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-bound",
 witness_type="finite-object",
 witness_check_cost="cheap: both mu*(G) (minimum maximal matching, computable by ILP or brute force for small G) and H(G) (a direct sum over edges) are cheaply computable for concrete small graphs",
 known_cases=(
  "The unrestricted version (TxGraffiti, 2023: mu*(G)<=H(G) for every nontrivial connected graph) is "
  "refuted -- Biyikoglu showed the ratio mu*(G)/H(G) can be made arbitrarily large, and this paper "
  "exhibits the friendship graph F_4 (9 vertices, hub degree 8) as the smallest counterexample. "
  "Restricting to maximum degree <=4 is exactly the fix proposed to save the conjecture; it is also "
  "proved when all vertices have equal degree (regular graphs)."
 ),
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="Directly descended from a TxGraffiti (automated conjecturing software) conjecture that was already refuted once in the unrestricted form -- strong precedent that this exact restricted form is the kind of statement small-graph search is good at settling either way.",
 notes="A counterexample is a connected graph of maximum degree <=4 with mu*(G) > H(G) -- straightforward to search exhaustively via nauty/geng over small graphs with a degree cap.",
)

# 24 -----------------------------------------------------------------
add(
 id="lit-combinatorics-cist-k-outerplanar-nonexistence",
 source="arXiv:2606.12827 (Completely Independent Spanning Trees in k-Outerplanar Triangulated Discs)",
 url="http://arxiv.org/abs/2606.12827v1",
 provenance=prov(3824),
 statement_nl=(
  "A planar graph is k-outerplanar if it has a planar embedding in which, after repeatedly deleting "
  "the vertices on the outer face k times, no vertices remain (1-outerplanar = outerplanar: all "
  "vertices on one face). A triangulated disc is a maximal planar graph drawn with a distinguished "
  "outer face such that every bounded face is a triangle. Given k spanning trees T_1,...,T_k of a "
  "graph G, they are completely independent spanning trees (CISTs) if, for every pair of vertices "
  "u,v, the u-v paths in the k trees are pairwise internally vertex-disjoint. Conjecture: for every "
  "integer k >= 4, there exists a 3-connected k-outerplanar triangulated disc that has no two "
  "completely independent spanning trees (i.e. G admits no pair of CISTs)."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-exists-construction",
 witness_type="finite-object",
 witness_check_cost="moderate: for a fixed candidate graph, checking whether it has 2 CISTs is a finite search over pairs of spanning trees (NP-hard in general for k>=3 trees, but the base case of exactly 2 CISTs and small structured planar graphs is tractable via ILP/SAT)",
 known_cases="The paper itself already proves every 3-connected 2-outerplanar triangulated disc HAS 2 CISTs, and exhibits an explicit 3-connected 4-outerplanar triangulation with NO 2 CISTs -- i.e. the k=4 case of this very conjecture is already resolved (proved) by the source paper. The residual open part is k >= 5.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="Companion to lit-combinatorics-cist-3-outerplanar-universal (same paper): together they assert 2-outerplanar always has 2 CISTs (proved), 3-outerplanar always has 2 CISTs (conjectured, open), and k-outerplanar for k>=4 sometimes lacks 2 CISTs (k=4 proved by explicit example, k>=5 open). Attack the k>=5 residual by adapting the paper's own k=4 counterexample construction.",
)

# 25 -----------------------------------------------------------------
add(
 id="lit-combinatorics-cist-3-outerplanar-universal",
 source="arXiv:2606.12827 (Completely Independent Spanning Trees in k-Outerplanar Triangulated Discs)",
 url="http://arxiv.org/abs/2606.12827v1",
 provenance=prov(3823),
 statement_nl=(
  "Using the definitions of k-outerplanar, triangulated disc, and completely independent spanning "
  "trees (CISTs) from lit-combinatorics-cist-k-outerplanar-nonexistence: conjecture that every "
  "3-connected 3-outerplanar triangulated disc has two completely independent spanning trees."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-exists-two-trees",
 witness_type="finite-object",
 witness_check_cost="moderate: a counterexample is one explicit 3-connected 3-outerplanar triangulated disc with no valid pair of CISTs -- checkable by exhaustive search over spanning-tree pairs for a concrete finite graph",
 known_cases="Paper proves only sufficient conditions for a 3-connected 3-outerplanar triangulated disc to have 2 CISTs (not the fully general statement), so the gap between 'sufficient conditions hold' and 'always true' is the open part.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="Directly complementary to lit-combinatorics-cist-k-outerplanar-nonexistence: this one is a universal ('always has CISTs') claim at outerplanarity depth exactly 3, the layer right below where the paper's own k=4 counterexample shows the property can fail. A natural first target: exhaustively generate small 3-connected 3-outerplanar triangulated discs (plantri-style planar triangulation generation with an outerplanarity filter) and CIST-check each one.",
)

# 26 -----------------------------------------------------------------
add(
 id="lit-combinatorics-chi2-planar-coloring",
 source="arXiv:2602.13037 (Between proper and square coloring of planar graphs, hardness and extremal graphs)",
 url="http://arxiv.org/abs/2602.13037v1",
 provenance=prov(385),
 statement_nl=(
  "Call a set S of vertices of a graph G '2-independent' if the subgraph induced by S, G[S], has "
  "maximum degree at most 1 (equivalently, S is the union of an independent set and a matching). "
  "Let chi_2(G) be the minimum number of parts in a partition of V(G) into 2-independent sets "
  "(reconstructed from the paper's '(1^a,2^b)-coloring' framework as the all-2-independent extreme "
  "case a=0; verify against the paper's exact Definition before use). Let Delta(G) be the maximum "
  "degree of G. Conjecture: for every planar graph G, chi_2(G) <= 7 if Delta(G) = 3; chi_2(G) <= "
  "Delta(G) + 5 if 4 <= Delta(G) <= 7; chi_2(G) <= floor(3*Delta(G)/2) + 1 otherwise (Delta(G) >= 8)."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-bound-caselist",
 witness_type="finite-object",
 witness_check_cost="moderate: for a concrete planar graph, chi_2(G) is computable by ILP/SAT search over partitions (each part checked for max-induced-degree <=1); planar-graph generation via plantri makes exhaustive small-case search feasible",
 known_cases="Paper proves related upper bounds of the form (1^a, 2^{O(sqrt n)}) for k-degenerate, triangle-free planar, and general planar graphs, and shows the underlying (1^a,2^b)-coloring decision problem is NP-complete even on restricted planar graph classes.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="DEFINITION RISK: chi_2(G) is reconstructed from context (the paper's body_tex for this conjecture uses the symbol directly without repeating the definition in the extracted snippet); confirm the precise definition against the source paper before writing a checker. If confirmed, NP-completeness of the underlying decision problem (proved by the same paper) means an ILP/SAT-based checker, not a greedy algorithm, is required for exact chi_2 values.",
)

# 27 -----------------------------------------------------------------
add(
 id="lit-combinatorics-depth-symbolic-power-weakly-chordal",
 source="arXiv:2607.04231 (Ordered alternating paths and the depth of symbolic powers of cover ideals of graphs)",
 url="http://arxiv.org/abs/2607.04231v1",
 provenance=prov(4602),
 statement_nl=(
  "For a simple graph G with vertex set V(G) of size n, let S be the polynomial ring in n variables "
  "(one per vertex) over a field, and let J(G) be the cover ideal of G (the ideal generated by the "
  "monomials prod_{v in C} x_v over all minimal vertex covers C of G). For a matching M of G, let "
  "l(M) be the length (number of edges) of the longest M-alternating path in G. Define alpha_t(G) to "
  "be the maximum size of an 'ordered matching' M of G (a matching admitting a linear order of its "
  "edges with a specific alternating-path compatibility property, per the paper's Definition) with "
  "l(M) <= 2t-1. G is weakly chordal if neither G nor its complement has an induced cycle of length "
  ">= 5. Conjecture: for every weakly chordal graph G on n vertices, depth(S / J(G)^(t)) = n - 1 - "
  "alpha_t(G) for all t >= 1, where J(G)^(t) is the t-th symbolic power of J(G)."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-and-integers-exact-equality",
 witness_type="numeric-bound",
 witness_check_cost=(
  "expensive: exact depth of S/J(G)^(t) generally requires a Groebner-basis / free-resolution "
  "computation in a computer algebra system (Macaulay2, Singular, CoCoA) -- decidable and exact but "
  "not cheap, and worst-case complexity is doubly exponential in the number of variables, so flag as "
  "a heavy per-instance check even though it is not classically NP-hard"
 ),
 known_cases="Paper proves the inequality depth(S/J(G)^(t)) <= n-1-alpha_t(G) unconditionally for ALL graphs, and proves equality when G is a forest; weakly chordal graphs (which include forests as a special case) is the proposed sharp generality for the equality direction.",
 current_bounds={"lower": None, "upper": "n-1-alpha_t(G) (proved in general)"},
 class_=None,
 tractability=None,
 prior_attempts=None,
 notes="A counterexample is a weakly chordal graph G and integer t>=1 with strict inequality depth(S/J(G)^(t)) < n-1-alpha_t(G) -- checkable exactly via Macaulay2/Singular for small G and small t, though each check is a real computer-algebra computation rather than combinatorial brute force.",
)

# 28 -----------------------------------------------------------------
add(
 id="lit-combinatorics-circular-chromatic-index-kd1-minus-e",
 source="arXiv:2603.08822 (Circular chromatic index of small graphs)",
 url="http://arxiv.org/abs/2603.08822v1",
 provenance=prov(923),
 statement_nl=(
  "The circular chromatic index chi'_c(G) of a graph G is the infimum of r/s over all pairs of "
  "positive integers (r,s) with r >= s such that G has a circular edge coloring with colors "
  "{0,1,...,r-1} arranged on a cycle, in which adjacent edges e,f receive colors c(e),c(f) with "
  "circular distance min(|c(e)-c(f)|, r-|c(e)-c(f)|) >= s (this equals the classical chromatic index "
  "when s=1; it is always between Delta(G) and Delta(G)+1 where Delta is the maximum degree). Let "
  "K_{d+1} be the complete graph on d+1 vertices. Conjecture: for every even integer d > 4, the "
  "graph G obtained from K_{d+1} by deleting a single edge has chi'_c(G) = d+1."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-exact-value",
 witness_type="finite-object",
 witness_check_cost="moderate: circular chromatic index is computable exactly via LP/ILP relaxation techniques for a concrete small graph (K_{d+1} minus an edge has only d+1 vertices), so each even d is an independent, fully finite check",
 known_cases="Paper systematically computes circular chromatic index for small graphs/multigraphs of maximum degree 4,5,6 and constructs infinite families with circular chromatic index in {Delta+1/2, Delta+2/3, Delta+3/4, Delta+1}, explicitly refuting an edge-connectivity variant of the 'Upper Gap Conjecture'.",
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="This same paper already systematically computed circular chromatic index for all small graphs of degree <=6 -- meaning small even d (say d=6,8) are very likely already checked by the authors' own systematic computation; the genuinely open range is presumably larger even d beyond their systematic search.",
 notes="Being an exact-value claim about one specific, explicitly-named graph family (K_{d+1} minus an edge) per even d, this is essentially as close to a pure finite check as this harvest found -- but the authors' own systematic small-graph computation may already cover small d, so the real target is likely mid-to-large even d not yet reached by exhaustive search.",
)

# 29 -----------------------------------------------------------------
add(
 id="lit-combinatorics-dominating-set-sequence-unimodal",
 source="arXiv:2605.02193 (Trees and Graphs with Non Log-concave Dominating Set Sequence via AI Tools)",
 url="https://arxiv.org/abs/2605.02193v1",
 provenance=prov(2467),
 statement_nl=(
  "For a graph G on n vertices, let d_i(G) be the number of dominating sets of G with exactly i "
  "vertices, for i=0,...,n (a set S subset V(G) is dominating if every vertex not in S has a "
  "neighbor in S). Conjecture: for every finite graph G, the sequence d_0(G), d_1(G), ..., d_n(G) is "
  "unimodal, i.e. there exists some 0 <= m <= n with d_0(G) <= d_1(G) <= ... <= d_m(G) >= d_(m+1)(G) "
  ">= ... >= d_n(G)."
 ),
 statement_formal=None,
 quantifier_shape="forall-graphs-shape-property",
 witness_type="finite-object",
 witness_check_cost="cheap for small graphs: d_i(G) for all i is exactly the coefficient sequence of the domination polynomial of G, computable by brute-force subset enumeration (2^n subsets) or a faster domination-polynomial algorithm; checking unimodality of the resulting sequence is trivial once computed",
 known_cases=(
  "The strictly STRONGER log-concavity version of this same sequence is explicitly REFUTED by this "
  "very paper: it reports new counterexample graphs (found by PatternBoost, a transformer-based "
  "reinforcement-learning search tool) with non-log-concave dominating-set sequences, plus an "
  "infinite family of trees with non-log-concave sequences at >= m indices for any m. The weaker "
  "unimodality claim is what survives as the open conjecture. A large class of caterpillar graphs is "
  "shown to have log-concave (hence unimodal) sequences, and a continuous analogue of the sequence is "
  "proved unimodal/log-concave for all graphs."
 ),
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts=(
  "The source paper itself already ran a machine-learning-guided search (PatternBoost) specifically "
  "hunting for counterexamples to the STRONGER log-concavity property and succeeded there -- a strong, "
  "directly relevant precedent that the weaker unimodality property is a natural next target for the "
  "exact same search methodology, and a meaningfully different (harder) bar than what has already been refuted."
 ),
 notes="One of the cleanest entries in this batch: the domination polynomial is a completely standard, brute-force-computable graph invariant, and the paper's own tooling (PatternBoost) is a ready-made counterexample-search baseline to compare against or extend.",
)

# 30 -----------------------------------------------------------------
add(
 id="lit-numbertheory-reciprocal-rado-f2k",
 source="arXiv:2607.04373 (A sharp lower bound for some reciprocal Rado numbers)",
 url="http://arxiv.org/abs/2607.04373v1",
 provenance=prov(4594),
 statement_nl=(
  "For positive integers r,k, let f_r(k) be the smallest n such that every r-coloring of "
  "{1,2,...,n} contains a monochromatic solution (x_1,...,x_k,x_(k+1)), not necessarily distinct, to "
  "1/x_1 + 1/x_2 + ... + 1/x_k = 1/x_(k+1). Conjecture: if k >= 4 and k is not an odd prime power, "
  "then f_2(k) = 3*k^2."
 ),
 statement_formal=None,
 quantifier_shape="forall-integers-exact-value",
 witness_type="numeric-bound",
 witness_check_cost=(
  "expensive for large k despite being fully finite: verifying f_2(k)=3k^2 requires (a) a 2-coloring "
  "of {1,...,3k^2-1} with NO monochromatic solution (a finite combinatorial certificate, checkable in "
  "polynomial time once exhibited, but the search space of 2-colorings is exponential) and (b) a proof "
  "that every 2-coloring of {1,...,3k^2} DOES contain one (in principle a finite SAT instance, size "
  "growing with k)"
 ),
 known_cases=(
  "Paper proves f_r(2) >= 4^r/2 for all r>=1 and f_r(k) >= (2^r-1)*k^r for all k>=3, r>=1 (general "
  "lower bounds); for r=2 specifically, proves f_2(k)=3k^2 exactly when k=3*2^m (m a positive "
  "integer), and f_2(k) >= 3k^2+1 (i.e. the formula FAILS by at least 1) when k=p^m for an odd prime "
  "p. The conjectured case (k not an odd prime power, k>=4) is the general form covering the "
  "remaining k not already resolved as k=3*2^m or excluded as an odd prime power."
 ),
 current_bounds=None,
 class_=None,
 tractability=None,
 prior_attempts="Paper reports its own new computational results for f_2(k) and f_3(k) -- i.e. some exact small-k values are already machine-computed; check the paper's computational appendix/tables before re-deriving small cases.",
 notes="Precisely defined via the generating Rado-type equation, no additional structure to reconstruct. Natural SAT-based attack: for each small even/composite k not an odd prime power, encode 'every 2-coloring of {1..3k^2} has a monochromatic solution' as a SAT instance and check satisfiability of the negation (search for a coloring with none) at n=3k^2 and n=3k^2-1.",
)

# ---------------------------------------------------------------------
assert len(entries) == 30, len(entries)

out_path = "/home/user/openproblem-miner/mine/corpus/raw/h6_literature.jsonl"
seen_ids = set()
with open(out_path, "w") as f:
    for e in entries:
        rec = {
            "id": e["id"],
            "source": e["source"],
            "url": e["url"],
            "provenance": e["provenance"],
            "statement_nl": e["statement_nl"],
            "statement_formal": e.get("statement_formal"),
            "quantifier_shape": e.get("quantifier_shape"),
            "witness_type": e["witness_type"],
            "witness_check_cost": e.get("witness_check_cost"),
            "known_cases": e.get("known_cases"),
            "current_bounds": e.get("current_bounds"),
            "prior_attempts": e.get("prior_attempts"),
            "prize": None,
            "class": e.get("class_"),
            "tractability": e.get("tractability"),
            "provenance_type": "clone",
            "notes": e.get("notes"),
        }
        assert rec["id"] not in seen_ids, f"dup id {rec['id']}"
        seen_ids.add(rec["id"])
        line = json.dumps(rec, ensure_ascii=False)
        # validate round-trip
        json.loads(line)
        f.write(line + "\n")

print("wrote", len(entries), "entries to", out_path)
