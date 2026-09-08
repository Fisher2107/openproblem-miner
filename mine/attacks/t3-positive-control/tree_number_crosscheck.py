#!/usr/bin/env python3
"""External cross-check of the one unformalised step in Conj200Control.lean (gap M1).

The Lean file encodes "induced subgraph that is a tree" as "connected and |E| = |V| - 1".
This script recomputes tree(G) under the *literal* definition "connected and acyclic"
(acyclicity by repeated leaf-stripping, which empties a graph iff it is a forest) and
checks that the two families of induced trees coincide for this graph.

    $ python3 tree_number_crosscheck.py

This is a T1-level check outside Lean; it does not close gap M1 inside the kernel.
"""
import itertools, subprocess

g6 = 'J^~~u?_C?O?'
out = subprocess.run(f"echo '{g6}' | nauty-listg -a", shell=True,
                     capture_output=True, text=True).stdout
A = [[int(c) for c in l.strip()] for l in out.splitlines()
     if l.strip() and set(l.strip()) <= set('01')]
n = len(A)
assert n == 11 and all(A[i][j] == A[j][i] for i in range(n) for j in range(n))
N = [set(j for j in range(n) if A[i][j]) for i in range(n)]

def verts(m):   return [i for i in range(n) if m >> i & 1]
def edges(m):   return sum(1 for a, b in itertools.combinations(verts(m), 2) if A[a][b])

def connected(m):
    vs = verts(m)
    if not vs: return False
    seen, stack = {vs[0]}, [vs[0]]
    while stack:
        x = stack.pop()
        for y in N[x]:
            if (m >> y & 1) and y not in seen:
                seen.add(y); stack.append(y)
    return len(seen) == len(vs)

def acyclic(m):
    """A finite graph is a forest iff repeatedly deleting vertices of degree <= 1 empties it."""
    cur, changed = set(verts(m)), True
    while changed:
        changed = False
        for v in list(cur):
            if len(N[v] & cur) <= 1:
                cur.discard(v); changed = True
    return not cur

literal = {m for m in range(1 << n) if m and connected(m) and acyclic(m)}
edgechr = {m for m in range(1 << n) if m and connected(m) and edges(m) == len(verts(m)) - 1}

print(f"graph6 {g6}: {n} vertices, {sum(map(len, N)) // 2} edges")
print("tree(G), literal 'connected and acyclic' :", max(len(verts(m)) for m in literal))
print("tree(G), 'connected and |E| = |V| - 1'   :", max(len(verts(m)) for m in edgechr))
print("the two families of induced trees agree  :", literal == edgechr,
      f"({len(literal)} induced trees)")
print("witness 225 = {0,5,6,7} is acyclic       :", acyclic(225))
assert literal == edgechr and max(len(verts(m)) for m in literal) == 4 and acyclic(225)
print("OK")
