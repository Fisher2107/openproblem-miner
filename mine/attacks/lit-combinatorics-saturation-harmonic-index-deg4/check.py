"""
Target: lit-combinatorics-saturation-harmonic-index-deg4
Source corpus entry: mine/corpus/raw/h6_literature.jsonl (arXiv:2606.15761,
"Sharp bounds between the saturation number and the harmonic index")

Statement (restated exactly, all symbols defined):
  The saturation number mu*(G) of a graph G is the minimum cardinality of a maximal
  matching (a matching that cannot be extended by adding another disjoint edge) --
  equivalently, the minimum size of an edge dominating set (a set M of edges such that
  every edge of G either is in M or shares an endpoint with some edge in M): the two
  notions coincide because "M cannot be extended" means every edge not in M meets some
  edge of M.
  The harmonic index is H(G) = sum_{uv in E(G)} 2/(deg(u)+deg(v)).
  Conjecture: every connected graph of maximum degree at most 4 satisfies mu*(G) <= H(G).

Witness: a single connected graph G, Delta(G) <= 4, with mu*(G) > H(G).

Method: exhaustively generate ALL connected graphs of maximum degree <= 4 on n vertices
via `nauty-geng -c -D4 n`, decode each g6 string, and for each graph:
  - compute H(G) EXACTLY as a Python Fraction (sum of 2/(deg(u)+deg(v)) over edges,
    degrees are small integers so this is exact rational arithmetic, no floats);
  - compute mu*(G) EXACTLY via a MaxSAT encoding of minimum edge dominating set, solved
    with pysat's RC2 (exact MaxSAT solver, not a heuristic/approximation): hard clauses
    enforce (a) at most one selected edge per vertex (matching constraint) and (b) every
    edge is either selected or adjacent to a selected edge (domination/maximality
    constraint); soft unit clauses (one per edge, weight 1, preferring the edge
    unselected) make RC2 minimize the total number of selected edges. This is provably
    exact (MaxSAT solvers are complete), not an ILP relaxation or a greedy heuristic.
Both quantities being exact means an observed mu*(G) > H(G) is a genuine mathematical
counterexample, not a numerical artifact -- there is no float-tolerance question here
unlike the eigenvalue-based targets in this batch.
"""
import subprocess
import time
from fractions import Fraction
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF


def g6_to_edges(g6: str):
    data = [ord(c) - 63 for c in g6.strip()]
    n = data[0]
    bits = []
    for byte in data[1:]:
        for shift in range(5, -1, -1):
            bits.append((byte >> shift) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def harmonic_index(n, edges, deg):
    return sum(Fraction(2, deg[u] + deg[v]) for u, v in edges)


def min_maximal_matching_size(n, edges):
    m = len(edges)
    if m == 0:
        return 0
    # variable id for edge index i (1-indexed for pysat)
    var = lambda i: i + 1
    incident = [[] for _ in range(n)]  # incident[v] = list of edge indices touching v
    for i, (u, v) in enumerate(edges):
        incident[u].append(i)
        incident[v].append(i)
    adj_edges = [set() for _ in range(m)]  # edges adjacent to edge i (sharing an endpoint)
    for v in range(n):
        for i in incident[v]:
            for j in incident[v]:
                if i != j:
                    adj_edges[i].add(j)

    wcnf = WCNF()
    # matching constraint: for each vertex, at most one incident edge selected
    for v in range(n):
        inc = incident[v]
        for a in range(len(inc)):
            for b in range(a + 1, len(inc)):
                wcnf.append([-var(inc[a]), -var(inc[b])])
    # domination/maximality constraint: each edge i is selected or adjacent to a selected edge
    for i in range(m):
        clause = [var(i)] + [var(j) for j in adj_edges[i]]
        wcnf.append(clause)
    # soft: prefer each edge unselected (minimize count of selected edges)
    for i in range(m):
        wcnf.append([-var(i)], weight=1)

    rc2 = RC2(wcnf)
    model = rc2.compute()
    cost = rc2.cost
    rc2.delete()
    return cost


def sweep(n_max):
    total = 0
    violations = []
    t0 = time.time()
    for n in range(2, n_max + 1):
        proc = subprocess.run(["nauty-geng", "-c", "-D4", str(n)], capture_output=True, text=True)
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        n_checked_here = 0
        for g6 in lines:
            nv, edges = g6_to_edges(g6)
            deg = [0] * nv
            for u, v in edges:
                deg[u] += 1
                deg[v] += 1
            H = harmonic_index(nv, edges, deg)
            mu = min_maximal_matching_size(nv, edges)
            total += 1
            n_checked_here += 1
            if mu > H:
                violations.append((n, g6, mu, H))
        print(f"  n={n}: {n_checked_here} connected maxdeg<=4 graphs checked "
              f"(cumulative total={total}), elapsed={time.time()-t0:.1f}s")
    return total, violations, time.time() - t0


if __name__ == "__main__":
    N_MAX = 10
    total, violations, wall = sweep(N_MAX)
    print(f"\nTotal connected maxdeg<=4 graphs checked (n=2..{N_MAX}): {total}")
    print(f"wall={wall:.1f}s")
    if violations:
        print(f"VIOLATIONS ({len(violations)}):")
        for v in violations[:10]:
            print("  ", v)
    else:
        print("NO VIOLATION found (exact rational arithmetic + exact MaxSAT, no tolerance needed)")
