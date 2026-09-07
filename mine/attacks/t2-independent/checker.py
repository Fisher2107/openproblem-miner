#!/usr/bin/env python3
"""
Independent from-scratch checker (Tier 2) for the claim:

  G (given below in graph6) satisfies:
    1. G is connected
    2. tree(G) = ceil(1 + l_avg(G))
    3. G has no Hamiltonian path

Where l(v) = independence number of the subgraph induced on the open
neighbourhood N(v), l_avg(G) = average of l(v) over all vertices,
tree(G) = max number of vertices in an induced subgraph that is a tree
(connected and acyclic).

All arithmetic is exact (Python ints and fractions.Fraction). No floats.

This file was written from scratch without consulting any existing
verifier/checker/attack code in this repository, per task instructions.
"""

from fractions import Fraction
from itertools import combinations, permutations
import sys

GRAPH6 = "J^~~u?_C?O?"


def decode_graph6(s):
    """Decode a graph6 string into (n, adjacency-set-of-frozensets edges).
    Implements the standard McKay graph6 format from scratch:
      - N(n) encoding: if first byte < 63, n = byte-63 (n <= 62 case).
        (We only need the small-n case here; still implement the general
        rule defensively.)
      - Remaining bytes: each byte b represents 6 bits = b - 63, written
        as bits from most-significant (32) to least-significant (1).
      - Bits fill in the upper triangle of the adjacency matrix in
        column-major order per graph6 spec: bit stream corresponds to
        pairs (i,j) with i<j ordered as
        (0,1),(0,2),(1,2),(0,3),(1,3),(2,3),... i.e. j from 1..n-1,
        i from 0..j-1.
    """
    data = s.strip()
    codes = [ord(c) for c in data]
    for c in codes:
        if not (63 <= c <= 126):
            raise ValueError(f"byte {c} out of graph6 printable range")

    idx = 0
    if codes[0] == 126:
        # extended N(n) encoding (not needed for n<=62, but handle defensively)
        if codes[1] == 126:
            # 8-byte length field
            nbytes = codes[2:8]
            idx = 8
        else:
            nbytes = codes[1:4]
            idx = 4
        n = 0
        for b in nbytes:
            n = (n << 6) | (b - 63)
    else:
        n = codes[0] - 63
        idx = 1

    # remaining bytes -> bit stream
    bits = []
    for c in codes[idx:]:
        v = c - 63
        if not (0 <= v <= 63):
            raise ValueError("bad byte value")
        for k in range(5, -1, -1):  # 6 bits, MSB first
            bits.append((v >> k) & 1)

    num_pairs = n * (n - 1) // 2
    if len(bits) < num_pairs:
        raise ValueError(f"not enough bits: have {len(bits)}, need {num_pairs}")

    edges = set()
    bitpos = 0
    for j in range(1, n):
        for i in range(0, j):
            bit = bits[bitpos]
            bitpos += 1
            if bit:
                edges.add((i, j))

    return n, edges


def build_adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for (i, j) in edges:
        adj[i].add(j)
        adj[j].add(i)
    return adj


def independence_number(vertices, adj):
    """Exhaustively compute the independence number of the subgraph induced
    on `vertices` (an iterable of vertex ids), using adjacency sets `adj`
    which are indexed by global vertex id. Brute force over all subsets,
    from largest size down, checking pairwise non-adjacency. Correctness
    over cleverness, as instructed; these neighbourhoods are small.
    """
    verts = list(vertices)
    m = len(verts)
    if m == 0:
        return 0
    # try subset sizes from m down to 0, return first that has an
    # independent set (guaranteed at size 0 and 1)
    for size in range(m, -1, -1):
        for combo in combinations(verts, size):
            ok = True
            for a in range(len(combo)):
                if not ok:
                    break
                for b in range(a + 1, len(combo)):
                    if combo[b] in adj[combo[a]]:
                        ok = False
                        break
            if ok:
                return size
    return 0


def is_connected(n, adj):
    if n == 0:
        return True
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == n


