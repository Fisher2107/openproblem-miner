"""Exact-arithmetic graph invariants for the frozen verifier.

DESIGN RULES (this file is hash-locked by scripts/freeze.sh; read them before trusting it)

1. No floating point anywhere. Counts are `int`; averages are `fractions.Fraction`;
   the one square root in the corpus (`degreeL2Norm`) is handled by exact integer
   comparison, never by `math.sqrt`.
2. Correctness over speed. Every invariant is computed by exhaustive enumeration over
   subsets, because a checker runs on ONE witness and a subtle fast algorithm is a
   much worse trade here than a slow obvious one. Where an identity is used instead of
   the literal definition (only `Ls`), the identity is validated exhaustively over all
   small connected graphs in the freeze-time test suite.
3. Each function names the Lean definition it mirrors, in
   google-deepmind/formal-conjectures @ 8323e878, so that a reader can diff the
   informal statement against the formal one. Statement drift is the dominant failure
   mode of a system like this; these citations are the defence against it.
4. This file is INDEPENDENT of mine/tools/graphtool.c. The C tool searches; this
   library verifies. They were written separately and agreement between them is
   evidence, not architecture.
"""
from fractions import Fraction
from itertools import combinations

MAX_N_EXHAUSTIVE = 22          # refuse rather than guess above this


