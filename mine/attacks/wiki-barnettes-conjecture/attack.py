#!/usr/bin/env python3
"""Barnette's conjecture: every 3-connected cubic bipartite planar graph is Hamiltonian.

Exhaustive over the class itself, which is small: geng generates connected cubic bipartite
graphs, networkx filters for planarity and 3-connectivity, and a backtracking search
decides Hamiltonicity. A counterexample would be a graph in the class with no Hamiltonian
cycle. NOTE: no frozen checker exists for this problem, so nothing found here could ship.
"""
import subprocess, sys
import networkx as nx

def decode_graph6(s):
    b = [ord(c) - 63 for c in s.strip()]
    n, rest = b[0], b[1:]
    bits = []
    for x in rest:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    G = nx.Graph(); G.add_nodes_from(range(n))
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: G.add_edge(i, j)
            k += 1
    return G

def hamiltonian_cycle(G):
    n = G.number_of_nodes()
    if n < 3: return False
    adj = {v: sorted(G[v]) for v in G}
    start = 0
    path = [start]; used = {start}
    def bt(v):
        if len(path) == n:
            return start in adj[v]
        # prune: remaining graph must stay connected to an unused vertex
        for u in adj[v]:
            if u not in used:
                used.add(u); path.append(u)
                if bt(u): return True
                path.pop(); used.discard(u)
        return False
    return bt(start)

def main():
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    for n in range(lo, hi + 1, 2):
        out = subprocess.run(["nauty-geng", "-qc", "-d3", "-D3", "-b", str(n)],
                             capture_output=True, text=True).stdout.split()
        inclass = 0; nonham = []
        for g6 in out:
            G = decode_graph6(g6)
            ok, _ = nx.check_planarity(G)
            if not ok: continue
            if nx.node_connectivity(G) < 3: continue
            inclass += 1
            if not hamiltonian_cycle(G):
                nonham.append(g6)
        print("n=%-3d cubic-bipartite=%-6d in-class(3-connected planar)=%-5d non-Hamiltonian=%d %s"
              % (n, len(out), inclass, len(nonham), nonham[:3]), flush=True)

if __name__ == "__main__":
    main()
