"""Reproduces the N=10^18 frontier claim in log.md for erdos-0366-c."""
from kfull_gen import cubefull_upto
import time

if __name__ == "__main__":
    t0 = time.time()
    Q = cubefull_upto(10**18)
    Qset = set(Q.tolist())
    found = None
    for v in Q:
        v = int(v)
        if v + 1 in Qset:
            found = (v, v+1)
            break
    print(f"{len(Q)} cube-full numbers <= 1e18, generated in {time.time()-t0:.2f}s")
    print("consecutive 3-full pair found:", found)