# ----------------------------------------------------------------- graph6 input
def decode_graph6(s):
    """Decode a graph6 string to (n, adj) with adj a list of int bitmasks.

    Independent implementation of the McKay graph6 format: first byte n+63 (n<63),
    then ceil(n(n-1)/2 / 6) bytes of 6 bits each, column-major upper triangle.
    """
    s = s.strip()
    if s.startswith('>>graph6<<'):
        s = s[len('>>graph6<<'):]
    if not s:
        raise ValueError("empty graph6 string")
    b = [ord(c) - 63 for c in s]
    if any(x < 0 or x > 63 for x in b):
        raise ValueError("graph6 byte out of range")
    if b[0] == 63:
        raise ValueError("graph6 with n >= 63 not supported by this checker")
    n, rest = b[0], b[1:]
    need = (n * (n - 1) // 2 + 5) // 6
    if len(rest) < need:
        raise ValueError("graph6 payload too short: need %d bytes, got %d" % (need, len(rest)))
    bits = []
    for x in rest:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    adj = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            k += 1
    return n, adj


def from_edge_list(n, edges):
    adj = [0] * n
    for (u, v) in edges:
        if u == v:
            raise ValueError("loops are not simple-graph edges")
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return n, adj


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def popcount(x):
    return bin(x).count('1')


def subsets(n):
    return range(1 << n)


def _guard(n):
    if n > MAX_N_EXHAUSTIVE:
        raise ValueError(
            "witness has n=%d > %d: this checker verifies by exhaustive enumeration and "
            "refuses to guess. Reject rather than accept an unverified witness." % (n, MAX_N_EXHAUSTIVE))


# ----------------------------------------------------------------- basic structure
def degrees(n, adj):
    return [popcount(adj[v]) for v in range(n)]


def num_edges(n, adj):
    return sum(degrees(n, adj)) // 2


def induced_connected(adj, S):
    """Is the induced subgraph on vertex set `S` (bitmask) connected? Empty set: False."""
    if S == 0:
        return False
    start = (S & -S)
    seen, frontier = start, start
    while frontier:
        nxt = 0
        for v in bits(frontier):
            nxt |= adj[v] & S & ~seen
        seen |= nxt
        frontier = nxt
    return seen == S


def is_connected(n, adj):
    return n == 0 or induced_connected(adj, (1 << n) - 1)


def induced_edges(adj, S):
    return sum(popcount(adj[v] & S) for v in bits(S)) // 2


def induced_acyclic(adj, S):
    """Induced subgraph on S is acyclic  <=>  every component is a tree
    (|E| = |V| - #components). Mirrors `SimpleGraph.IsAcyclic` on `G.induce s`."""
    verts = list(bits(S))
    if not verts:
        return True                     # the empty graph is acyclic
    comps, seen = 0, 0
    for v in verts:
        if seen >> v & 1:
            continue
        comps += 1
        stack, seen = [v], seen | (1 << v)
        while stack:
            u = stack.pop()
            for w in bits(adj[u] & S & ~seen):
                seen |= 1 << w
                stack.append(w)
    return induced_edges(adj, S) == len(verts) - comps


def induced_bipartite(adj, S):
    """Induced subgraph on S admits a proper 2-colouring. Mirrors `IsBipartite`."""
    colour = {}
    for start in bits(S):
        if start in colour:
            continue
        colour[start] = 0
        stack = [start]
        while stack:
            u = stack.pop()
            for w in bits(adj[u] & S):
                if w not in colour:
                    colour[w] = 1 - colour[u]
                    stack.append(w)
                elif colour[w] == colour[u]:
                    return False
    return True


def induced_is_tree(adj, S):
    """Connected and acyclic. Mirrors `(G.induce s).IsTree`; the empty set is not a tree
    because mathlib's `Connected` requires `Nonempty`."""
    return S != 0 and induced_connected(adj, S) and induced_acyclic(adj, S)


# ----------------------------------------------------------------- independence
def independence_number_on(adj, S):
    """alpha of the induced subgraph on S, by exhaustive branch and bound."""
    best = 0

    def rec(cand, have):
        nonlocal best
        if have + popcount(cand) <= best:
            return
        if cand == 0:
            best = max(best, have)
            return
        v = (cand & -cand).bit_length() - 1
        rec(cand & ~(1 << v) & ~adj[v], have + 1)     # take v
        rec(cand & ~(1 << v), have)                   # drop v

    rec(S, 0)
    return best


def independence_number(n, adj):
    """alpha(G). Mirrors `SimpleGraph.indepNum`."""
    _guard(n)
    return independence_number_on(adj, (1 << n) - 1)


def indep_neighbors_card(n, adj, v):
    """l(v) = alpha(G[N(v)]). Mirrors `indepNeighborsCard G v`."""
    return independence_number_on(adj, adj[v])


def max_indep_neighbors(n, adj):
    """max_v l(v)."""
    return max(indep_neighbors_card(n, adj, v) for v in range(n))


def average_indep_neighbors(n, adj):
    """l_avg(G) = (sum_v l(v)) / n, EXACT as a Fraction. Mirrors `averageIndepNeighbors`."""
    return Fraction(sum(indep_neighbors_card(n, adj, v) for v in range(n)), n)


# ----------------------------------------------------------------- induced maxima
def _max_induced(n, adj, pred):
    _guard(n)
    best = 0
    for S in subsets(n):
        c = popcount(S)
        if c > best and pred(adj, S):
            best = c
    return best


def largest_induced_forest_size(n, adj):
    """f(G). Mirrors `largestInducedForestSize` (acyclic induced subgraph, empty allowed)."""
    return _max_induced(n, adj, induced_acyclic)


def largest_induced_bipartite_size(n, adj):
    """b(G). Mirrors `largestInducedBipartiteSubgraphSize`."""
    return _max_induced(n, adj, induced_bipartite)


def largest_induced_tree_size(n, adj):
    """tree(G). Mirrors `largestInducedTreeSize` (connected AND acyclic)."""
    return _max_induced(n, adj, induced_is_tree)


def largest_induced_path_size(n, adj):
    """path(G) = number of vertices of a largest induced path.

    Mirrors `SimpleGraph.path`, whose `isInducedPath` requires the vertex list to be
    nodup and to have G.Adj (l i) (l j) exactly when |i-j| = 1. Equivalently: the
    induced subgraph on the vertex set is a path graph, i.e. it is a tree with at most
    two vertices of degree 1 and no vertex of degree > 2. A single vertex is a path.
    """
    _guard(n)
    best = 0
    for S in subsets(n):
        c = popcount(S)
        if c <= best:
            continue
        if not induced_is_tree(adj, S):
            continue
        degs = [popcount(adj[v] & S) for v in bits(S)]
        if max(degs) <= 2:                 # a tree with max degree <= 2 is a path
            best = c
    return best


# ----------------------------------------------------------------- domination
def is_dominating(n, adj, S):
    cov = S
    for v in bits(S):
        cov |= adj[v]
    return cov == (1 << n) - 1


def is_total_dominating(n, adj, S):
    """Every vertex of G has a NEIGHBOUR in S. Mirrors `IsTotalDominatingSet`."""
    cov = 0
    for v in bits(S):
        cov |= adj[v]
    return cov == (1 << n) - 1


def total_domination_number(n, adj):
    """gamma_t(G). Mirrors `totalDominationNumber`. Returns None when no total
    dominating set exists (a graph with an isolated vertex)."""
    _guard(n)
    best = None
    for S in subsets(n):
        if best is not None and popcount(S) >= best:
            continue
        if is_total_dominating(n, adj, S):
            best = popcount(S)
    return best


def connected_domination_number(n, adj):
    """gamma_c(G): minimum size of a connected dominating set. Mirrors
    `connectedDominationNumber`."""
    _guard(n)
    best = None
    for S in subsets(n):
        if S == 0:
            continue
        if best is not None and popcount(S) >= best:
            continue
        if is_dominating(n, adj, S) and induced_connected(adj, S):
            best = popcount(S)
    return best


def minimal_total_dominating_sets(n, adj):
    """All S that are total dominating and inclusion-minimal.
    Mirrors `IsMinimalTotalDominatingSet` (T strictly contained in S, T not TDS)."""
    _guard(n)
    tds = [S for S in subsets(n) if is_total_dominating(n, adj, S)]
    tdset = set(tds)
    out = []
    for S in tds:
        minimal = True
        for v in bits(S):
            if (S & ~(1 << v)) in tdset:
                minimal = False
                break
        if minimal:
            out.append(S)
    return out


def is_well_totally_dominated(n, adj):
    """Every minimal total dominating set has the same cardinality.
    Mirrors `IsWellTotallyDominated`.

    NOTE on the minimality test: `IsMinimalTotalDominatingSet` quantifies over all
    T STRICTLY contained in S, but a total dominating set stays total dominating when
    a vertex is added back, so a set is inclusion-minimal iff no single-vertex deletion
    is total dominating -- which is what `minimal_total_dominating_sets` tests. That
    equivalence is checked exhaustively for n <= 7 in the freeze-time test suite.
    """
    sizes = {popcount(S) for S in minimal_total_dominating_sets(n, adj)}
    return len(sizes) <= 1


# ----------------------------------------------------------------- spanning trees
def max_leaf_spanning_tree(n, adj):
    """Ls(G) = max over spanning trees of the number of degree-1 vertices.
    Mirrors `SimpleGraph.Ls`.

    Computed as n - gamma_c(G) for n >= 3 (Douglas 1992: the internal vertices of a
    spanning tree form a connected dominating set, and conversely every connected
    dominating set is the internal-vertex set of some spanning tree). The identity is
    validated against brute-force spanning-tree enumeration for EVERY connected graph
    on at most 7 vertices in the freeze-time test suite. n <= 2 is handled literally:
    K1 has the one-vertex tree with no degree-1 vertex, K2's spanning tree has two.
    """
    _guard(n)
    if not is_connected(n, adj):
        raise ValueError("Ls is defined here for connected graphs only")
    if n == 1:
        return 0
    if n == 2:
        return 2
    gc = connected_domination_number(n, adj)
    return n - gc


def max_leaf_spanning_tree_bruteforce(n, adj):
    """Literal computation of Ls by enumerating every spanning tree. Only used to
    validate `max_leaf_spanning_tree` on small graphs in the test suite."""
    if n > 8:
        raise ValueError("brute-force Ls is for validation on n <= 8 only")
    edges = [(u, v) for u in range(n) for v in range(u + 1, n) if adj[u] >> v & 1]
    best = 0
    for comb in combinations(edges, n - 1):
        deg = [0] * n
        sub = [0] * n
        for (u, v) in comb:
            deg[u] += 1
            deg[v] += 1
            sub[u] |= 1 << v
            sub[v] |= 1 << u
        if induced_connected(sub, (1 << n) - 1):        # n-1 edges + connected = tree
            best = max(best, sum(1 for v in range(n) if deg[v] == 1))
    return best


# ----------------------------------------------------------------- distance
def eccentricities(n, adj):
    """List of eccentricities. Raises on a disconnected graph (distance undefined)."""
    out = []
    for s in range(n):
        seen, frontier, d, last = 1 << s, 1 << s, 0, 0
        while frontier:
            nxt = 0
            for v in bits(frontier):
                nxt |= adj[v] & ~seen
            if not nxt:
                break
            seen |= nxt
            frontier = nxt
            d += 1
        if seen != (1 << n) - 1:
            raise ValueError("graph is disconnected; eccentricity undefined")
        out.append(d)
        last = d
    del last
    return out


def diameter(n, adj):
    return max(eccentricities(n, adj))


def radius(n, adj):
    return min(eccentricities(n, adj))


def average_eccentricity(n, adj):
    """EXACT Fraction. Mirrors `averageEccentricity`."""
    e = eccentricities(n, adj)
    return Fraction(sum(e), n)


def girth(n, adj):
    """Length of a shortest cycle, or None if acyclic. Mirrors `SimpleGraph.girth`
    (which is `⊤` for an acyclic graph; the WOWII files use 0 in that case, so callers
    must map None themselves and say which convention they used)."""
    best = None
    for s in range(n):
        dist = [-1] * n
        par = [-1] * n
        dist[s] = 0
        q = [s]
        qi = 0
        while qi < len(q):
            v = q[qi]
            qi += 1
            for u in bits(adj[v]):
                if dist[u] < 0:
                    dist[u] = dist[v] + 1
                    par[u] = v
                    q.append(u)
                elif u != par[v]:
                    c = dist[u] + dist[v] + 1
                    if best is None or c < best:
                        best = c
    return best


def has_cycle_of_length_4(n, adj):
    """True iff G contains a cycle of length exactly 4 (NOT necessarily induced):
    equivalently two distinct vertices with two common neighbours.
    Used for the WOWII `chi_{C_4}` indicator."""
    for u in range(n):
        for v in range(u + 1, n):
            if popcount(adj[u] & adj[v]) >= 2:
                return True
    return False


# ----------------------------------------------------------------- triangles, degrees
def num_triangles_at_vertex(n, adj, v):
    """T(v): number of 3-cliques containing v. Mirrors `numTrianglesAtVertex`."""
    nb = list(bits(adj[v]))
    return sum(1 for i in range(len(nb)) for j in range(i + 1, len(nb))
               if adj[nb[i]] >> nb[j] & 1)


def havel_hakimi_step(seq):
    """One Havel-Hakimi step on a descending list. Mirrors `havelHakimiStep`:
    drop the head d, decrement the next d entries (truncated at 0), re-sort descending."""
    if not seq:
        return []
    d, rest = seq[0], seq[1:]
    to_dec, remaining = rest[:d], rest[d:]
    dec = [max(0, x - 1) for x in to_dec]
    return sorted(dec + remaining, reverse=True)


def residue(n, adj):
    """Havel-Hakimi residue. Mirrors `residueAux`: recurse until the head is 0, then
    the answer is the length of the remaining (all-zero) list."""
    seq = sorted(degrees(n, adj), reverse=True)
    while True:
        if not seq:
            return 0
        if seq[0] == 0:
            return len(seq)
        seq = havel_hakimi_step(seq)


def havel_hakimi_zero_index(n, adj):
    """k(G): the FIRST index i >= 0 at which the i-th Havel-Hakimi iterate of the
    descending degree sequence contains a zero. Iterate 0 is the degree sequence itself."""
    seq = sorted(degrees(n, adj), reverse=True)
    i = 0
    while True:
        if any(x == 0 for x in seq) or not seq:
            return i
        seq = havel_hakimi_step(seq)
        i += 1
        if i > 4 * n + 8:
            raise ValueError("Havel-Hakimi iteration did not reach a zero; refusing to guess")


def degree_l2_norm_squared(n, adj):
    """S = sum_v deg(v)^2, so that degreeL2Norm = sqrt(S). Kept squared and INTEGER so
    that comparisons stay exact; see `ceil_half_sum_with_sqrt`."""
    return sum(d * d for d in degrees(n, adj))


def ceil_of_quarter_2L_plus_sqrtS(L, S):
    """Exact ceil((2L + sqrt(S)) / 4) for integers L >= 0, S >= 0, with no floats.

    This is `ceil((L + sqrt(S)/2)/2)` as it appears in WOWII conjecture 100.
    m is the answer iff 4m >= 2L + sqrt(S) and 4(m-1) < 2L + sqrt(S), and since
    sqrt(S) >= 0 the first is equivalent to (4m - 2L) >= 0 and (4m-2L)^2 >= S.
    """
    m = 0
    while True:
        t = 4 * m - 2 * L
        if t >= 0 and t * t >= S:
            return m
        m += 1
        if m > 10 ** 6:
            raise ValueError("ceil search diverged")


# ----------------------------------------------------------------- paths / hamiltonicity
def has_hamiltonian_path(n, adj):
    """Does G have a path visiting every vertex exactly once? DP over subsets."""
    _guard(n)
    if n <= 1:
        return True
    full = (1 << n) - 1
    reach = [0] * (1 << n)              # reach[S] = bitmask of endpoints of paths covering S
    for v in range(n):
        reach[1 << v] = 1 << v
    for S in range(1, 1 << n):
        ends = reach[S]
        if not ends:
            continue
        if S == full:
            return True
        for v in bits(ends):
            for w in bits(adj[v] & ~S):
                reach[S | (1 << w)] |= 1 << w
    return bool(reach[full])


def path_cover_number(n, adj):
    """p(G): minimum number of vertex-disjoint paths of G covering V(G).
    Mirrors `pathCoverNumber` (paths in G, not induced paths; a single vertex counts)."""
    if n > 16:
        raise ValueError("path_cover_number is exhaustive; refusing above n=16")
    is_path_set = [False] * (1 << n)
    for S in range(1, 1 << n):
        verts = list(bits(S))
        sub = [adj[v] & S for v in range(n)]
        k = len(verts)
        if k == 1:
            is_path_set[S] = True
            continue
        if not induced_connected(adj, S):
            continue
        # Hamiltonian path within the induced subgraph on S
        reach = {}
        for v in verts:
            reach[1 << v] = 1 << v
        found = False
        order = sorted([T for T in range(1, 1 << n) if T & ~S == 0], key=popcount)
        for T in order:
            ends = reach.get(T, 0)
            if not ends:
                continue
            if T == S:
                found = True
                break
            for v in bits(ends):
                for w in bits(sub[v] & ~T):
                    reach[T | (1 << w)] = reach.get(T | (1 << w), 0) | (1 << w)
        is_path_set[S] = found
    INF = 10 ** 9
    dp = [INF] * (1 << n)
    dp[0] = 0
    for S in range(1, 1 << n):
        low = (S & -S)
        T = S
        # iterate over subsets of S that contain the lowest set bit
        sub = S
        while sub:
            if sub & low and is_path_set[sub] and dp[S ^ sub] + 1 < dp[S]:
                dp[S] = dp[S ^ sub] + 1
            sub = (sub - 1) & S
        del T
    return dp[(1 << n) - 1]
