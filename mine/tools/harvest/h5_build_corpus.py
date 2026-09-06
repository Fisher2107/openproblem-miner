#!/usr/bin/env python3
"""H5 (graph-invariant conjecture generators) corpus builder.

Regenerate with:
    python3 mine/cache/h5_extract_lean.py \
        && python3 mine/cache/h5_build_corpus.py

Source 1: google-deepmind/formal-conjectures @ 8323e878b83fcd7f4a448256069352a265460d75,
          FormalConjectures/WrittenOnTheWallII/*.lean  (48 files, DeLaVina Graffiti.pc WOWII).
          statement_formal is extracted VERBATIM from the Lean file by h5_extract_lean.py.
Source 2: RandyRDavila/TxGraffiti2 @ e37126da53b84150d142a5d61202b61f78521fcc (docs .rst).
Source 3: WebSearch snippets (every remote host is blocked by the egress proxy; see
          mine/logs/NETWORK.md).  Marked provenance websearch:<url>.
"""
import json, os

COMMIT = "8323e878b83fcd7f4a448256069352a265460d75"
REPO = "google-deepmind/formal-conjectures"
WOWURL = "http://cms.dt.uh.edu/faculty/delavinae/research/wowII/"
SIGS = json.load(open("/home/user/openproblem-miner/mine/cache/h5_lean_sigs.json"))

NPHARD_NOTE = ("witness_check_cost is exponential in n in general because of NP-hard invariants "
               "[{}]; for n <= 11 the exact check is subset enumeration over <= 2^11 vertex sets "
               "and runs in milliseconds, so treat it as trivial inside the geng search range.")

# num -> dict(nl, npf=NP-hard invariants, known, prior, extra)
W = {}
def w(num, nl, npf, known="not stated at source", prior="", extra=""):
    W[num] = dict(nl=nl, npf=npf, known=known, prior=prior, extra=extra)

GL = ("Throughout: G is a finite simple connected graph, n(G)=|V(G)|; "
      "alpha(G) is the independence number (max size of a pairwise non-adjacent vertex set); "
      "l(v) is the LOCAL independence number of v, i.e. alpha of the subgraph induced on the OPEN "
      "neighbourhood N(v); l_avg(G)=l(G) is the average of l(v) over all n(G) vertices; "
      "Ls(G) is the maximum number of leaves over all spanning trees of G; "
      "b(G) is the maximum order of an induced bipartite subgraph; "
      "f(G) is the maximum order of an induced forest; "
      "tree(G) is the maximum order of an induced subgraph that is a tree; "
      "residue(G) is the Havel-Hakimi residue (number of zeros left when the Havel-Hakimi "
      "reduction of the degree sequence terminates); "
      "rad(G)/diam(G)/ecc(v) are radius, diameter and vertex eccentricity in the usual "
      "shortest-path metric.")

w("1", "For every finite simple connected graph G on n(G) vertices, Ls(G) >= n(G) + 1 - 2*mu(G), "
       "where Ls(G) is the maximum number of leaves over all spanning trees of G and mu(G) is the "
       "matching number (size of a maximum matching).",
   ["Ls"], known="Proved; Lean proof linked at source.",
   prior="formal_proof (lean4): github.com/MiskinAleksandr23/WOWII-1 @eda16f6e96b313bd112351ae9859133b77d537c9")
w("2", "For every finite simple connected graph G, Ls(G) >= 2*(l_avg(G) - 1), where Ls(G) is the "
       "maximum number of leaves over all spanning trees and l_avg(G) is the average over all "
       "vertices v of l(v) = the independence number of the subgraph induced on the open "
       "neighbourhood N(v).",
   ["Ls", "l(v)"], known="Proved (three independent Lean proofs linked at source).",
   prior="AlphaProof/Nexus (arXiv 2605.22763); formal proofs at google-deepmind/alphaproof-nexus-results, "
         "kingcharlezz/formal-conjectures, KitaKen1/wowii-graph-conjecture-2-lean")
w("3", "For every finite simple connected graph G, Ls(G) >= i(G) * MaxTemp(G), where Ls(G) is the "
       "maximum number of leaves over all spanning trees, i(G) is the independent domination number "
       "(minimum size of a set that is both independent and dominating), and "
       "MaxTemp(G) = max over vertices v of deg(v)/(n(G) - deg(v)), with the convention that the "
       "term is 0 when deg(v) = n(G).",
   ["Ls", "i(G)"], known="Proved (no external proof link recorded at source).")
w("4", "For every finite simple connected graph G, Ls(G) >= NG(G) - 1, where Ls(G) is the maximum "
       "number of leaves over all spanning trees and NG(G) is the minimum, over all non-edges "
       "{u,v} of G (unordered pairs of distinct non-adjacent vertices), of |N(u) union N(v)|; if G "
       "is complete (no non-edge) then NG(G) := n(G).",
   ["Ls"], known="Proved (no external proof link recorded at source).")
