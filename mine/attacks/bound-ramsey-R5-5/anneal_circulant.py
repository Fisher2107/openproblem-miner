#!/usr/bin/env python3
"""Simulated annealing over circulant graphs for a (s,t,n)-Ramsey lower-bound witness.

Search space: symmetric connection sets S subset of {1..floor(n/2)} on Z_n.
Objective (to minimise, target 0): total number of monochromatic K_s cliques
plus total number of independent t-sets, computed EXACTLY (not sampled) by
exploiting vertex-transitivity of circulant graphs: every vertex of a
circulant graph is equivalent under the cyclic shift automorphism, so the
count of size-k structures through vertex 0 times n/k equals the total count.
This makes each evaluation cheap (only counts structures touching a single
fixed vertex) instead of enumerating all C(n,s) / C(n,t) subsets directly.

Usage: python3 anneal_circulant.py <s> <t> <n> <iters> <seed> [restarts]
Prints checkpoints and, on success (objective==0), writes a witness JSON
next to this script and exits 0. This script is NOT the verifier -- every
witness it emits still has to pass mine/verify/checkers/check_ramsey_lower.py
unmodified before it counts as anything.
"""
import sys, os, json, random, time
from itertools import combinations

def build_adj(n, S):
    adj = [0]*n
    for d in S:
        for i in range(n):
            j1 = (i+d) % n
            j2 = (i-d) % n
            adj[i] |= (1 << j1) | (1 << j2)
    return adj

def count_through_0(n, adj, k, want_clique):
    if want_clique:
        cand = [v for v in range(1, n) if (adj[0] >> v) & 1]
    else:
        cand = [v for v in range(1, n) if not ((adj[0] >> v) & 1)]
    cnt = 0
    for combo in combinations(cand, k-1):
        ok = True
        m = len(combo)
        for i in range(m):
            ai = adj[combo[i]]
            for j in range(i+1, m):
                bit = (ai >> combo[j]) & 1
                if want_clique and not bit:
                    ok = False; break
                if (not want_clique) and bit:
                    ok = False; break
            if not ok:
                break
        if ok:
            cnt += 1
    return cnt

def objective(n, S, s, t):
    adj = build_adj(n, S)
    c0 = count_through_0(n, adj, s, True)
    i0 = count_through_0(n, adj, t, False)
    total_cliques = n * c0 // s
    total_indep = n * i0 // t
    return total_cliques + total_indep, adj

def to_graph6(n, adj):
    # McKay graph6 encoder matching mine/verify/lib/exactgraph.decode_graph6's format
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (adj[i] >> j) & 1 else 0)
    while len(bits) % 6 != 0:
        bits.append(0)
    out = [chr(n + 63)]
    for k in range(0, len(bits), 6):
        chunk = bits[k:k+6]
        val = 0
        for b in chunk:
            val = (val << 1) | b
        out.append(chr(val + 63))
    return "".join(out)

def anneal(s, t, n, iters, seed, log=sys.stdout):
    random.seed(seed)
    half = n // 2
    universe = list(range(1, half+1))
    S = set(random.sample(universe, k=random.randint(1, len(universe))))
    best_obj, best_adj = objective(n, S, s, t)
    cur_obj = best_obj
    T0, T1 = 3.0, 0.02
    t0 = time.time()
    for it in range(iters):
        T = T0 * ((T1/T0) ** (it/max(1,iters-1)))
        d = random.choice(universe)
        newS = set(S)
        if d in newS: newS.discard(d)
        else: newS.add(d)
        if not newS:
            continue
        obj, adj = objective(n, newS, s, t)
        if obj <= cur_obj or random.random() < pow(2.718281828, -(obj-cur_obj)/max(T,1e-6)):
            S, cur_obj = newS, obj
            if obj < best_obj:
                best_obj, best_adj, best_S = obj, adj, set(S)
        if it % max(1, iters//20) == 0:
            print("iter=%d T=%.3f cur_obj=%d best_obj=%d elapsed=%.1fs S=%s" %
                  (it, T, cur_obj, best_obj, time.time()-t0, sorted(S)), file=log)
        if best_obj == 0:
            break
    return best_obj, best_adj, time.time()-t0

if __name__ == "__main__":
    s, t, n, iters, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    restarts = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    global_best = None
    for r in range(restarts):
        print("=== restart %d/%d seed=%d ===" % (r+1, restarts, seed+r))
        obj, adj, wall = anneal(s, t, n, iters, seed+r)
        print("restart %d done: best_obj=%d wall=%.1fs" % (r+1, obj, wall))
        if global_best is None or obj < global_best[0]:
            global_best = (obj, adj)
        if obj == 0:
            break
    obj, adj = global_best
    g6 = to_graph6(n, adj)
    print("FINAL best_obj=%d n=%d s=%d t=%d graph6=%s" % (obj, n, s, t, g6))
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sa_best_s%d_t%d_n%d.json" % (s,t,n))
    json.dump({"family":"ramsey","s":s,"t":t,"n":n,"graph6":g6,"objective":obj}, open(outpath,"w"))
    print("wrote", outpath)