def induces_tree(vertex_set, adj):
    """Return True iff the induced subgraph on vertex_set (a set/tuple of
    vertex ids) is connected and acyclic, i.e. a tree. For a simple graph,
    an induced subgraph on k vertices is a tree iff it is connected and has
    exactly k-1 induced edges."""
    verts = list(vertex_set)
    k = len(verts)
    if k == 0:
        return False  # tree(G) counts vertices of a tree subgraph; empty has no meaning here, exclude
    if k == 1:
        return True  # single vertex: connected, acyclic, trivially a tree
    vset = set(verts)
    edge_count = 0
    # build induced adjacency restricted to vset
    local_adj = {v: (adj[v] & vset) for v in verts}
    for v in verts:
        edge_count += len(local_adj[v])
    edge_count //= 2
    if edge_count != k - 1:
        return False
    # check connectivity of induced subgraph
    start = verts[0]
    seen = {start}
    stack = [start]
    while stack:
        u = stack.pop()
        for w in local_adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == k


def max_induced_tree_size(n, adj):
    """Exhaustive search over all vertex subsets, largest first, for the
    largest induced subgraph that is a tree (connected + acyclic)."""
    all_verts = list(range(n))
    for size in range(n, 0, -1):
        for combo in combinations(all_verts, size):
            if induces_tree(combo, adj):
                return size
    return 0  # n==0 edge case


def has_hamiltonian_path(n, adj):
    """Exhaustive search (brute force over permutations, with pruning via
    DFS) for a Hamiltonian path: a permutation of all n vertices such that
    consecutive vertices are adjacent."""
    if n == 0:
        return True
    if n == 1:
        return True

    # DFS-based exhaustive search (equivalent to trying all permutations,
    # but prunes early -- still exhaustive/correct, not heuristic).
    def dfs(path, visited):
        if len(path) == n:
            return True
        last = path[-1]
        for w in adj[last]:
            if w not in visited:
                visited.add(w)
                path.append(w)
                if dfs(path, visited):
                    return True
                path.pop()
                visited.remove(w)
        return False

    for start in range(n):
        if dfs([start], {start}):
            return True
    return False


def main():
    n, edges = decode_graph6(GRAPH6)
    adj = build_adjacency(n, edges)

    print(f"Decoded graph6 string: {GRAPH6!r}")
    print(f"n = {n}")
    print(f"Number of edges = {len(edges)}")
    print("Edge list (0-indexed):")
    print(sorted(edges))
    print()
    print("Adjacency lists (0-indexed):")
    for v in range(n):
        print(f"  N({v}) = {sorted(adj[v])}  (degree {len(adj[v])})")
    print()

    connected = is_connected(n, adj)
    print(f"Condition 1: G is connected -> {connected}")
    print()

    l_values = []
    for v in range(n):
        lv = independence_number(adj[v], adj)
        l_values.append(lv)
        print(f"  l({v}) = independence number of G[N({v})] = {lv}   "
              f"(|N({v})| = {len(adj[v])}, N({v}) = {sorted(adj[v])})")

    total = sum(l_values)
    l_avg = Fraction(total, n)
    print()
    print(f"Sum of l(v) over all v = {total}")
    print(f"l_avg(G) = {total}/{n} = {l_avg}  (as exact fraction)")

    one_plus_avg = 1 + l_avg
    # exact ceiling of a Fraction
    ceil_val = -((-one_plus_avg.numerator) // one_plus_avg.denominator)
    print(f"1 + l_avg(G) = {one_plus_avg}")
    print(f"ceil(1 + l_avg(G)) = {ceil_val}")
    print()

    tree_size = max_induced_tree_size(n, adj)
    print(f"tree(G) = largest induced tree subgraph size = {tree_size}")
    print()

    cond2 = (tree_size == ceil_val)
    print(f"Condition 2: tree(G) == ceil(1 + l_avg(G))  ->  {tree_size} == {ceil_val}  ->  {cond2}")
    print()

    ham = has_hamiltonian_path(n, adj)
    print(f"Hamiltonian path exists: {ham}")
    cond3 = not ham
    print(f"Condition 3: G has NO Hamiltonian path -> {cond3}")
    print()

    overall = connected and cond2 and cond3
    print("=" * 60)
    print(f"Condition 1 (connected):                 {connected}")
    print(f"Condition 2 (tree(G) == ceil(1+l_avg)):   {cond2}  ({tree_size} vs {ceil_val})")
    print(f"Condition 3 (no Hamiltonian path):        {cond3}")
    print(f"OVERALL CLAIM HOLDS:                      {overall}")
    print("=" * 60)

    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