w("5", "For every finite simple connected graph G, Ls(G) >= max over centre vertices c of "
       "|{w : dist(c,w) = rad(G)}|, i.e. the largest sphere of radius rad(G) about a centre vertex, "
       "where a centre vertex is one whose eccentricity equals the radius and Ls(G) is the maximum "
       "number of leaves over all spanning trees.",
   ["Ls"], known="Proved (no external proof link recorded at source).")
w("6", "For every finite simple connected graph G, Ls(G) >= 1 + n(G) - mu(G) - alpha(G), where "
       "Ls(G) is the maximum number of leaves over all spanning trees, mu(G) the matching number, "
       "and alpha(G) the independence number.",
   ["Ls", "alpha"], known="Proved (no external proof link recorded at source).")
w("7", "For every finite simple connected graph G, Ls(G) >= max_v l(v) - 1 + n(G) - 2*alpha(G), "
       "where l(v) is the independence number of the subgraph induced on the open neighbourhood "
       "N(v), alpha(G) is the independence number and Ls(G) is the maximum number of leaves over "
       "all spanning trees.",
   ["Ls", "alpha", "l(v)"], known="Proved by DeLaVina, Fajtlowicz and Waller (2002), per the source docstring.")
w("13", "For every finite simple connected graph G, b(G) >= diam(G) + max_v l(v) - 1, where b(G) is "
        "the maximum order of an induced bipartite subgraph, diam(G) is the diameter, and l(v) is "
        "the independence number of the subgraph induced on the open neighbourhood N(v).",
   ["b", "l(v)"], known="Proved (no external proof link recorded at source).")
w("16", "For every finite simple connected graph G, b(G) >= 2*(rad(G) - 1) + max_v l(v), where b(G) "
        "is the maximum order of an induced bipartite subgraph, rad(G) is the radius (minimum "
        "eccentricity) and l(v) is the independence number of the subgraph induced on N(v).",
   ["b", "l(v)"], known="Proved (no external proof link recorded at source).")
w("17", "For every finite simple connected graph G, b(G) >= alpha(G) + ceil(diam(G)/3), where b(G) "
        "is the maximum order of an induced bipartite subgraph, alpha(G) the independence number "
        "and diam(G) the diameter.",
   ["b", "alpha"], known="Proved by Schindl, per the docstring of conjecture 18 at source.")
w("18", "For every finite simple connected graph G, b(G) >= alpha(G) + ceil(sqrt(dist_max(M))), "
        "where b(G) is the maximum order of an induced bipartite subgraph, alpha(G) the "
        "independence number, M = {v : deg(v) = maxDegree(G)} the set of maximum-degree vertices, "
        "and dist_max(M) = max{dist(u,v) : u,v in M} (0 if |M| <= 1).",
   ["b", "alpha"], known="Proved by Benny John (Feb. 2006), generalising Schindl's proof of conjecture 17.")
w("19", "For every finite simple connected graph G on at least two vertices, "
        "b(G) >= floor( (sum over v of ecc(v))/n(G) + max_v l(v) ), where b(G) is the maximum order "
        "of an induced bipartite subgraph, ecc(v) is the eccentricity of v, and l(v) is the "
        "independence number of the subgraph induced on the open neighbourhood N(v).",
   ["b", "l(v)"])
w("20", "For every finite simple connected graph G, b(G) >= n(G) / floor(deg_avg(G)), where b(G) is "
        "the maximum order of an induced bipartite subgraph and deg_avg(G) = (sum_v deg(v))/n(G) is "
        "the average degree.",
   ["b"], known="Proved (no external proof link recorded at source).")
w("23", "REFUTED. It was conjectured that for every finite simple connected graph G, "
        "b(G) >= floor( alpha(G) + dist_avg(M)/2 ), where b(G) is the maximum order of an induced "
        "bipartite subgraph, alpha(G) the independence number, M = {v : deg(v) = maxDegree(G)}, and "
        "dist_avg(M) = (1/n(G)) * sum over all vertices u of dist(u, M) with dist(u,M) the minimum "
        "distance from u to a vertex of M.",
   ["b", "alpha"], known="False. Source records a counterexample with b(G)=19, alpha(G)=15, dist_avg(M)=10.")
w("31", "For every finite simple connected graph G, path(G) >= 2*rad(G) - 1, where rad(G) is the "
        "radius. WARNING: in the Lean development path(G) is SimpleGraph.path, defined in "
        "FormalConjecturesForMathlib/.../VertexDistance.lean as the maximum order of an induced "
        "path of G, while the docstring of this file describes path(G) as the floor of the average "
        "distance. The two readings are NOT equivalent; see notes.",
   ["path"], known="This is Chung's theorem (F.R.K. Chung, The average distance and the independence number, "
                   "J. Graph Theory 12 (1988) 229-235) under the average-distance reading.",
   extra="AMBIGUITY: docstring says 'floor of the average distance', the Lean def SimpleGraph.path says "
         "'number of vertices of a largest induced path'. Resolve before building a checker.")
