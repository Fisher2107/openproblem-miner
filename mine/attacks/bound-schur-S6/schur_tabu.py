#!/usr/bin/env python3
"""Tabu/greedy local search for r-colourings of [1,n] minimising the number of
monochromatic Schur triples (x+y=z, x<=y, standard condition matching the frozen
checker). Same incremental-conflict design as vdw_tabu.py.

Usage: schur_tabu.py r n seconds [seed]
"""
import sys, json, random, time

def all_triples(n):
    triples = []
    for x in range(1, n + 1):
        for y in range(x, n + 1):
            z = x + y
            if z > n:
                break
            triples.append((x, y, z))
    return triples

def run(r, n, seconds, seed=0):
    random.seed(seed)
    triples = all_triples(n)
    m = len(triples)
    elem_tr = [[] for _ in range(n + 1)]
    for idx, (x, y, z) in enumerate(triples):
        # x can equal y (standard Schur condition allows x=y); dedupe so a triple is
        # never double-counted in one element's incidence list (that caused a real
        # conflict-tracking bug: see log.md / negative-a2.jsonl).
        for e in {x, y, z}:
            elem_tr[e].append(idx)

    col = [random.randrange(r) for _ in range(n + 1)]

    def tr_mono(idx):
        x, y, z = triples[idx]
        return col[x] == col[y] == col[z]

    mono = [tr_mono(i) for i in range(m)]
    conflicts = sum(mono)
    best_conflicts = conflicts
    best_col = col[:]

    tabu = {}
    it = 0
    t_start = time.time()
    tabu_tenure = max(5, n // 20)
    stall = 0
    last_report = t_start
    while time.time() - t_start < seconds:
        it += 1
        if conflicts == 0:
            break
        bad = [i for i in range(m) if mono[i]]
        if not bad:
            break
        tr_idx = random.choice(bad)
        elem = random.choice(triples[tr_idx])
        cur_c = col[elem]
        best_delta = None
        best_c = None
        for c in range(r):
            if c == cur_c:
                continue
            delta = 0
            for idx in elem_tr[elem]:
                before = mono[idx]
                x, y, z = triples[idx]
                cx = c if x == elem else col[x]
                cy = c if y == elem else col[y]
                cz = c if z == elem else col[z]
                after = (cx == cy == cz)
                delta += (1 if after else 0) - (1 if before else 0)
            aspiration = (conflicts + delta) < best_conflicts
            if tabu.get((elem, c), -1) > it and not aspiration:
                continue
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_c = c
        if best_c is None:
            continue
        old_c = col[elem]
        col[elem] = best_c
        for idx in elem_tr[elem]:
            mono[idx] = tr_mono(idx)
        conflicts += best_delta
        tabu[(elem, old_c)] = it + tabu_tenure
        if conflicts < best_conflicts:
            best_conflicts = conflicts
            best_col = col[:]
            stall = 0
        else:
            stall += 1
        if time.time() - last_report > 15:
            print("  it=%d conflicts=%d best=%d elapsed=%.1fs" %
                  (it, conflicts, best_conflicts, time.time() - t_start), file=sys.stderr)
            last_report = time.time()
        if stall > 3000:
            for _ in range(max(1, n // 50)):
                e = random.randint(1, n)
                col[e] = random.randrange(r)
            mono[:] = [tr_mono(i) for i in range(m)]
            conflicts = sum(mono)
            stall = 0

    # Independent from-scratch recheck (do not trust the incremental tracker alone --
    # a prior version of this script double-counted x=y triples and reported false 0s).
    if best_conflicts == 0:
        full_col = [None] + best_col
        real_conflicts = sum(1 for (x, y, z) in triples if full_col[x] == full_col[y] == full_col[z])
        if real_conflicts != 0:
            print("INTERNAL BUG: incremental tracker said 0 but full recheck found %d "
                  "monochromatic triples -- discarding this witness" % real_conflicts,
                  file=sys.stderr)
            best_conflicts = real_conflicts

    return best_conflicts, best_col[1:]

if __name__ == "__main__":
    r, n, seconds = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    t0 = time.time()
    best_conflicts, best_col = run(r, n, seconds, seed)
    print("r=%d n=%d best_conflicts=%d wall=%.1fs" %
          (r, n, best_conflicts, time.time() - t0), file=sys.stderr)
    if best_conflicts == 0:
        print(json.dumps({"family": "schur", "r": r, "n": n, "colouring": best_col}))
