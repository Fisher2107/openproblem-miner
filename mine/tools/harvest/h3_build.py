import json

REPO = "yao-creative/Wiki-clustering-ml"
COMMIT = "58c53df46c4f9f623cc818187895255812b4db43"
PATH = "data/List_of_unsolved_problems_in_mathematics.txt"
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_mathematics"

def clone_prov(line):
    return f"clone:{REPO}@{COMMIT}:{PATH}#L{line}"

def base(id_, statement, line, quantifier, witness_type, witness_cost, known_cases="", notes="", prior="", src=WIKI_URL):
    return {
        "id": id_,
        "source": "en.wikipedia.org/List_of_unsolved_problems_in_mathematics (via GitHub mirror, wiki blocked at egress)",
        "url": src,
        "provenance": clone_prov(line),
        "statement_nl": statement,
        "statement_formal": None,
        "quantifier_shape": quantifier,
        "witness_type": witness_type,
        "witness_check_cost": witness_cost,
        "known_cases": known_cases,
        "current_bounds": {"lower": None, "upper": None},
        "prior_attempts": prior,
        "prize": None,
        "class": None,
        "tractability": None,
        "notes": notes,
    }

entries = []

# ---------------- GEOMETRY ----------------

entries.append(base(
    "wiki-borsuks-problem",
    "For each n, let f(n) be the smallest number such that every bounded set in R^n can be partitioned into f(n) subsets of strictly smaller diameter. Borsuk conjectured f(n) = n+1; Kahn and Szemerédi (1993) disproved this for large n via a counterexample using c^n points on a sphere. What is the exact value (or asymptotic growth rate) of f(n), and for which n does f(n) = n+1 still hold?",
    456,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Kahn-Szemerédi (1993) showed f(n) can require exponentially many pieces for large n, refuting the original n+1 conjecture in high dimension; f(n)=n+1 is known to hold for n<=3. The exact asymptotic rate of f(n) and its value for most individual small n (e.g. whether f(n)=n+1 fails already at some specific small n like 4,...,63) remain undetermined.",
    notes="Distinct from the disproved Borsuk conjecture itself: the still-open object is the exact behavior of f(n), a bound-gap problem.",
))

entries.append(base(
    "wiki-kissing-number-problem",
    "The kissing number k(n) is the maximum number of non-overlapping unit spheres in R^n that can simultaneously touch a central unit sphere. k(n) is known exactly only for n in {1,2,3,4,8,24}. Determine the exact value of k(n) for all other n.",
    485,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Exact values known for n=1,2,3,4,8,24 (n=3 by Hales et al., n=4 by Musin 2003/2008, n=8,24 by Viazovska et al. 2016-17). Only upper/lower bounds are known for all other n.",
))

entries.append(base(
    "wiki-reinhardts-conjecture",
    "Reinhardt's conjecture: among all centrally-symmetric convex regions in the plane, the smoothed octagon (a regular octagon with its corners rounded by hyperbolic arcs) has the lowest possible maximum packing density, i.e. it is the worst-packing centrally-symmetric convex shape.",
    486,
    "exists-construction",
    "none",
    "unknown",
))

entries.append(base(
    "wiki-sphere-packing-other-dims",
    "For dimension n, let Delta(n) be the density of the densest packing of congruent spheres in R^n. Delta(n) is known exactly only for n in {1,2,3,8,24}. Determine the exact value of Delta(n) for all other n, and determine the asymptotic behavior of Delta(n) as n -> infinity.",
    487,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Exact optimal density known for n=1,2,3 (Hales, Kepler conjecture), n=8 and n=24 (Viazovska et al., 2016-2017). All other dimensions, and the asymptotic rate as n->infinity, remain open.",
))

entries.append(base(
    "wiki-ulams-packing-conjecture",
    "Ulam's packing conjecture: no convex solid packs 3-dimensional space with a lower maximum density than the sphere. Equivalently, the sphere is conjectured to be the worst-packing convex solid in R^3.",
    489,
    "forall-integers",
    "none",
    "unknown",
    notes="Quantifier is really 'for all convex solids'; classified here as forall-integers loosely per schema options (no closer fit).",
))

entries.append(base(
    "wiki-caratheodory-conjecture",
    "Carathéodory's conjecture: every convex, closed, and sufficiently smooth (C^3, say) surface in R^3 admits at least two umbilical points (points where the surface's two principal curvatures are equal).",
    497,
    "forall-graphs",
    "none",
    "unknown",
))

entries.append(base(
    "wiki-cartan-hadamard-conjecture",
    "The Cartan-Hadamard conjecture: can the classical isoperimetric inequality for subsets of Euclidean space (bounding surface area in terms of enclosed volume) be extended to Cartan-Hadamard manifolds, i.e. complete simply-connected Riemannian manifolds of everywhere nonpositive sectional curvature?",
    498,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Known to hold in dimensions 2, 3, and 4 (Weil; Kleiner; Croke; and others). Open for dimension >= 5.",
))