w("32", "REFUTED. It was conjectured that for every finite simple connected graph G, "
        "path(G) >= dist_avg(A) + 0.5*ecc_avg(M), where A = {v : deg(v)=minDegree(G)}, "
        "M = {v : deg(v)=maxDegree(G)}, dist_avg(A) = (1/n) sum_u dist(u,A), and ecc_avg(M) is the "
        "average eccentricity of the vertices of M. path(G) is SimpleGraph.path (see notes on the "
        "path ambiguity).",
   ["path"], known="False. Source: 'The path on 5 vertices is a counterexample, path = 5, distavg(A) = 4 "
                   "and the average of eccentricity of maximum degree vertices is 8/3.'",
   extra="AMBIGUITY: same path(G) reading conflict as conjecture 31.")
w("33", "REFUTED. It was conjectured that for every finite simple connected graph G, "
        "path(G) >= ceil(2*dist_avg(M)) where M = {v : deg(v)=maxDegree(G)} and "
        "dist_avg(M) = (1/n) sum over all vertices u of dist(u,M). path(G) is SimpleGraph.path "
        "(see notes on the path ambiguity).",
   ["path"], known="Recorded as False at source (answer(False)); no counterexample exhibited in the file.",
   extra="AMBIGUITY: same path(G) reading conflict as conjecture 31.")
w("34", "STATUS UNRESOLVED IN THE SOURCE FILE. It is asked whether for every finite simple connected "
        "graph G, path(G) >= ceil( dist_avg(C) + dist_avg(M) ), where C = center(G) is the set of "
        "minimum-eccentricity vertices, M = {v : deg(v)=maxDegree(G)}, and dist_avg(S) = "
        "(1/n) sum over all vertices u of dist(u,S). path(G) is SimpleGraph.path.",
   ["path"], known="Tagged 'research solved' in Lean but the answer slot is literally answer(sorry): the "
                   "file carries a TODO saying the True/False answer has not been recorded.",
   extra="AMBIGUITY: same path(G) reading conflict as conjecture 31. Also the tag/answer mismatch means "
         "the 'solved' label here is unreliable.")
w("36", "REFUTED. It was conjectured that for every finite simple connected graph G with at least one "
        "diametrical pair, path(G) >= 2*rad(G)/dp(G), where dp(G) is the number of unordered pairs "
        "{u,v} of distinct vertices with dist(u,v) = diam(G). path(G) is SimpleGraph.path.",
   ["path"], known="Disproved by Waller in Oct 2003 (counterexample with path number 5, radius 3, dp 1).",
   extra="AMBIGUITY: same path(G) reading conflict as conjecture 31.")
w("40", "For every finite simple connected graph G on at least two vertices, "
        "f(G) >= ceil( (p(G) + b(G) + 1)/2 ), where f(G) is the maximum order of an induced forest, "
        "b(G) is the maximum order of an induced bipartite subgraph, and p(G) is the path cover "
        "number: the minimum number of vertex-disjoint paths whose vertex sets cover V(G).",
   ["f", "b", "p (path cover)"])
w("58", "REFUTED. It was conjectured that for every finite simple connected graph G, "
        "f(G) >= ceil( b(G)/l_avg(G) ), where f(G) is the maximum order of an induced forest, b(G) "
        "the maximum order of an induced bipartite subgraph, and l_avg(G) the average over vertices "
        "v of l(v) = alpha(G[N(v)]).",
   ["f", "b", "l(v)"],
   known="False. Counterexample on n=79: K_{3,3} on {0..5} plus K_73 on {6..78}, with vertex 0 joined to "
         "every vertex of the K_73. Then b>=7, f<=6, l_avg = 92/79, ceil(b/l_avg) >= 7 > 6 >= f.",
   prior="Counterexample found by Moritz Firsching and Goran Zuzic with an experimental pipeline; "
         "formal proof at mo271/formal-conjectures @4bd72a06842a10e1b8d7bb0fd6b1ef5e6bd20210")
w("59", "REFUTED. It was conjectured that for every finite simple connected graph G, "
        "f(G) >= ceil( sqrt( residue(G) * b(G) ) ), where f(G) is the maximum order of an induced "
        "forest, residue(G) the Havel-Hakimi residue, and b(G) the maximum order of an induced "
        "bipartite subgraph.",
   ["f", "b"],
   known="False. Connected counterexample on 123 vertices with residue = 101, b = 122, f = 111; "
         "101*122 = 12322 = 111^2 + 1, so the conjectured bound is 112.",
   prior="formal_proof (lean4): github.com/QDKStorm/wowii59-counterexample")
w("61", "For every finite simple connected graph G, f(G) >= residue(G) + ceil(diam(G)/3), where f(G) "
        "is the maximum order of an induced forest, residue(G) the Havel-Hakimi residue of the "
        "degree sequence, and diam(G) the diameter.",
   ["f"], known="not stated at source; residue reference is Favaron, Maheo, Sacle (1991)")
w("63", "REFUTED. It was conjectured that for every finite simple connected graph G, "
        "f(G) >= ceil( (min_v distEven(v) + b(G) + 1)/3 ), where f(G) is the maximum order of an "
        "induced forest, b(G) the maximum order of an induced bipartite subgraph, and "
        "distEven(v) = |{w : dist(v,w) is even}| (v itself counts, distance 0 being even).",
   ["f", "b"],
   known="False, witnessed by the lexicographic product C_5[K_4]: min_v distEven(v) = 9, f = b = 4, so the "
         "conjectured bound is ceil((9+4+1)/3) = 5 > 4.",
   prior="formal_proof (lean4): github.com/Kuberwastaken/wowii-63-85-counterexample")
