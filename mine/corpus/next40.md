# Recommended next 40 problems (run 2)

Ranked by `mine/tools/next40.py`, which re-scores the corpus with run 1's calibration:
frontier headroom counts, published exhaustive sweeps are a penalty, and a witness
shape our verifier family cannot express is a penalty. **Write the checkers for all
forty before freezing** -- run 1's largest process error was freezing mid-harvest.

| # | id | class | score | statement (abridged) | why it is on the list |
|---|---|---|---|---|---|
| 1 | `wow2-133` | A | 10.0 | For every finite simple connected graph G, path(G) >= rad(G) + floor(l_avg(G))^{cC4(G)}, where path(G) is the  | path>=diam+1 gate is strong; push n=11-12 |
| 2 | `wow2-141` | A | 10.0 | For every finite simple connected graph G, tree(G) >= floor(girth(G)/2) - 1 + max_v l(v), where tree(G) is the | raise to n=18-19; the girth argument keeps it cheap |
| 3 | `wow2-19` | A | 10.0 | For every finite simple connected graph G on at least two vertices, b(G) >= floor( (sum over v of ecc(v))/n(G) | the tightest arm we found: equality is achieved but never exceeded, so it is the best candidate for a violation just past our reach |
| 4 | `wow2-198a` | A | 10.0 | For every finite simple connected graph G on at least two vertices, if b(G) <= 2 + ecc_avg(G) then G has a Ham | gate alpha*n <= 2n+sum ecc |
| 5 | `wow2-61` | A | 10.0 | For every finite simple connected graph G, f(G) >= residue(G) + ceil(diam(G)/3), where f(G) is the maximum ord | gate lhs>alpha; n=11 affordable |
| 6 | `wow2-100` | A | 9.5 | For every finite simple connected graph G, alpha(G) <= ceil( ( max_v l(v) + 0.5*length(complement of G) ) / 2  | all invariants cheap; n=11 exhaustive is affordable |
| 7 | `wow2-160` | A | 9.5 | For every finite simple connected graph G, Ls(G) >= max_v l(v) + (max_v T(v)) * cC4(G), where Ls(G) is the max | gate maxL+maxT*cC4 >= n is very restrictive; enumerate n=11..12 exhaustively |
| 8 | `wow2-291` | A | 9.5 | For every finite simple connected graph G with n(G) > 2, gamma_t(G) <= k(G) + freq_min_T(G), where gamma_t(G)  | all invariants cheap |
| 9 | `wow2-314` | A | 9.5 | For every finite simple connected graph G on at least two vertices, if G is triangle-free and its largest indu | triangle-free gate; enumerate triangle-free graphs to n=13 |
| 10 | `wow2-40` | A | 9.5 | For every finite simple connected graph G on at least two vertices, f(G) >= ceil( (p(G) + b(G) + 1)/2 ), where | expensive arm (needs both f and b); needs a cheap necessary condition first |
| 11 | `erdos-0023` | A | 8.5 | Can every triangle-free graph on 5n vertices be made bipartite by deleting at most n^2 edges? | witness is a graph: nauty makes our frontier concrete and extendable; Lean statement already exists, so T3 is cheaper |
| 12 | `erdos-0617` | A | 8.5 | Let r≥ 3. If the edges of K_{r^2+1} are r-coloured then there exist r+1 vertices with at least one colour miss | witness is a graph: nauty makes our frontier concrete and extendable; Lean statement already exists, so T3 is cheaper |
| 13 | `erdos-0628` | A | 8.5 | Let G be a graph with chromatic number k containing no K_k. If a,b≥ 2 and a+b=k+1 then must there exist two di | witness is a graph: nauty makes our frontier concrete and extendable; Lean statement already exists, so T3 is cheaper |
| 14 | `erdos-0835-b` | A | 8.5 | Alternative statement of Erdős Problem 835 using the chromatic number of the Johnson graph. This is equivalent | witness is a graph: nauty makes our frontier concrete and extendable; Lean statement already exists, so T3 is cheaper |
| 15 | `erdos-0982` | A | 8.5 | If n distinct points in ℝ^2 form a convex polygon then some vertex has at least floor((n)/(2)) different dista | witness is a graph: nauty makes our frontier concrete and extendable; Lean statement already exists, so T3 is cheaper |
| 16 | `fc-wikipedia-Conway99Graph` | A | 8.5 | Context (Conway's 99-graph problem). Does there exist an undirected graph with 99 vertices, in which each two  | witness is a graph: nauty makes our frontier concrete and extendable; Lean statement already exists, so T3 is cheaper |
| 17 | `bound-ramsey-R3333` | A | 8.0 | The 4-colour diagonal Ramsey number R(3,3,3,3) is the smallest n such that every 4-colouring of the edges of K | witness is a graph: nauty makes our frontier concrete and extendable |
| 18 | `bound-ramsey-R4-6` | A | 8.0 | The Ramsey number R(4,6) is the smallest n such that every 2-colouring of the edges of K_n contains a monochro | witness is a graph: nauty makes our frontier concrete and extendable |
| 19 | `bound-ramsey-R5-6` | A | 8.0 | The Ramsey number R(5,6) is the smallest n such that every 2-colouring of the edges of K_n contains a monochro | witness is a graph: nauty makes our frontier concrete and extendable |
| 20 | `erdos-0835-a` | A | 8.0 | Does there exist a k>2 such that the k-sized subsets of {1,...,2k} can be coloured with k+1 colours such that  | Lean statement already exists, so T3 is cheaper |
| 21 | `erdos-1041` | A | 8.0 | Let f(z) = Π_{i=1}^{n} (z - z_i) ∈ ℂ[x] with /z_i/ < 1 for all i. Conjecture: Must there always exist a path o | Lean statement already exists, so T3 is cheaper |
| 22 | `graffiti-3` | A | 8.0 | For every finite simple connected graph G, alpha(G) >= rad(G), where alpha(G) is the independence number and r | witness is a graph: nauty makes our frontier concrete and extendable |
| 23 | `bound-cage-k3g14` | A | 7.5 | n(3,14) is the number of vertices in the smallest 3-regular (cubic) graph of girth 14 (a (3,14)-cage). The cur | witness is a graph: nauty makes our frontier concrete and extendable |
| 24 | `bound-cr-K13` | A | 7.5 | cr(K13) is the minimum number of edge crossings over all drawings of the complete graph K13 in the plane. Guy' | witness is a graph: nauty makes our frontier concrete and extendable |
| 25 | `bound-ramsey-R6-6` | A | 7.5 | The Ramsey number R(6,6) is the smallest n such that every 2-colouring of the edges of K_n contains a monochro | witness is a graph: nauty makes our frontier concrete and extendable |
| 26 | `bound-vdw-W4-4` | A | 7.5 | The van der Waerden number W(4,4) is the smallest N such that every 2-colouring of {1,...,N} contains a monoch | witness is a graph: nauty makes our frontier concrete and extendable |
| 27 | `erdos-0064` | A | 7.5 | Does every finite graph with minimum degree at least 3 contain a cycle of length 2^k for some k ≥ 2? | witness is a graph: nauty makes our frontier concrete and extendable; Lean statement already exists, so T3 is cheaper |
| 28 | `erdos-0128` | A | 7.5 | Let G be a graph with n vertices such that every induced subgraph on ≥ n/2 vertices has more than n^2/50 edges | witness is a graph: nauty makes our frontier concrete and extendable; Lean statement already exists, so T3 is cheaper |
| 29 | `erdos-0307-b` | A | 7.5 | There are no examples known of the weakened coprime version if we insist that 1∉ P∪ Q. | Lean statement already exists, so T3 is cheaper |
| 30 | `erdos-0366-a` | A | 7.5 | Are there any 2-full n such that n+1 is 3-full? | Lean statement already exists, so T3 is cheaper |
| 31 | `erdos-0723-b` | A | 7.5 | It is open whether there exists a projective plane of order 12. | Lean statement already exists, so T3 is cheaper |
| 32 | `erdos-0779` | A | 7.5 | A Conjecture of Marian Deaconescu, see p.120 in https://doi.org/10.2307/2975810 [Needed to index shift in orde | Lean statement already exists, so T3 is cheaper |
| 33 | `fc-mathoverflow-21003` | A | 7.5 | Context (Mathoverflow 21003). Is there any polynomial $f(x, y) \in \mathbb{Q}[x, y]$ such that $f : \mathbb{Q} | Lean statement already exists, so T3 is cheaper |
| 34 | `fc-wikipedia-EulerBrick-b` | A | 7.5 | Context (Open questions regarding the existence of Euler bricks). Is there an Euler brick in $4$-dimensional s | Lean statement already exists, so T3 is cheaper |
| 35 | `bound-ramsey-R444` | A | 6.5 | The 3-colour diagonal Ramsey number R(4,4,4) is the smallest n such that every 3-colouring of the edges of K_n | witness is a graph: nauty makes our frontier concrete and extendable |
| 36 | `erdos-0107` | A | 6.5 | Let f(n) be minimal such that any f(n) points in ℝ^2, no three on a line, contain n points which form the vert | witness is a graph: nauty makes our frontier concrete and extendable; Lean statement already exists, so T3 is cheaper |
| 37 | `erdos-0647-a` | A | 6.5 | Let τ(n) count the number of divisors of n. Is there some n > 24 such that max_{m < n}(m + τ(m)) ≤ n + 2? | Lean statement already exists, so T3 is cheaper |
| 38 | `bound-kissing-d10` | A | 6.0 | The kissing number K(10) is the maximum number of non-overlapping unit spheres that can simultaneously touch a | top of the re-scored corpus |
| 39 | `bound-kissing-d11` | A | 6.0 | The kissing number K(11) is the maximum number of non-overlapping unit spheres that can simultaneously touch a | top of the re-scored corpus |
| 40 | `bound-kissing-d12` | A | 6.0 | The kissing number K(12) is the maximum number of non-overlapping unit spheres that can simultaneously touch a | top of the re-scored corpus |

## The ten run-1 arms and exactly where each stopped

| id | frontier reached in run 1 | how to extend it |
|---|---|---|
| `wow2-141` | exhausted to n=16 (all girth>=5 graphs) | raise to n=18-19; the girth argument keeps it cheap |
| `wow2-19` | exhausted n<=10; annealing objective reaches 0 (tight) at n=11..13 | the tightest arm we found: equality is achieved but never exceeded, so it is the best candidate for a violation just past our reach |
| `wow2-160` | exhausted n<=10, families to n=18 | gate maxL+maxT*cC4 >= n is very restrictive; enumerate n=11..12 exhaustively |
| `wow2-100` | exhausted n<=10, families to n=18 | all invariants cheap; n=11 exhaustive is affordable |
| `wow2-133` | exhausted n<=10 | path>=diam+1 gate is strong; push n=11-12 |
| `wow2-291` | exhausted n<=10 | all invariants cheap |
| `wow2-314` | exhausted n<=10 | triangle-free gate; enumerate triangle-free graphs to n=13 |
| `wow2-40` | exhausted n<=10 | expensive arm (needs both f and b); needs a cheap necessary condition first |
| `wow2-61` | exhausted n<=10 | gate lhs>alpha; n=11 affordable |
| `wow2-198a` | exhausted n<=10 | gate alpha*n <= 2n+sum ecc |