entries.append(base(
    "wiki-filling-area-conjecture",
    "The filling area conjecture: among all fillings of a closed curve of a given length by a surface (a shortcut-free surface whose boundary is that curve, meaning no filling's induced boundary distance is shorter than the original), the round hemisphere has the minimum area.",
    502,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Proved by Ivanov for fillings that are Riemannian disks; the general case (arbitrary shortcut-free surfaces / other topologies) remains open.",
))

entries.append(base(
    "wiki-hadwiger-covering-conjecture",
    "Hadwiger's covering conjecture: every bounded convex body in R^n can be covered by at most 2^n smaller (positively scaled) translates of itself, with equality only for the parallelepiped.",
    512,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Proved for n=2 (equality is the case of the parallelogram/hexagon needing 4). Best known general upper bound is exponential but with a worse constant than 2^n (e.g. binom(2n,n)*n*ln(n) type bounds). Open for n>=3.",
    notes="Not to be confused with the Hadwiger conjecture on graph coloring (already formalized) or the Hadwiger-Nelson chromatic-number-of-the-plane problem.",
))

entries.append(base(
    "wiki-kalais-3d-conjecture",
    "Kalai's 3^d conjecture: every centrally symmetric d-dimensional polytope has at least 3^d nonempty faces (including the polytope itself and the empty face is excluded, i.e. summing over faces of all dimensions from 0 to d).",
    523,
    "bound",
    "numeric-bound",
    "poly",
    known_cases="Proved for d<=3 and for simplicial or simple centrally symmetric polytopes in general dimension (Stanley, and others). Open in general for d>=4 among all centrally symmetric polytopes.",
))

entries.append(base(
    "wiki-kobon-triangle-problem",
    "The Kobon triangle problem: let K(n) be the maximum number of nonoverlapping triangles that can be formed by an arrangement of n straight lines in the plane. Determine K(n) exactly for every n.",
    524,
    "bound",
    "numeric-bound",
    "exponential",
    known_cases="Exact value of K(n) is known for small n (up to around n=32 or so via computer search / constructions) and a general upper bound floor(n(n-2)/3) is known; the exact value for general/large n remains open.",
))

entries.append(base(
    "wiki-kusner-conjecture",
    "The Kusner conjecture: in R^d equipped with the l^1 (taxicab) metric, at most 2d points can be pairwise equidistant from one another.",
    525,
    "bound",
    "numeric-bound",
    "exponential",
    known_cases="Proved for d<=4. Open for d>=5.",
))