w("65", "REFUTED. It was conjectured that for every finite simple connected graph G, "
        "f(G) >= dist_min(A) + ceil(dist_min(M)/3), where f(G) is the maximum order of an induced "
        "forest, A = {v : deg(v)=minDegree(G)}, M = {v : deg(v)=maxDegree(G)}, and "
        "dist_min(S) = min{dist(u,v) : u,v in S, u != v} (0 if |S| < 2).",
   ["f"],
   known="False. Counterexample on 17 vertices (graph6 PhCGGC@?G?_@?@O?G?G?G?@C): the path v0..v12 with a "
         "triangle attached at v1 and another at v11; dist_min(A)=12, dist_min(M)=10, conjectured bound 16, "
         "but f = 15. The Lean file contains a complete kernel-checked refutation.",
   prior="Refutation proved inline in the source file (no sorry).")
w("85", "REFUTED. It was conjectured that for every finite simple connected graph G, "
        "tree(G) >= ceil( sqrt( 1 + 2*min_v distEven(v) ) ), where tree(G) is the maximum order of "
        "an induced subgraph that is a tree and distEven(v) = |{w : dist(v,w) is even}|.",
   ["tree"],
   known="False, witnessed by C_5[K_4]: min_v distEven(v) = 9 and tree = 4, while ceil(sqrt(19)) = 5.",
   prior="formal_proof (lean4): github.com/Kuberwastaken/wowii-63-85-counterexample")
w("100", "For every finite simple connected graph G, "
         "alpha(G) <= ceil( ( max_v l(v) + 0.5*length(complement of G) ) / 2 ), where alpha(G) is the "
         "independence number, l(v) = alpha(G[N(v)]) is the local independence number taken in G, and "
         "length(H) = sqrt( sum over v of deg_H(v)^2 ) is the Euclidean norm of the degree sequence of "
         "H, evaluated on the complement of G.",
   ["alpha", "l(v)"],
   known="WOWII status O (open). The file notes that an earlier extraction dropped the complement bar; the "
         "complement reading is the one stated here.")
w("101", "For every finite simple connected graph G, alpha(G) <= floor( (n(G) + |alphaCore(G)|)/2 ), "
         "where alpha(G) is the independence number and alphaCore(G) = {v : alpha(G - v) < alpha(G)} "
         "is the set of vertices whose deletion strictly decreases the independence number (G - v is "
         "the subgraph induced on V(G) \\ {v}).",
   ["alpha", "alphaCore"], known="Recorded at source as a theorem following from inclusion-exclusion principles.")
w("103", "REFUTED. It was conjectured that for every finite simple connected graph G, "
         "alpha(G) <= floor( b(G) - ln(ecc_avg(G)) ), where alpha(G) is the independence number, b(G) "
         "the maximum order of an induced bipartite subgraph, ecc_avg(G) = (1/n) sum_v ecc(v) the "
         "average eccentricity, and ln the natural logarithm.",
   ["alpha", "b"],
   known="False. Counterexample on 11 vertices: a triangle {0,1,2} with four pendant vertices at 0 and four "
         "at 1; alpha = 9, b = 10, ecc_avg = 30/11, and 1 < ln(30/11) < 2 so the bound is 8.",
   prior="Refutation proved inline in the source file (no sorry).")
w("109", "REFUTED. It was conjectured that for every finite simple connected graph G, "
         "alpha(G) <= floor( (residue(G) + 2*b(G))/3 ), where alpha(G) is the independence number, "
         "residue(G) the Havel-Hakimi residue and b(G) the maximum order of an induced bipartite "
         "subgraph.",
   ["alpha", "b"],
   known="False. Smallest counterexample recorded: the connected 13-vertex graph "
         "complement(K_7) join (K_3 disjoint-union K_3), with alpha = 7, residue = 2, b = 9, so the bound "
         "is 6. A 21-vertex counterexample (alpha 15, residue 8, b <= 18) is also recorded.",
   prior="formal proofs at DomTheDeveloper/formal-conjectures and chelokot/wowii-109-counterexample")
w("133", "For every finite simple connected graph G, path(G) >= rad(G) + floor(l_avg(G))^{cC4(G)}, "
         "where path(G) is the maximum order of an induced path, rad(G) the radius, l_avg(G) the "
         "average over vertices v of l(v) = alpha(G[N(v)]), and cC4(G) = 1 if G contains no cycle of "
         "length 4 (not necessarily induced) and 0 otherwise.",
   ["path", "l(v)"],
   known="not stated at source",
   extra="This file reads path(G) as the largest induced path order, matching the Lean definition of "
         "SimpleGraph.path; conjectures 31-36 read the same symbol as floor of average distance. "
         "The bracket notation [average of lambda(v)] is read as floor, a Graffiti.pc convention.")
