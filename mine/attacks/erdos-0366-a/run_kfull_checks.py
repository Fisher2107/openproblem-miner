import time, sys
from kfull_gen import powerful_upto, cubefull_upto
import numpy as np

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10**12

t0 = time.time()
P = powerful_upto(N)   # 2-full ("powerful") numbers <= N, sorted unique
t1 = time.time()
Q = cubefull_upto(N)   # 3-full ("cube-full") numbers <= N, sorted unique
t2 = time.time()

print(f"N={N}")
print(f"|P| (2-full) = {len(P)}, gen time {t1-t0:.2f}s")
print(f"|Q| (3-full) = {len(Q)}, gen time {t2-t1:.2f}s")

# --- erdos-0364-a: consecutive TRIPLE of powerful (2-full) numbers ---
# look for a,a+1,a+2 all in P
Pset = set(P.tolist())
found_triple = None
for v in P:
    v = int(v)
    if v+1 in Pset and v+2 in Pset:
        found_triple = (v, v+1, v+2)
        break
print("erdos-0364-a consecutive powerful triple found:", found_triple)

# --- erdos-0366-c: consecutive PAIR of 3-full integers ---
Qset = set(Q.tolist())
found_pair_33 = None
for v in Q:
    v = int(v)
    if v+1 in Qset:
        found_pair_33 = (v, v+1)
        break
print("erdos-0366-c consecutive 3-full pair found (excluding known 12167/12168):", found_pair_33)

# --- erdos-0366-a: 2-full n with n+1 3-full ---
found_23 = None
for v in P:
    v = int(v)
    if v+1 in Qset:
        found_23 = (v, v+1)
        break
print("erdos-0366-a: 2-full n with n+1 3-full, found:", found_23)

t3 = time.time()
print(f"check time {t3-t2:.2f}s, total {t3-t0:.2f}s")
