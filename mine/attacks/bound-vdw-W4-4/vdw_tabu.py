#!/usr/bin/env python3
"""Tabu / greedy local search for r-colourings of [1,n] minimising the number of
monochromatic k-term APs. Generic in k, r, n. Incremental conflict tracking:
for each element we precompute the list of AP-indices containing it, so a single
recolour only re-examines the APs touching that element.

Usage: vdw_tabu.py k r n seconds [seed]
Prints best conflict count found and, if 0, the witness JSON to stdout (last line).
"""
import sys, json, random, time

def all_aps(n, k):
    aps = []
    for a in range(1, n + 1):
        d = 1
        while True:
            terms = [a + i * d for i in range(k)]
            if terms[-1] > n:
                break
            aps.append(terms)
            d += 1
    return aps

def run(k, r, n, seconds, seed=0):
    random.seed(seed)
    aps = all_aps(n, k)
    m = len(aps)
    elem_aps = [[] for _ in range(n + 1)]  # 1-indexed
    for idx, terms in enumerate(aps):
        for t in terms:
            elem_aps[t].append(idx)

    col = [random.randrange(r) for _ in range(n + 1)]  # col[0] unused

    def ap_mono(idx):
        terms = aps[idx]
        c0 = col[terms[0]]
        for t in terms[1:]:
            if col[t] != c0:
                return False
        return True

    mono = [ap_mono(i) for i in range(m)]
    conflicts = sum(mono)
    best_conflicts = conflicts
    best_col = col[:]

    tabu = {}  # (elem,colour) -> iteration until which tabu
    it = 0
    t_start = time.time()
    tabu_tenure = max(5, n // 20)
    stall = 0
    last_report = t_start
    while time.time() - t_start < seconds:
        it += 1
        if conflicts == 0:
            break
        # pick a random element involved in a conflict
        bad_aps = [i for i in range(m) if mono[i]]
        if not bad_aps:
            break
        ap_idx = random.choice(bad_aps)
        elem = random.choice(aps[ap_idx])
        cur_c = col[elem]
        best_delta = None
        best_c = None
        for c in range(r):
            if c == cur_c:
                continue
            if tabu.get((elem, c), -1) > it and conflicts - 0 > 0:
                # allow aspiration if it would beat best
                pass
            # compute delta: recount APs touching elem before/after
            delta = 0
            for idx in elem_aps[elem]:
                before = mono[idx]
                terms = aps[idx]
                c0 = c if terms[0] == elem else col[terms[0]]
                after = all((c if t == elem else col[t]) == c0 for t in terms)
                delta += (1 if after else 0) - (1 if before else 0)
            aspiration = (conflicts + delta) < best_conflicts
            if tabu.get((elem, c), -1) > it and not aspiration:
                continue
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_c = c
        if best_c is None:
            continue
        # apply
        old_c = col[elem]
        col[elem] = best_c
        for idx in elem_aps[elem]:
            mono[idx] = ap_mono(idx)
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
            # perturb: randomise a chunk
            for _ in range(max(1, n // 50)):
                e = random.randint(1, n)
                col[e] = random.randrange(r)
            mono[:] = [ap_mono(i) for i in range(m)]
            conflicts = sum(mono)
            stall = 0

    return best_conflicts, best_col[1:]

if __name__ == "__main__":
    k, r, n, seconds = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    t0 = time.time()
    best_conflicts, best_col = run(k, r, n, seconds, seed)
    print("k=%d r=%d n=%d best_conflicts=%d wall=%.1fs" %
          (k, r, n, best_conflicts, time.time() - t0), file=sys.stderr)
    if best_conflicts == 0:
        print(json.dumps({"family": "vdw", "k": k, "r": r, "n": n, "colouring": best_col}))