w("141", "For every finite simple connected graph G, tree(G) >= floor(girth(G)/2) - 1 + max_v l(v), "
         "where tree(G) is the maximum order of an induced subgraph that is a tree, girth(G) is the "
         "length of a shortest cycle (0 if G is acyclic), and l(v) = alpha(G[N(v)]).",
   ["tree", "l(v)"],
   known="not stated at source",
   extra="A 2026 preprint (arXiv 2608.01396, 'Three Graffiti.pc Conjectures on Largest Induced Trees: "
         "Proofs of Conjectures 141, 142, and 143') claims a proof; the pinned formal-conjectures commit "
         "still tags 141 'research open'. Check prior art before spending. arXiv is blocked here so this "
         "claim is from a WebSearch title only.")
w("142", "For every finite simple connected graph G, tree(G) >= (2/3)*girth(G) + eccSet(G, B), where "
         "tree(G) is the maximum order of an induced tree, girth(G) the length of a shortest cycle "
         "(0 if acyclic), B the set of vertices of maximum eccentricity (the periphery), and "
         "eccSet(G,S) = max over ALL vertices u of dist(u,S) (vertices in S contribute 0).",
   ["tree"], known="Proved; a Lean formalization is linked at source.",
   prior="formal_proof: AlperTheKing/formal-conjectures @46bf39015f5c3c3ba3bfcf9f752b4b1e49b584ac")
w("143", "For every finite simple connected graph G with second-smallest degree sigma(G) > 0, "
         "girth(G) + 1 <= tree(G) * sigma(G) (the denominator-free form of tree(G) >= "
         "(girth(G)+1)/sigma(G)), where tree(G) is the maximum order of an induced tree, girth(G) is "
         "the length of a shortest cycle, and sigma(G) is the second entry of the degree sequence "
         "sorted in non-decreasing order (0 by convention when n <= 1).",
   ["tree"], known="Proved; a Lean formalization is linked at source.",
   prior="formal_proof: DomTheDeveloper/formal-conjectures @693e9aa206a5c6c98598aa4e6e5f3db0994a79b7")
w("144", "For every finite simple connected graph G, tree(G) >= girth(G) - 1 + ecc(G, center(G)), "
         "where tree(G) is the maximum order of an induced tree, girth(G) the length of a shortest "
         "cycle (0 if acyclic), center(G) the set of minimum-eccentricity vertices, and ecc(G,S) = "
         "max over vertices u NOT in S of dist(u,S) (0 when S = V).",
   ["tree"], known="Proved; a Lean formalization is linked at source.",
   prior="formal_proof (lean4): beowulf127/wowii144-lean @046429d509b28c90ee2ec38ae27c1ad377c6a5fc")
w("145", "For every finite simple connected graph G whose complement has positive minimum local "
         "independence number, 2*eccSet(G, B) <= tree(G) * lMin(complement of G), the "
         "denominator-free form of tree(G) >= 2*eccSet(G,B)/lMin(complement of G). Here tree(G) is "
         "the maximum order of an induced tree, B is the set of maximum-eccentricity vertices, "
         "eccSet(G,S) = max over all vertices u of dist(u,S), and lMin(H) = min over vertices v of "
         "alpha(H[N_H(v)]).",
   ["tree"], known="Proved by Dominic Dabish; Lean proof linked at source.",
   prior="formal_proof (lean4): DomTheDeveloper/crl @2ee448baa80c98f0c8b9a0c1c3d9421200f99aa5")
w("146", "For every finite simple connected graph G with rad(G^2) > 0, "
         "2*eccSet(G, B) <= tree(G) * rad(G^2), the denominator-free form of "
         "tree(G) >= 2*eccSet(G,B)/rad(G^2). Here G^2 is the square of G (distinct u,v adjacent iff "
         "dist_G(u,v) <= 2), rad(G^2) its radius, tree(G) the maximum order of an induced tree, and "
         "B the set of maximum-eccentricity vertices.",
   ["tree"], known="Proved; Lean proof linked at source.",
   prior="formal_proof (lean4): akakabrian/WOW-146 @f9e0ad75d829170804ce1d8f9fd4c1d4a0085203")
w("160", "For every finite simple connected graph G, Ls(G) >= max_v l(v) + (max_v T(v)) * cC4(G), "
         "where Ls(G) is the maximum number of leaves over all spanning trees, l(v) = alpha(G[N(v)]) "
         "is the local independence number, T(v) is the number of triangles of G containing v "
         "(equivalently the number of adjacent pairs inside N(v)), and cC4(G) = 1 if G has no cycle "
         "of length 4 (not necessarily induced) and 0 otherwise.",
   ["Ls", "l(v)"],
   known="not stated at source",
   extra="An earlier revision of this file used the COUNT of induced 4-cycles; the historical conjecture "
         "uses the binary C4-free indicator, which is what the pinned statement encodes.")
