#!/usr/bin/env python3
"""Second generator-program family: richer attachment shapes than genfamilies.py.

genfamilies.py covered "dense core + apexes + pendants", the shape of the published
counterexamples. This one widens the program space along the axes that shape leaves out:
  - attachments that are paths of length 2, not just single pendants
  - two cores joined by an edge or a path (the objectives involve radius/diameter, which a
    single dense core keeps tiny)
  - complete bipartite and cycle cores, and blow-ups of small graphs
Emits graph6 on stdout. As before, nothing here decides anything: candidates go to the
frozen checker.
"""
import sys
from itertools import combinations

def g6(n, adj):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if adj[i] >> j & 1 else 0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        c = bits[k:k + 6] + [0] * (6 - len(bits[k:k + 6]))
        v = 0
        for b in c:
            v = (v << 1) | b
        out += chr(v + 63)
    return out

def connected(n, adj):
    seen, st = {0}, [0]
    while st:
        u = st.pop()
        for v in range(n):
            if adj[u] >> v & 1 and v not in seen:
                seen.add(v)
                st.append(v)
    return len(seen) == n

class G:
    def __init__(s, n=0):
        s.n = n
        s.adj = [0] * n
    def add(s, u, v):
        while max(u, v) >= s.n:
            s.adj.append(0)
            s.n += 1
        s.adj[u] |= 1 << v
        s.adj[v] |= 1 << u
    def new(s):
        s.adj.append(0)
        s.n += 1
        return s.n - 1

def core(kind, q):
    g = G(q)
    for i, j in combinations(range(q), 2):
        if kind == "K":
            g.add(i, j)
        elif kind == "K-e" and not (i == 0 and j == 1):
            g.add(i, j)
        elif kind == "C" and (j == i + 1 or (i == 0 and j == q - 1)):
            g.add(i, j)
        elif kind == "P" and j == i + 1:
            g.add(i, j)
    if kind.startswith("Kbip"):
        a = int(kind.split(":")[1])
        g = G(q)
        for i in range(a):
            for j in range(a, q):
                g.add(i, j)
    return g

def emit_all(nmax, out):
    seen = set()
    kinds = ["K", "K-e", "C", "P"] + ["Kbip:%d" % a for a in (2, 3, 4)]
    for kind in kinds:
        for q in range(3, min(nmax, 13)):
            if kind.startswith("Kbip") and int(kind.split(":")[1]) >= q:
                continue
            for apex in range(0, 4):
                for p1 in range(0, 7):                 # pendant vertices
                    for p2 in range(0, 4):             # attached paths of length 2
                        g = core(kind, q)
                        base = g.n
                        for _ in range(apex):
                            a = g.new()
                            for c in range(q):
                                g.add(a, c)
                        for k in range(p1):
                            v = g.new()
                            g.add(v, k % q)
                        for k in range(p2):
                            u = g.new()
                            v = g.new()
                            g.add(u, (k + 1) % q)
                            g.add(u, v)
                        if 3 <= g.n <= nmax and connected(g.n, g.adj):
                            s = g6(g.n, g.adj)
                            if s not in seen:
                                seen.add(s)
                                out.write(s + "\n")
    # two cores joined by an edge or a path of length 2
    for k1 in ("K", "K-e", "C"):
        for k2 in ("K", "K-e", "C"):
            for q1 in range(3, 9):
                for q2 in range(3, 9):
                    for link in (1, 2):
                        for pend in range(0, 4):
                            g = core(k1, q1)
                            off = g.n
                            h = core(k2, q2)
                            for i in range(h.n):
                                g.new()
                            for i in range(h.n):
                                for j in range(i + 1, h.n):
                                    if h.adj[i] >> j & 1:
                                        g.add(off + i, off + j)
                            if link == 1:
                                g.add(0, off)
                            else:
                                m = g.new()
                                g.add(0, m)
                                g.add(m, off)
                            for t in range(pend):
                                v = g.new()
                                g.add(v, t % q1)
                            if 3 <= g.n <= nmax and connected(g.n, g.adj):
                                s = g6(g.n, g.adj)
                                if s not in seen:
                                    seen.add(s)
                                    out.write(s + "\n")
    return len(seen)

if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 18
    n = emit_all(nmax, sys.stdout)
    print("generated %d distinct graphs" % n, file=sys.stderr)
