"""
Target: lit-combinatorics-bollobas-nikiforov-k4free
Source corpus entry: mine/corpus/raw/h6_literature.jsonl (arXiv:2603.26379,
"The Bollobas-Nikiforov Conjecture for Complete Multipartite Graphs and Dense K4-Free
Graphs")

Statement (restated exactly, all symbols defined):
  For a graph G with adjacency eigenvalues lambda_1(G) >= lambda_2(G) >= ... and m edges,
  the Bollobas-Nikiforov conjecture specialized to K4-free graphs (omega(G) <= 3) is:
    for every K4-free graph G with G != K_3:  lambda_1(G)^2 + lambda_2(G)^2 <= 4*m/3.

Witness: a single K4-free graph G != K_3 with lambda_1(G)^2 + lambda_2(G)^2 > 4*m/3.

Method: exhaustively generate ALL K4-free graphs (connected and disconnected, all of
them -- the conjecture quantifies over every K4-free graph, not just connected ones) on
n vertices via `nauty-geng -k n` for n = 1..10, decode each g6 string, compute the exact
number of edges m and the adjacency eigenvalues via numpy (double precision -- this is a
T0 float screen only, no exact/interval arithmetic used, since nothing here can ship
regardless), and flag any graph where lambda_1^2+lambda_2^2 exceeds 4m/3 by more than a
generous floating-point tolerance (1e-6, chosen because the LHS/RHS here are both O(1)-
to-O(n) scale quantities and IEEE double precision easily resolves differences far above
1e-6 for graphs this size -- a true violation would show up as a much larger gap, and
this is explicitly flagged as a screen, not a certificate).
"""
import subprocess
import time
import numpy as np


def g6_to_adj(g6: str) -> np.ndarray:
    """Decode a single-line graph6 string (networkx-independent, no isolated-vertex
    padding needed since nauty-geng -k n always emits n-vertex graphs)."""
    data = [ord(c) - 63 for c in g6.strip()]
    n = data[0]
    bits = []
    for byte in data[1:]:
        for shift in range(5, -1, -1):
            bits.append((byte >> shift) & 1)
    A = np.zeros((n, n), dtype=np.float64)
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                A[i, j] = 1.0
                A[j, i] = 1.0
            idx += 1
    return A


def sweep(n_max, tol=1e-6):
    worst_margin = None  # (margin, n, g6) -- margin = LHS - RHS, most positive = closest to violating
    total = 0
    violations = []
    t0 = time.time()
    for n in range(2, n_max + 1):  # n=1 has no lambda_2 (only one eigenvalue exists); skip as trivial
        proc = subprocess.run(["nauty-geng", "-k", str(n)], capture_output=True, text=True)
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        for g6 in lines:
            A = g6_to_adj(g6)
            m = int(A.sum() // 2)
            if m == n * (n - 1) // 2:
                # G is complete (K_n). The corpus's statement_nl says "G != K_3" only,
                # but the underlying general Bollobas-Nikiforov conjecture (Bollobas &
                # Nikiforov 2002) excludes EVERY complete graph, not just K_3 -- see
                # log.md "Definition correction" section. Since K4-free graphs can only
                # be complete for n<=3 (K_1, K_2, K_3), exclude all of them here.
                continue
            total += 1
            eigs = np.linalg.eigvalsh(A)  # ascending
            l1, l2 = eigs[-1], eigs[-2]
            lhs = l1 ** 2 + l2 ** 2
            rhs = 4.0 * m / 3.0
            margin = lhs - rhs
            if worst_margin is None or margin > worst_margin[0]:
                worst_margin = (margin, n, g6, l1, l2, m)
            if margin > tol:
                violations.append((n, g6, l1, l2, m, margin))
        print(f"  n={n}: {len(lines)} K4-free graphs checked (cumulative total={total}), "
              f"elapsed={time.time()-t0:.1f}s")
    return total, violations, worst_margin, time.time() - t0


if __name__ == "__main__":
    N_MAX = 9  # bump to 10 separately if time allows (2.9M graphs at n=10)
    total, violations, worst_margin, wall = sweep(N_MAX)
    print(f"\nTotal K4-free graphs checked (n=1..{N_MAX}, K_3 excluded): {total}")
    print(f"wall={wall:.1f}s")
    print(f"Closest-to-violating margin found (LHS-RHS, want <=0): {worst_margin}")
    if violations:
        print(f"VIOLATIONS ({len(violations)}):")
        for v in violations[:10]:
            print("  ", v)
    else:
        print("NO VIOLATION found (float screen, tol=1e-6)")