w("194", "REFUTED. It was conjectured that every finite simple connected graph G with "
         "alpha(G) <= 1 + l_avg(G) has a Hamiltonian path, where alpha(G) is the independence number "
         "and l_avg(G) is the average over vertices v of l(v) = alpha(G[N(v)]).",
   ["alpha", "l(v)", "Hamiltonian path"],
   known="False. 18-vertex counterexample (graph6 Q~~~~~~~~~~~~}~}^~??G??_??_): K_11 on {0..10}, four "
         "vertices 11..14 each joined to every clique vertex, and a pendant vertex at each of 11, 12 and 14. "
         "alpha = 4, sum of l(v) = 54 so l_avg = 3, hypothesis holds with equality, but three pendant "
         "vertices forbid a Hamiltonian path.",
   prior="formal_proof: anagnorisis2peripeteia/formal-conjectures @4bff865a14c2cd61fefbffbe9c49cbfc5a89ac45")
w("198a", "For every finite simple connected graph G on at least two vertices, if "
          "b(G) <= 2 + ecc_avg(G) then G has a Hamiltonian path, where b(G) is the maximum order of "
          "an induced bipartite subgraph and ecc_avg(G) = (1/n) sum_v ecc(v) is the average "
          "eccentricity.",
   ["b", "Hamiltonian path"])
w("200", "REFUTED. It was conjectured that every finite simple connected graph G with "
         "tree(G) = ceil(1 + l_avg(G)) has a Hamiltonian path, where tree(G) is the maximum order of "
         "an induced tree and l_avg(G) the average over vertices v of l(v) = alpha(G[N(v)]).",
   ["tree", "l(v)", "Hamiltonian path"],
   known="False. An infinite family indexed by q >= 5 is given at source; its smallest member has 11 "
         "vertices, graph6 J??FFBRq}N_. The source states this is a smallest counterexample: an exhaustive "
         "nauty geng search over all 11,989,760 connected graphs with 4 <= n <= 10 found none.",
   prior="formal_proof: infinityscroll/formal-conjectures @9dd290db402c49922fa42793e4a7cfb802daf5c1")
w("217", "For every finite simple connected graph G on n > 1 vertices, if "
         "Ls(G) <= 4*chi_{residue=2}(G) + 2 then G has a Hamiltonian path, where Ls(G) is the maximum "
         "number of leaves over all spanning trees and chi_{residue=2}(G) is 1 if residue(G) = 2 and "
         "0 otherwise.",
   ["Ls", "Hamiltonian path"], known="Proved; Lean audit linked at source.",
   prior="formal_proof (lean4): KitaKen1/wowii-graph-conjecture-217-lean @6a2fb82fcd17aa15ec734736740794bb8bd194c0")
w("291", "For every finite simple connected graph G with n(G) > 2, "
         "gamma_t(G) <= k(G) + freq_min_T(G), where gamma_t(G) is the total domination number "
         "(minimum size of a set D such that every vertex of G has a neighbour in D), "
         "T(v) is the number of triangles of G containing v, freq_min_T(G) = |{v : T(v) = min_u T(u)}| "
         "is the number of vertices attaining the minimum triangle count, and k(G) is the FIRST index "
         "i >= 0 at which the i-th Havel-Hakimi iterate of the descending degree sequence of G "
         "contains a zero entry (or has become the empty list).",
   ["gamma_t", "freq_min_T is poly"],
   known="not stated at source",
   extra="k(G) is explicitly NOT n - residue(G): it is the first step at which SOME entry hits zero, not "
         "the total number of reduction steps. The source file spells this out because the distinction is "
         "easy to get wrong.")
w("314", "For every finite simple connected graph G on at least two vertices, if G is triangle-free "
         "and its largest induced path has at most 4 vertices, then G is well totally dominated "
         "(every minimal total dominating set of G has the same cardinality). A total dominating set "
         "is a set D with every vertex of G having a neighbour in D; it is minimal if no proper "
         "subset is total dominating.",
   ["largest induced path", "well totally dominated"],
   known="not stated at source",
   extra="The file explicitly warns that earlier revisions used SimpleGraph.path (documented there as floor "
         "of average distance) and that the intended invariant is the size of a largest induced path, "
         "defined locally in the file as largestInducedPathSize.")
w("315", "For every finite simple connected graph G, if alpha(G) = |P(G)| where P(G) is the set of "
         "pendant vertices (vertices of degree 1) and alpha(G) is the independence number, then G is "
         "well totally dominated.",
   ["alpha", "well totally dominated"], known="Proved; Lean proof linked at source.",
   prior="Formal proof by Goran Zuzic and Moritz Firsching (experimental pipeline); "
         "mo271/formal-conjectures @9ef80e1a3709ed3eda43d9ed6ff1087681621041")
w("316", "For every finite simple connected graph G, if |P(G)| >= deg_avg(complement of G), where "
         "P(G) is the set of pendant (degree-1) vertices of G and deg_avg(H) = (sum_v deg_H(v))/n is "
         "the average degree of H, then G is well totally dominated.",
   ["well totally dominated"], known="Proved; Lean proof linked at source.",
   prior="formal_proof (lean4): KitaKen1/wowii-graph-conjecture-316-lean @3335e07151bc43e86d5c104dd30fee3596f06410")
w("322", "For every finite simple connected graph G on n >= 5 vertices, if every vertex v satisfies "
         "l_complement(v) <= 1, where l_complement(v) is the independence number of the subgraph of "
         "the complement of G induced on the open neighbourhood of v IN THE COMPLEMENT, then G is "
         "well totally dominated.",
   ["well totally dominated"],
   known="Proved by Samuel Schlesinger; the proof is given inline in the source file (no sorry).")
