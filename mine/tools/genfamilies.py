#!/usr/bin/env python3
"""Generator-program search: enumerate STRUCTURED graph families, not random graphs.

The published counterexamples to WOWII conjectures 103, 194 and 200 all have the same
shape -- a dense core, a few apex vertices joined to all of it, and several pendant
vertices -- because pendants force high independence/low traceability while the core keeps
the averaged invariants small. So rather than annealing over arbitrary graphs (which
failed both positive controls), we enumerate a parameterised family of that shape. The
parameters ARE the program; this is the "evolve generator programs, not objects" rung of
the ladder, done exhaustively over a small parameter grid.

Emits graph6 on stdout for piping into ./mine/tools/wowscan.
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
        chunk = bits[k:k + 6]
        chunk += [0] * (6 - len(chunk))
        v = 0
        for b in chunk:
            v = (v << 1) | b
        out += chr(v + 63)
    return out

def build(core_kind, q, apex, zpair, pendants, pend_on_apex=0):
    """core on [0,q), apex vertices complete to the core, an optional z adjacent to exactly
    two core vertices, and pendant vertices hung on distinct core vertices."""
    n = q + apex + (1 if zpair else 0) + pendants + pend_on_apex
    if n > 20 or n < 3:
        return None
    adj = [0] * n
    def add(u, v):
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    for i, j in combinations(range(q), 2):
        if core_kind == "K":
            add(i, j)
        elif core_kind == "K-e":
            if not (i == 0 and j == 1):
                add(i, j)
        elif core_kind == "K-M":                     # clique minus a perfect matching
            if not (j == i + 1 and i % 2 == 0):
                add(i, j)
        elif core_kind == "C":                       # cycle
            if j == i + 1 or (i == 0 and j == q - 1):
                add(i, j)
        elif core_kind == "P":                       # path
            if j == i + 1:
                add(i, j)
    idx = q
    apex_ids = list(range(idx, idx + apex))
    for a in apex_ids:
        for c in range(q):
            add(a, c)
    idx += apex
    if zpair:
        z = idx
        add(z, 0)
        add(z, 1)
        idx += 1
    for k in range(pendants):                        # pendants on distinct core vertices
        p = idx + k
        add(p, (k + 2) % q)
    idx += pendants
    for k in range(pend_on_apex):
        p = idx + k
        if apex_ids:
            add(p, apex_ids[k % len(apex_ids)])
    # connectivity check
    seen, stack = {0}, [0]
    while stack:
        u = stack.pop()
        for v in range(n):
            if adj[u] >> v & 1 and v not in seen:
                seen.add(v)
                stack.append(v)
    if len(seen) != n:
        return None
    return n, adj

def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    seen = set()
    count = 0
    for kind in ("K", "K-e", "K-M", "C", "P"):
        for q in range(3, nmax):
            for apex in range(0, 5):
                for zp in (0, 1):
                    for pend in range(0, nmax):
                        for pa in range(0, 5):
                            r = build(kind, q, apex, zp, pend, pa)
                            if not r:
                                continue
                            n, adj = r
                            if n > nmax:
                                continue
                            s = g6(n, adj)
                            if s in seen:
                                continue
                            seen.add(s)
                            print(s)
                            count += 1
    print("generated %d distinct graphs" % count, file=sys.stderr)

if __name__ == "__main__":
    main()
