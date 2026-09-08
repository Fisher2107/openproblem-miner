"""
erdos-0647-a: tau(n) = divisor count. Is there n>24 with max_{m<n}(m+tau(m)) <= n+2 ?
True for n=24. Sieve tau via numpy divisor-counting sieve, track running max, scan.
"""
import numpy as np, time, sys

def run(N):
    t0 = time.time()
    tau = np.zeros(N+1, dtype=np.int32)
    for d in range(1, N+1):
        tau[d::d] += 1
    t1 = time.time()
    vals = np.arange(N+1, dtype=np.int64) + tau
    running_max = np.maximum.accumulate(vals)
    # condition for n: running_max[n-1] <= n+2  (max over m<n, i.e. m=0..n-1)
    n_arr = np.arange(N+1, dtype=np.int64)
    cond = np.zeros(N+1, dtype=bool)
    cond[1:] = running_max[:-1] <= (n_arr[1:] + 2)
    hits = np.where(cond & (n_arr > 24))[0]
    t2 = time.time()
    return tau, running_max, hits, t1-t0, t2-t1

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
    tau, rm, hits, sieve_t, scan_t = run(N)
    print(f"N={N} sieve_time={sieve_t:.2f}s scan_time={scan_t:.2f}s")
    print(f"hits (n>24 with max_(m<n)(m+tau(m))<=n+2): {hits[:20].tolist()} (total {len(hits)})")
    print("running max final value:", int(rm[N]), " n+2 at N:", N+2)