w("327", "REFUTED. It was conjectured that every finite simple connected graph G with "
         "3*gamma(G) = i(G) is well totally dominated, where gamma(G) is the domination number and "
         "i(G) the independent domination number.",
   ["gamma", "i(G)", "well totally dominated"],
   known="False. 12-vertex counterexample given at source on {u,v,a_0..a_4,b_0..b_4} with edges uv, u a_i "
         "(all i), v b_i (all i), a_0 b_3, a_1 b_3, a_2 b_0, a_3 b_0, a_4 b_3, a_4 b_4. Then gamma = 2, "
         "i = 6, so 3*gamma = i, yet {u,v} and {v,b_0,b_3} are minimal total dominating sets of "
         "different sizes.",
   prior="Counterexample by Moritz Firsching and Goran Zuzic; "
         "mo271/formal-conjectures @6e85aabe821e6ddf718d050a5bd8f19a48e4f2d9")

entries = []
missing = []
for num, s in SIGS.items():
    if num not in W:
        missing.append(num); continue
    d = W[num]
    status = s["status"]
    notes = ["status in Lean @[category ...]: research " + status,
             "graph glossary: " + GL,
             NPHARD_NOTE.format(", ".join(d["npf"]))]
    if d["extra"]:
        notes.append(d["extra"])
    notes.append("statement_formal is the Lean theorem signature copied verbatim from the cited file "
                 "(some hypotheses live in the file's `variable` line, so read the file for full context).")
    entries.append({
        "id": "wow2-" + num,
        "source": "formal-conjectures/WrittenOnTheWallII (E. DeLaVina, Written on the Wall II: Conjectures of Graffiti.pc)",
        "url": WOWURL,
        "provenance": f"clone:{REPO}@{COMMIT}:FormalConjectures/WrittenOnTheWallII/{s['file']}",
        "statement_nl": d["nl"],
        "statement_formal": s["signature"],
        "quantifier_shape": "forall-graphs",
        "witness_type": "finite-object",
        "witness_check_cost": "exponential",
        "known_cases": d["known"],
        "current_bounds": {"lower": None, "upper": None},
        "prior_attempts": d["prior"],
        "prize": None,
        "class": None,
        "tractability": None,
        "notes": " || ".join(notes),
    })