entries.append(base(
    "wiki-mcmullen-problem",
    "The McMullen problem: what is the largest number f(d) such that, for any f(d) points in general position in R^d, there is a projective transformation taking all of the points into convex position (i.e. onto the vertices of a convex polytope)?",
    548,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Bounds 2d+1 <= f(d) <= 3d+1 are known (McMullen's original bounds, subsequently sharpened somewhat). The exact value of f(d) is open for d>=3.",
))

entries.append(base(
    "wiki-opaque-forest-problem",
    "The opaque forest problem: for a given convex region in the plane (e.g. the unit square or unit disk), what is the shortest total length of a collection of curves (a 'barrier' or 'opaque forest') such that every line crossing the region must intersect the collection?",
    549,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Best known upper and lower bounds for the unit square and unit disk barrier lengths do not match; the exact minimum length is unknown even for the unit square.",
))

entries.append(base(
    "wiki-danzers-problem",
    "Danzer's problem (also called Conway's dead fly problem): does there exist a Danzer set of bounded density, i.e. a set of points in R^n that intersects every convex body of volume 1, with the number of points in any ball of radius R growing only linearly in R (bounded density), or one of bounded separation between consecutive points along any line?",
    606,
    "exists-construction",
    "none",
    "unknown",
))

entries.append(base(
    "wiki-ehrharts-volume-conjecture",
    "Ehrhart's volume conjecture: if a convex body K in R^n contains exactly one lattice point in its interior and that point is the center of mass of K, then the volume of K is at most (n+1)^n / n!.",
    607,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Known to hold in low dimensions (proved for n<=... small cases and for specific families); open in general dimension n.",
))

entries.append(base(
    "wiki-falconers-conjecture",
    "Falconer's conjecture: if a set A in R^d has Hausdorff dimension greater than d/2, then the distance set {|x-y| : x,y in A} has positive Lebesgue measure.",
    647,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="The d=2 case was proved by Guth, Iosevich, Ou, and Wang (2020) with threshold 5/4 improved toward but not reaching 1. General d/2 threshold for d=2, and the conjecture for all d>=3, remains open.",
))

entries.append(base(
    "wiki-lebesgues-universal-covering-problem",
    "Lebesgue's universal covering problem: find the convex region of smallest area in the plane that contains (can cover, after rotation and translation) a congruent copy of every set of diameter 1.",
    694,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Best known upper bound area is approximately 0.8440935944 (Baek, 2023) and best known lower bound is approximately 0.832 (Sriamorn / Brass-Sharifi lineage); the exact minimal area is not known.",
))

entries.append(base(
    "wiki-mahlers-conjecture",
    "Mahler's conjecture: for a centrally symmetric convex body K in R^n, the product vol(K) * vol(K°) of the volume of K and the volume of its polar dual K° is minimized (among centrally symmetric convex bodies) by the n-dimensional cube (equivalently the cross-polytope), giving the conjectured minimum 4^n/n!.",
    695,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Proved for n<=3, and asymptotically up to a constant factor in general dimension (Bourgain-Milman gives a lower bound of the right exponential order, and Kuperberg / others sharpened constants). The exact sharp constant in general n remains open.",
))

entries.append(base(
    "wiki-kelvin-problem",
    "The Kelvin problem: what is the partition of 3-dimensional space into cells of equal volume that minimizes the total surface area of the cell boundaries? Is the Weaire-Phelan structure (which beats Kelvin's original tetrakaidecahedral foam) in fact optimal?",
    693,
    "exists-construction",
    "none",
    "unknown",
    known_cases="The Weaire-Phelan structure (1993) is the best known candidate, improving on Kelvin's conjectured optimum; no proof that it is optimal is known.",
))

entries.append(base(
    "wiki-ruperts-property",
    "Does every convex polyhedron have Rupert's property, i.e. is it always possible to cut a hole in a copy of the polyhedron large enough to pass an identical (or larger) copy of the same polyhedron through the hole?",
    698,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Verified computationally/constructively for all 5 Platonic solids and many other specific polyhedra (including, controversially, some claims about all Archimedean solids); no proof that it holds for every convex polyhedron, nor a counterexample, is known.",
))

entries.append(base(
    "wiki-shephards-problem",
    "Shephard's problem (also called Dürer's conjecture): does every convex polyhedron have a net, i.e. can its surface always be unfolded along a spanning tree of its edges into a simple (non-self-overlapping) planar polygon?",
    699,
    "forall-graphs",
    "none",
    "unknown",
))

entries.append(base(
    "wiki-nonconvex-polyhedron-seven-faces",
    "Is there a non-convex polyhedron without self-intersections, all of whose faces share an edge with every other face, that has more than seven faces?",
    700,
    "bound",
    "finite-object",
    "exponential",
    known_cases="A polyhedron with exactly seven mutually edge-adjacent faces is known (Császár-type construction); whether more than seven is achievable is open.",
))

entries.append(base(
    "wiki-thomson-problem",
    "The Thomson problem: for n mutually-repelling point charges confined to the surface of a unit sphere, interacting via a 1/r potential, what is the minimum-energy configuration (equilibrium arrangement) of the n points, for general n?",
    701,
    "bound",
    "numeric-bound",
    "exponential",
    known_cases="Exact minimum-energy configurations are proven only for small n (e.g. n<=6, and a handful of special values like the icosahedron's 12 vertices); for general n only numerically-obtained candidate configurations are known, without a proof of global optimality.",
))

entries.append(base(
    "wiki-rados-covering-problem",
    "The covering problem of Radó: if a finite union of axis-parallel squares (of arbitrary sizes) has total area 1, how small can the largest total area be of a subset of pairwise-disjoint squares chosen from that union?",
    457,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Known that a disjoint subcollection of area at least 1/9 can always be found, and this is the best known general lower bound; the exact optimal constant is not known.",
))

# ---------------- GRAPH THEORY ----------------

entries.append(base(
    "wiki-cerecedas-conjecture",
    "Cereceda's conjecture: for a d-degenerate graph G on n vertices, the diameter of its (d+2)-recoloring graph (whose vertices are the proper (d+2)-colorings of G, with an edge between colorings differing at one vertex) is at most O(n^2).",
    728,
    "bound",
    "numeric-bound",
    "poly",
    known_cases="An exponential upper bound is known unconditionally; the conjectured quadratic bound is verified for special graph classes (e.g. some sparse/planar classes) but open in general.",
))

entries.append(base(
    "wiki-gyarfas-sumner-conjecture",
    "The Gyárfás-Sumner conjecture: for every tree T, there exists a function f_T such that every T-free graph (containing no induced copy of T) with clique number omega has chromatic number at most f_T(omega). Equivalently, the class of T-free graphs is chi-bounded for every tree T.",
    730,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Proved for several specific families of trees (e.g. paths as a consequence of the Gyárfás-Sumner conjecture for paths, brooms, spiders, and some others); open for general trees.",
))

entries.append(base(
    "wiki-hadwiger-conjecture-coloring",
    "Hadwiger's conjecture: for every integer t, every graph with no K_t minor is (t-1)-colorable. Equivalently, every graph's chromatic number is at most the size of its largest complete-graph minor.",
    731,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Known to be true for t<=6 (t<=4 classical, t=5 equivalent to the Four Color Theorem via Wagner's theorem, t=6 proved by Robertson-Seymour-Thomas 1993). Open for t>=7. A recent (2023) preprint by Delcourt and Postle claims an approximate version; the exact conjecture for t>=7 remains open as of the source consulted.",
    prior="Robertson-Seymour-Thomas (1993) for t=6; Delcourt-Postle approximate version (2023).",
))

entries.append(base(
    "wiki-jaegers-petersen-coloring-conjecture",
    "Jaeger's Petersen-coloring conjecture: every bridgeless cubic (3-regular) graph admits a cycle-continuous mapping to the Petersen graph (a map on edges sending each cycle to a cycle, induced by a map on the Petersen graph's edge set).",
    733,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Known to imply, and be implied by, several other flow/coloring conjectures (e.g. it would imply the cycle double cover conjecture and Tutte's 5-flow conjecture); unresolved in general.",
))

entries.append(base(
    "wiki-list-coloring-conjecture",
    "The list coloring conjecture: for every graph G, the list chromatic index ch'(G) (the least k such that G is edge-colorable from any assignment of k-element color lists to its edges) equals the ordinary chromatic index chi'(G).",
    734,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Proved for bipartite graphs (Galvin, 1995) and for graphs with chi'(G) large relative to max degree in some regimes; open in general.",
))

entries.append(base(
    "wiki-total-coloring-conjecture",
    "The total coloring conjecture (Behzad-Vizing): for every graph G with maximum degree Delta, the total chromatic number (minimum colors to properly color all vertices and edges so that no two adjacent/incident elements share a color) is at most Delta + 2.",
    735,
    "bound",
    "numeric-bound",
    "poly",
    known_cases="Known to hold for Delta<=5 and for several special graph classes (planar graphs with Delta>=9, e.g.); an upper bound of Delta+3 (given by Molloy-Reed via probabilistic methods, later improved) is known unconditionally close to but not matching the conjectured Delta+2. Open in general.",
))

entries.append(base(
    "wiki-albertson-conjecture",
    "The Albertson conjecture: for every graph G with chromatic number chi(G) = r, the crossing number of G is at least the crossing number of the complete graph K_r.",
    742,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Proved for r<=16 (via the known cases of the four color theorem and subsequent work up to r=16 by Albertson, Cranston, and Fox and others). Open for r>=17.",
))

entries.append(base(
    "wiki-conways-thrackle-conjecture",
    "Conway's thrackle conjecture: a thrackle is a drawing of a graph in the plane where every pair of edges meets exactly once, either at a shared endpoint or at a proper crossing. The conjecture states that every thrackle drawing of a graph with n vertices has at most n edges.",
    743,
    "bound",
    "numeric-bound",
    "poly",
    known_cases="Proved that the number of edges is at most 1.3984n (Fenner, Gyárfás, and others improving earlier 1.5n bounds); the tight bound of exactly n edges remains open.",
))

entries.append(base(
    "wiki-harborths-conjecture",
    "Harborth's conjecture: every planar graph has a planar straight-line drawing in which every edge has an integer length.",
    744,
    "forall-graphs",
    "none",
    "unknown",
))

entries.append(base(
    "wiki-negamis-conjecture",
    "Negami's conjecture: a connected graph has a finite planar cover (a finite covering graph that is itself planar) if and only if the graph embeds in the projective plane.",
    745,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="The 'if' direction is easy/known. Proved for graphs of connectivity at most 2 (reduces to the 3-connected case) and for several other special cases; open in general.",
))

entries.append(base(
    "wiki-turans-brick-factory-problem",
    "Turán's brick factory problem: is the minimum number of edge-crossings in any drawing of the complete bipartite graph K_{m,n} in the plane equal to the value given by Zarankiewicz's formula floor(m/2) floor((m-1)/2) floor(n/2) floor((n-1)/2)?",
    747,
    "forall-integers",
    "none",
    "unknown",
    known_cases="Zarankiewicz's formula is proved to be an upper bound (achieved by an explicit drawing) and is proved to be exactly correct when min(m,n) <= 6, and for a few other special cases (Kleitman proved it for min(m,n)<=6). Open in general.",
))

entries.append(base(
    "wiki-universal-point-sets-subquadratic",
    "Does there exist, for every n, a set of O(n^{2-epsilon}) points in the plane (for some fixed epsilon > 0) that is universal for n-vertex planar graphs, i.e. every planar graph on n vertices has a planar straight-line drawing with vertices placed at points of the set?",
    751,
    "exists-construction",
    "none",
    "unknown",
    known_cases="It is known that Theta(n^2) points are needed in the worst case for some drawing conventions, but the best known universal point set constructions use O(n^2) points and no truly subquadratic (n^{2-epsilon}) universal point set is known to exist for general planar graphs; whether one exists is open.",
))

entries.append(base(
    "wiki-barnettes-conjecture",
    "Barnette's conjecture: every 3-connected cubic bipartite planar graph has a Hamiltonian cycle.",
    758,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Verified computationally for all such graphs up to a few hundred vertices; no counterexample or general proof is known.",
))

entries.append(base(
    "wiki-chvatals-toughness-conjecture",
    "Chvátal's toughness conjecture: there exists a constant t_0 such that every t_0-tough graph is Hamiltonian (a graph is t-tough if removing any set S of vertices leaves at most |S|/t components).",
    759,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Known to be false if 'Hamiltonian' is replaced by some stronger properties for some toughness thresholds (there exist arbitrarily tough non-Hamiltonian graphs was disproved as stated originally by Bauer, Broersma, Veldman for t<9/4, but the existence of SOME t_0 making all t_0-tough graphs Hamiltonian remains open); a 2025 preprint verifies the conjecture for t>=4 for graphs meeting certain additional closure conditions.",
    notes="Precision caveat: Bauer-Broersma-Veldman showed no fixed t<9/4 suffices; whether some larger constant t_0 suffices is the part still open.",
))

entries.append(base(
    "wiki-cycle-double-cover-conjecture",
    "The cycle double cover conjecture: every bridgeless (2-edge-connected) graph has a collection of cycles (a 'cycle double cover') such that every edge of the graph belongs to exactly two cycles in the collection.",
    760,
    "forall-graphs",
    "none",
    "unknown",
))

entries.append(base(
    "wiki-erdos-gyarfas-conjecture",
    "The Erdős-Gyárfás conjecture: every cubic (3-regular) graph contains a simple cycle whose length is a power of two.",
    761,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Verified for several restricted graph classes (e.g. graphs without induced long paths, per a 2024 result), and via computer search on many small cubic graphs; open in general.",
))

entries.append(base(
    "wiki-linear-arboricity-conjecture",
    "The linear arboricity conjecture: every graph with maximum degree Delta can be decomposed into ceil((Delta+1)/2) edge-disjoint linear forests (forests each of whose components is a path).",
    762,
    "bound",
    "numeric-bound",
    "poly",
    known_cases="Proved for Delta<=6 and asymptotically (Delta/2 + o(Delta)) for large Delta by Ferber, Fischer, and others improving earlier estimates; the exact conjectured value ceil((Delta+1)/2) for every Delta remains open.",
))

entries.append(base(
    "wiki-oberwolfach-problem",
    "The Oberwolfach problem: for which 2-regular graphs F on n vertices can the complete graph K_n (n odd) be decomposed into edge-disjoint copies of F?",
    764,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Solved for many specific families of F (single cycles of every length, several disjoint-cycle-union cases) and, per a 2020s result of Glock, Joos, Kühn, Osthus (announced), for all sufficiently large n; small/exceptional cases and a fully uniform combinatorial answer remain open.",
))

entries.append(base(
    "wiki-babais-problem-invariant-groups",
    "Babai's problem: for a finite group G, call G a Babai invariant group if [precise defining property as stated at the source is not elaborated beyond the name]. Which finite groups are Babai invariant groups?",
    783,
    "other",
    "none",
    "unknown",
    notes="DROPPED FOR IMPRECISION: source gives only the name with no definition; cannot state exactly. Included here only as a record of the drop, not for corpus inclusion.",
))

entries.append(base(
    "wiki-brouwers-conjecture",
    "Brouwer's conjecture: for a graph G with m edges and Laplacian eigenvalues mu_1 >= mu_2 >= ... >= mu_n, the sum of the t largest Laplacian eigenvalues is at most m + binom(t+1, 2), for every t between 1 and n.",
    784,
    "bound",
    "numeric-bound",
    "poly",
    known_cases="Proved for several graph classes (trees, unicyclic graphs, split graphs, and for t=1,2,3 in general); open in general for arbitrary t and graphs.",
))

entries.append(base(
    "wiki-gnrs-conjecture",
    "The GNRS conjecture (Gupta-Newman-Rabinovich-Sinclair): a minor-closed family of graphs excluding some fixed graph as a minor admits an embedding into l_1 with distortion bounded by a constant depending only on the excluded minor, if and only if the family excludes some fixed minor at all (equivalently: every minor-closed family with an excluded minor has O(1)-distortion l_1 embeddings).",
    787,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Proved for series-parallel graphs and graphs of bounded treewidth; open for general minor-closed families (e.g. planar graphs, where it is a prominent open case).",
))

entries.append(base(
    "wiki-jorgensens-conjecture",
    "Jørgensen's conjecture: every 6-vertex-connected graph with no K_6 minor is an apex graph (a graph that becomes planar after removing one vertex).",
    803,
    "forall-graphs",
    "none",
    "unknown",
))

entries.append(base(
    "wiki-meyniels-conjecture",
    "Meyniel's conjecture: in the game of cops and robbers on a graph with n vertices, the cop number (minimum number of cops needed to guarantee capturing the robber) is O(sqrt(n)).",
    804,
    "bound",
    "numeric-bound",
    "poly",
    known_cases="The best known general upper bound is O(n / 2^{(1-o(1))sqrt(log2 n)}), which is subquadratic but far from sqrt(n); Meyniel's conjectured sqrt(n) bound remains open, verified only for special graph classes (e.g. graphs of diameter 2, some random graph models).",
))

entries.append(base(
    "wiki-reconstruction-conjecture",
    "The (Kelly-Ulam) reconstruction conjecture: every simple graph on 3 or more vertices is uniquely determined (up to isomorphism) by its deck, i.e. the multiset of its vertex-deleted subgraphs G - v for each vertex v.",
    820,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Proved for several restricted classes (e.g. regular graphs, disconnected graphs, trees); open in general.",
))

entries.append(base(
    "wiki-second-neighborhood-problem",
    "The second neighborhood problem (Seymour's conjecture): does every oriented graph (a directed graph with no 2-cycles) contain a vertex v such that the number of vertices at directed distance exactly 2 from v is at least the number of vertices at directed distance exactly 1 from v?",
    821,
    "exists-construction",
    "none",
    "unknown",
    known_cases="Proved for tournaments (Fisher; Chen-Shen; Havet-Thomassé have partial/related results) and several other special classes; open for general oriented graphs.",
))

entries.append(base(
    "wiki-moore-graph-girth5-degree57",
    "Does a Moore graph with girth 5 and vertex degree 57 exist? (A Moore graph of degree k and girth 5 has exactly k^2+1 vertices and is known to exist only for k in {2,3,7,57} by the Hoffman-Singleton theorem, with explicit examples known for k=2,3,7; existence for k=57 is undetermined.)",
    851,
    "exists-construction",
    "finite-object",
    "exponential",
    known_cases="The Hoffman-Singleton theorem (1960) restricts possible degrees to k in {2,3,7,57}; explicit Moore graphs are known for k=2 (pentagon), k=3 (Petersen graph), k=7 (Hoffman-Singleton graph); existence (or nonexistence) for k=57, which would have 3250 vertices, is unresolved despite extensive computer search.",
))

entries.append(base(
    "wiki-sumners-conjecture",
    "Sumner's conjecture: every tournament (complete directed graph) on 2n-2 vertices contains, as a subgraph, every oriented tree on n vertices.",
    823,
    "forall-integers",
    "none",
    "unknown",
    known_cases="Proved for all sufficiently large n by Kühn, Mycroft, and Osthus (2011); open (exact threshold and small/general n uniformly) as a fully general statement, and the precise universal constant/exact bound for all n is not established.",
    notes="Precision caveat noted in known_cases: asymptotic version is proved; the conjecture as stated for every n is still open per the source framing.",
))

entries.append(base(
    "wiki-tuttes-flow-conjectures",
    "Tutte's flow conjectures: (1) the 5-flow conjecture: every bridgeless graph has a nowhere-zero 5-flow (an assignment of edge directions and values in {±1,±2,±3,±4} with no value zero, satisfying flow conservation at every vertex). (2) The 4-flow conjecture: every bridgeless graph with no Petersen-graph minor has a nowhere-zero 4-flow.",
    845,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Seymour (1981) proved every bridgeless graph has a nowhere-zero 6-flow, the best known general result toward (1). Both the 5-flow and the Petersen-minor-free 4-flow conjectures remain open.",
))

entries.append(base(
    "wiki-zarankiewicz-problem",
    "The Zarankiewicz problem: let z(m,n;s,t) be the maximum number of edges in a bipartite graph with parts of size m and n that contains no complete bipartite subgraph K_{s,t}. Determine z(m,n;s,t) exactly for all m,n,s,t.",
    823,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Exact value known when s=2 or via the Kővári-Sós-Turán bound up to constant factors for general s,t, and exactly for several small (s,t) pairs (e.g. z(m,n;2,2)); the exact value for general s,t,m,n remains open.",
))

entries.append(base(
    "wiki-pathwidth-cubic-graphs",
    "What is the largest possible pathwidth of an n-vertex cubic (3-regular) graph, as a function of n?",
    852,
    "bound",
    "numeric-bound",
    "exponential",
    known_cases="Known upper and lower bounds of the form c1*n and c2*n (linear in n) with c1 < c2, i.e. the constant multiplying n is not pinned down exactly.",
))

# ---------------- MODEL THEORY / SET THEORY ----------------

entries.append(base(
    "wiki-cherlin-zilber-conjecture",
    "The Cherlin-Zilber algebraicity conjecture: every infinite simple group whose first-order theory is stable (in the model-theoretic sense, of Morley rank / stable of U-rank omega_0) is isomorphic to a simple algebraic group over an algebraically closed field.",
    882,
    "forall-graphs",
    "none",
    "unknown",
    known_cases="Proved in several special cases (e.g. for groups of finite Morley rank satisfying additional structural hypotheses, and the 'even type' case under further assumptions); open in full generality.",
))

entries.append(base(
    "wiki-generalized-star-height-problem",
    "The generalized star height problem: is there an algorithm to compute the generalized star height of a given regular language, i.e. the minimum nesting depth of Kleene star operations needed in a generalized regular expression (allowing complementation) that describes the language?",
    896,
    "other",
    "none",
    "unknown",
    known_cases="The (non-generalized) star height problem, without complementation, is known to be decidable (Hashiguchi, 1988). Decidability of the generalized star height problem (with complementation allowed) remains open; it is even open whether every regular language has generalized star height 0 or 1 versus higher (a related weaker open question).",
))

entries.append(base(
    "wiki-hilberts-tenth-for-number-fields",
    "For which number fields K does an analogue of Hilbert's tenth problem hold, i.e. for which K is there an algorithm to decide, given a polynomial equation with coefficients in the ring of integers of K, whether it has a solution in that ring of integers?",
    897,
    "other",
    "none",
    "unknown",
    known_cases="Known undecidable for the rationals (Matiyasevich-Robinson-Davis-Putnam, 1970) and for rings of integers of several specific families of number fields; the general question for arbitrary number fields (and specifically decidability status for many individual number fields) remains open.",
))

entries.append(base(
    "wiki-kuekers-conjecture",
    "Kueker's conjecture: if a first-order theory T is omega-stable (totally transcendental) and, for every model M of T, the number of complete types over the empty set realized in M is countable, then T has (up to isomorphism) only countably many countable models.",
    898,
    "other",
    "none",
    "unknown",
))

entries.append(base(
    "wiki-shelahs-categoricity-conjecture",
    "Shelah's categoricity conjecture for L_{omega_1,omega}: there is a cardinal (the 'Hanf number' for this logic) such that if a sentence of the infinitary logic L_{omega_1,omega} is categorical (has a unique model up to isomorphism) in some cardinal above that Hanf number, then it is categorical in every cardinal above that Hanf number.",
    913,
    "other",
    "none",
    "unknown",
    known_cases="Proved under additional set-theoretic hypotheses (e.g. assuming instances of the generalized continuum hypothesis, by Shelah and others); open in ZFC alone.",
))

entries.append(base(
    "wiki-stable-field-conjecture",
    "The stable field conjecture: every infinite field whose first-order theory (in the language of rings) is stable is separably closed.",
    984,
    "forall-graphs",
    "none",
    "unknown",
))

entries.append(base(
    "wiki-tarskis-exponential-function-problem",
    "Tarski's exponential function problem: is the first-order theory of the real numbers with the exponential function (the ordered field of reals augmented with exp) decidable?",
    986,
    "other",
    "none",
    "unknown",
    known_cases="Macintyre and Wilkie (1996) proved decidability conditional on Schanuel's conjecture. Unconditional decidability remains open.",
))

entries.append(base(
    "wiki-universality-spectrum-problem",
    "The universality spectrum problem: is there a first-order theory T whose universality spectrum (the class of cardinals kappa for which T has a universal model of size kappa) has a minimum element that is not simply the theory's own Löwenheim-Skolem number or a trivial bound, i.e. can the universality spectrum be genuinely irregular?",
    988,
    "other",
    "none",
    "unknown",
    notes="Statement kept close to source phrasing ('is there a first-order theory whose universality spectrum is minimum'); a specialist framing may differ slightly in emphasis.",
))

entries.append(base(
    "wiki-jonsson-algebra-aleph-omega",
    "Does there exist a Jónsson algebra on aleph_omega, i.e. an algebraic structure on a set of cardinality aleph_omega with countably many finitary operations such that every proper subalgebra has strictly smaller cardinality?",
    1350,
    "exists-construction",
    "none",
    "unknown",
))

# ---------------- NUMBER THEORY OUTLIERS ----------------

entries.append(base(
    "wiki-skolem-problem",
    "The Skolem problem: given a linear recurrence sequence of integers (u_n) defined by a fixed linear recurrence with integer/rational coefficients and initial terms, is there an algorithm to decide whether some term u_n equals 0?",
    1160,
    "other",
    "none",
    "unknown",
    known_cases="Decidable for linear recurrences of order <= 4 (via results using Baker's theorem on linear forms in logarithms, and other special structural results); decidability for order 5 and higher is open.",
    notes="Source mirror line gives only the bare name 'skolem problem'; statement reconstructed from the standard formulation. Treat with slightly lower confidence than fully-quoted entries.",
))

entries.append(base(
    "wiki-fontaine-mazur-conjecture",
    "The Fontaine-Mazur conjecture: an irreducible p-adic representation of the absolute Galois group of a number field that is unramified almost everywhere and 'geometric' (de Rham at places above p) arises from the etale cohomology of some algebraic variety over that number field.",
    1177,
    "other",
    "none",
    "unknown",
    notes="Source mirror line gives only the bare name 'fontaine–mazur conjecture'; statement reconstructed from the standard formulation.",
))

entries.append(base(
    "wiki-selbergs-eigenvalue-conjecture",
    "Selberg's 1/4 conjecture (Selberg's eigenvalue conjecture): every Maass cusp form for a congruence subgroup Gamma_0(N) of SL_2(Z) has Laplacian eigenvalue at least 1/4 (equivalently, the corresponding automorphic representation has no exceptional/complementary-series component).",
    1183,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Selberg himself proved the bound 3/16 (1965); this has since been improved (e.g. by Kim-Sarnak to roughly 0.238 = 7/64 using bounds toward Ramanujan-Petersson for GL(2) via GL(4) symmetric-power L-functions). The sharp conjectured constant 1/4 remains open.",
    notes="Source mirror line gives only the bare name 'selberg's 1/4 conjecture'; statement reconstructed from the standard formulation.",
))

entries.append(base(
    "wiki-lang-trotter-supersingular-primes",
    "The Lang-Trotter conjecture on supersingular primes: for a fixed elliptic curve E over Q without complex multiplication, the number of primes p <= x at which E has supersingular reduction is asymptotically C_E * sqrt(x) / log(x) for an explicit constant C_E depending on E.",
    1182,
    "bound",
    "numeric-bound",
    "unknown",
    notes="Source mirror line gives only the bare name 'lang and trotter's conjecture on supersingular primes' without the asymptotic formula spelled out; the C_E*sqrt(x)/log(x) asymptotic form given here is the standard formulation and should be checked against a primary source before being used as an attack target.",
))

entries.append(base(
    "wiki-hermites-problem",
    "Hermite's problem: does there exist a general algorithm (analogous to the continued fraction algorithm for real numbers, which detects quadratic irrationals via eventual periodicity) for representing real numbers by a sequence of integers, such that the sequence is eventually periodic exactly when the real number is a cubic irrational?",
    1180,
    "exists-construction",
    "none",
    "unknown",
    known_cases="Several candidate algorithms (e.g. the Jacobi-Perron algorithm and others) have been proposed and shown NOT to have the desired eventual-periodicity property for all cubic irrationals; whether any algorithm with the desired property exists remains open.",
    notes="Source mirror line gives only the bare name \"hermite's problem\"; statement reconstructed from the standard formulation.",
))

entries.append(base(
    "wiki-de-bruijn-newman-constant",
    "Find the exact value of the de Bruijn-Newman constant Lambda, defined via the family of entire functions H(lambda, z) (a deformation of the Riemann xi function) all of whose zeros are real if and only if lambda >= Lambda.",
    1142,
    "bound",
    "numeric-bound",
    "unknown",
    known_cases="Known that Lambda <= 0 (Rodgers-Tao, 2018/2020, confirming a conjecture of de Bruijn) and the Riemann hypothesis is equivalent to Lambda <= 0 combined with Lambda >= 0, i.e. RH is equivalent to Lambda = 0. It is known Lambda < 1/2 (de Bruijn) and Lambda <= 0 (Rodgers-Tao); the exact value of Lambda (equivalently, whether Lambda = 0, i.e. RH) is open.",
    notes="This is essentially a restatement of the Riemann Hypothesis in disguise; included as its own entry because it is posed as a numeric-bound problem (find Lambda) rather than a yes/no RH statement, consistent with the Millennium-problem ballast policy which covers RH itself separately.",
))

# ---------------- ballast: Millennium-adjacent (class D, per instructions) ----------------
entries.append({
    "id": "wiki-millennium-ballast",
    "source": "en.wikipedia.org/List_of_unsolved_problems_in_mathematics (via GitHub mirror)",
    "url": WIKI_URL,
    "provenance": clone_prov(10),
    "statement_nl": "Ballast entry per harvest policy: of the seven Millennium Prize Problems, six remain unsolved as of the source's writing (Birch-Swinnerton-Dyer, Hodge, Navier-Stokes existence/smoothness, P vs NP, Riemann Hypothesis, Yang-Mills existence/mass gap); the Poincaré conjecture was solved by Perelman. Not elaborated further per mining policy.",
    "statement_formal": None,
    "quantifier_shape": "other",
    "witness_type": "none",
    "witness_check_cost": "unknown",
    "known_cases": "",
    "current_bounds": {"lower": None, "upper": None},
    "prior_attempts": "",
    "prize": "Clay Millennium Prize, $1,000,000 each",
    "class": None,
    "tractability": None,
    "notes": "corpus ballast, class D",
})

# ---------------- filter out the deliberately-dropped precision entry ----------------
final = [e for e in entries if "DROPPED FOR IMPRECISION" not in e.get("notes", "")]
dropped_for_imprecision = [e for e in entries if "DROPPED FOR IMPRECISION" in e.get("notes", "")]

# dedupe by id
seen = set()
deduped = []
for e in final:
    if e["id"] in seen:
        raise SystemExit(f"DUPLICATE ID {e['id']}")
    seen.add(e["id"])
    deduped.append(e)

out_path = "/home/user/openproblem-miner/mine/corpus/raw/h3_curated.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for e in deduped:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print(f"wrote {len(deduped)} entries to {out_path}")
print(f"dropped for imprecision (not written): {len(dropped_for_imprecision)} -> {[e['id'] for e in dropped_for_imprecision]}")