# ---- Source 2/3: Graffiti and TxGraffiti ----
TX2 = "clone:RandyRDavila/TxGraffiti2@e37126da53b84150d142a5d61202b61f78521fcc:docs/source/history_with_txgraffiti/graffiti/index.rst#L50-L58"
extra = [
 {"id":"graffiti-1",
  "source":"Fajtlowicz's Graffiti (as reproduced in the TxGraffiti2 documentation)",
  "url":"https://github.com/RandyRDavila/TxGraffiti2",
  "provenance":TX2,
  "statement_nl":"For every finite simple connected graph G, alpha(G) >= residue(G), where alpha(G) is the "
    "independence number and residue(G) is the Havel-Hakimi residue: repeatedly delete the largest degree d "
    "from the non-increasing degree sequence and subtract 1 from each of the next d entries, until all "
    "remaining entries are 0; residue(G) is the number of zeros left.",
  "statement_formal":None,
  "quantifier_shape":"forall-graphs","witness_type":"finite-object","witness_check_cost":"exponential",
  "known_cases":"Source calls it 'one of the two most well known conjectures of Graffiti' and does not record "
    "its status. It is widely attributed as proved by Favaron, Maheo and Sacle (1991), the same reference the "
    "formal-conjectures WOWII files cite for the residue; that attribution is NOT verified from a primary "
    "source in this container.",
  "current_bounds":{"lower":None,"upper":None},
  "prior_attempts":"See the residue references in mine/cache/formal-conjectures/.../Residue.lean",
  "prize":None,"class":None,"tractability":None,
  "notes":"status: almost certainly NOT open (believed a theorem); harvested as calibration / checker test "
    "material only. alpha is NP-hard, residue is O(n^2 log n). || Verified by exhaustive geng search it should "
    "hold for all n <= 10."},
 {"id":"graffiti-3",
  "source":"Fajtlowicz's Graffiti (as reproduced in the TxGraffiti2 documentation)",
  "url":"https://github.com/RandyRDavila/TxGraffiti2",
  "provenance":TX2,
  "statement_nl":"For every finite simple connected graph G, alpha(G) >= rad(G), where alpha(G) is the "
    "independence number and rad(G) is the radius (the minimum over vertices v of the eccentricity of v, "
    "eccentricity being the maximum shortest-path distance from v to any vertex).",
  "statement_formal":None,
  "quantifier_shape":"forall-graphs","witness_type":"finite-object","witness_check_cost":"exponential",
  "known_cases":"Source calls it 'one of the two most well known conjectures of Graffiti' and does not record "
    "its status.",
  "current_bounds":{"lower":None,"upper":None},
  "prior_attempts":"",
  "prize":None,"class":None,"tractability":None,
  "notes":"status not recorded at source; widely believed/known to be a theorem. Harvested as calibration / "
    "checker test material. alpha is NP-hard; rad is O(n*m) by BFS from every vertex."},
 {"id":"txgraffiti-alpha-z-cubic",
  "source":"TxGraffiti (Davila), the 'alpha-Z conjecture'",
  "url":"https://arxiv.org/abs/2607.23664",
  "provenance":"websearch:https://arxiv.org/abs/2607.23664",
  "statement_nl":"For every connected cubic (3-regular) finite simple graph G with G != K_4, "
    "Z(G) <= alpha(G) + 1, where Z(G) is the zero forcing number (minimum size of a set S of initially "
    "coloured vertices such that iterating the rule 'a coloured vertex with exactly one uncoloured neighbour "
    "forces that neighbour to become coloured' eventually colours V(G)) and alpha(G) is the independence "
    "number.",
  "statement_formal":None,
  "quantifier_shape":"forall-graphs","witness_type":"finite-object","witness_check_cost":"exponential",
  "known_cases":"Partial result recorded in the search result: Z(G) <= alpha(G)+1 holds whenever G != K_4 is "
    "connected, cubic and claw-free. Reported REFUTED in 2026 by a connected cubic counterexample on 36 "
    "vertices with alpha = 15 and Z = 17.",
  "current_bounds":{"lower":None,"upper":None},
  "prior_attempts":"Conjectured by TxGraffiti in 2017; several partial results; counterexample announced in "
    "arXiv:2607.23664 (title: 'A counterexample to the zero forcing versus independence conjecture for cubic "
    "and subcubic graphs').",
  "prize":None,"class":None,"tractability":None,
  "notes":"status: reported SOLVED (refuted) in 2026. Provenance is a WebSearch summary only: arxiv.org is "
    "blocked by the egress proxy in this container, so the statement was NOT read from the paper. Search "
    "query: 'TxGraffiti open conjecture independence number matching number cubic graph zero forcing number "
    "conjecture statement'. Both Z and alpha are NP-hard; for n <= 11 both are brute-forceable."},
 {"id":"txgraffiti-alpha-z-subcubic",
  "source":"TxGraffiti (Davila), subcubic form of the alpha-Z conjecture",
  "url":"https://arxiv.org/abs/2607.23664",
  "provenance":"websearch:https://arxiv.org/abs/2607.23664",
  "statement_nl":"For every connected finite simple graph G with maximum degree at most 3 (subcubic) and "
    "G != K_4, Z(G) <= alpha(G) + 1, where Z(G) is the zero forcing number and alpha(G) the independence "
    "number.",
  "statement_formal":None,
  "quantifier_shape":"forall-graphs","witness_type":"finite-object","witness_check_cost":"exponential",
  "known_cases":"Reported REFUTED in 2026 by a connected counterexample on 24 vertices with maximum degree 3, "
    "alpha = 9 and Z = 11.",
  "current_bounds":{"lower":None,"upper":None},
  "prior_attempts":"arXiv:2607.23664",
  "prize":None,"class":None,"tractability":None,
  "notes":"status: reported SOLVED (refuted) in 2026. WebSearch-summary provenance only (arxiv blocked). The "
    "exact hypothesis (whether K_4 is excluded in the subcubic form) was not verifiable here - confirm "
    "against the paper before using. NP-hard invariants: Z, alpha."},
 {"id":"txgraffiti-alpha-mu-regular",
  "source":"TxGraffiti (Davila), 'Conjectures of TxGraffiti: Independence, domination, and matchings'",
  "url":"https://arxiv.org/abs/2104.01092",
  "provenance":"websearch:https://arxiv.org/abs/2104.01092",
  "statement_nl":"For every finite simple regular graph G, alpha(G) <= mu(G), where alpha(G) is the "
    "independence number and mu(G) is the matching number (the size of a maximum matching).",
  "statement_formal":None,
  "quantifier_shape":"forall-graphs","witness_type":"finite-object","witness_check_cost":"exponential",
  "known_cases":"Reported at source as an established result (theorem) rather than an open conjecture.",
  "current_bounds":{"lower":None,"upper":None},
  "prior_attempts":"arXiv:2104.01092 / Australas. J. Combin. 84 (2022) 258-",
  "prize":None,"class":None,"tractability":None,
  "notes":"status: SOLVED (theorem). Harvested as checker calibration material: it is a clean forall-regular-"
    "graphs inequality whose refutation would be a single small graph, so it is an ideal known-true input for "
    "a geng-based checker. WebSearch-summary provenance only (arxiv blocked). alpha is NP-hard; mu is "
    "poly (Edmonds' blossom algorithm)."},
]
entries.extend(extra)

outp = "/home/user/openproblem-miner/mine/corpus/raw/h5_graphinv.jsonl"
os.makedirs(os.path.dirname(outp), exist_ok=True)
seen = set()
with open(outp, "w") as fh:
    for e in entries:
        assert e["id"] not in seen, e["id"]
        seen.add(e["id"])
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print("wrote", len(entries), "entries to", outp)
if missing: print("MISSING statement_nl for:", missing)
