/* wowclimb.c — SEARCH-SIDE simulated annealing over graphs of fixed order n.
 *
 * Exhaustive enumeration stops being possible around n=11, but the published
 * counterexamples to WOWII conjectures live at n=11..18. So for that range we hill-climb
 * on "distance to violation": the objective is lhs - rhs, and a positive value is a
 * candidate counterexample. The invariant code below is copied verbatim from wowscan.c,
 * which was cross-checked invariant-by-invariant against the frozen exact library on 850
 * graphs, so the two searchers cannot drift apart.
 *
 * This program NEVER decides anything. Whatever it reports is handed to the frozen
 * checker in mine/verify/, which is the only thing that decides.
 *
 * Build: gcc -O3 -o wowclimb wowclimb.c -lm
 * Usage: ./wowclimb <conjecture> <n> <restarts> <steps> [seed]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef uint32_t U;
static int N;
static U adj[24];
static U FULL;
static long long seen_graphs = 0, emitted = 0;
static int want[400];              /* which conjectures to scan */

static inline int pc(U x) { return __builtin_popcount(x); }
static inline int low(U x) { return __builtin_ctz(x); }

static int g6_decode(const char *s, int *nout, U *a) {
    const unsigned char *p = (const unsigned char *)s;
    int n, i, j;
    if (*p == 126) return -1;
    n = p[0] - 63; p++;
    if (n < 1 || n > 20) return -1;
    for (i = 0; i < n; i++) a[i] = 0;
    int bl = 0; unsigned cur = 0;
    for (j = 1; j < n; j++) for (i = 0; i < j; i++) {
        if (bl == 0) { if (*p < 63) return -1; cur = (unsigned)(*p++) - 63; bl = 6; }
        int bit = (cur >> (bl - 1)) & 1; bl--;
        if (bit) { a[i] |= (U)1 << j; a[j] |= (U)1 << i; }
    }
    *nout = n; return 0;
}

/* ---------- connectivity / acyclicity / bipartiteness on induced subsets ---------- */
static int conn_on(U S) {
    if (!S) return 0;
    U seen = S & -S, fr = seen;
    while (fr) { U nx = 0, f = fr;
        while (f) { int v = low(f); f &= f - 1; nx |= adj[v] & S & ~seen; }
        seen |= nx; fr = nx; }
    return seen == S;
}
static int edges_on(U S) { int e = 0; U s = S; while (s) { int v = low(s); s &= s - 1; e += pc(adj[v] & S); } return e / 2; }
static int acyclic_on(U S) {
    int comps = 0; U seen = 0, s = S;
    while (s) { int v = low(s); s &= s - 1;
        if (seen >> v & 1) continue;
        comps++; U st = (U)1 << v; seen |= st;
        U stack = st;
        while (stack) { int u = low(stack); stack &= stack - 1;
            U nb = adj[u] & S & ~seen; seen |= nb; stack |= nb; } }
    return edges_on(S) == pc(S) - comps;
}
static int bipartite_on(U S) {
    int col[24]; int i; for (i = 0; i < N; i++) col[i] = -1;
    U s = S;
    while (s) { int start = low(s); s &= s - 1;
        if (col[start] >= 0) continue;
        col[start] = 0; U stack = (U)1 << start;
        while (stack) { int u = low(stack); stack &= stack - 1;
            U nb = adj[u] & S;
            while (nb) { int wv = low(nb); nb &= nb - 1;
                if (col[wv] < 0) { col[wv] = 1 - col[u]; stack |= (U)1 << wv; }
                else if (col[wv] == col[u]) return 0; } } }
    return 1;
}
static int is_path_on(U S) {          /* induced subgraph is a path: tree with max degree <= 2 */
    if (!S) return 0;
    if (!conn_on(S) || !acyclic_on(S)) return 0;
    U s = S; while (s) { int v = low(s); s &= s - 1; if (pc(adj[v] & S) > 2) return 0; }
    return 1;
}

/* ---------- maxima over induced subsets, descending size with early exit ---------- */
static int max_induced(int (*pred)(U)) {
    int k;
    for (k = N; k >= 0; k--) {
        /* iterate subsets of size k via Gosper's hack */
        if (k == 0) return 0;
        U S = ((U)1 << k) - 1;
        while (S < ((U)1 << N)) {
            if (pred(S)) return k;
            U c = S & -S, r = S + c;
            if (!S) break;
            S = (((r ^ S) >> 2) / c) | r;
            if (S >= ((U)1 << N)) break;
        }
    }
    return 0;
}
static int f_forest(void)   { return max_induced(acyclic_on); }
static int b_bipart(void)   { return max_induced(bipartite_on); }

static int is_tree_on(U S) { return S && conn_on(S) && acyclic_on(S); }
static int tree_induced(void) { return max_induced(is_tree_on); }
static int path_induced(void) { return max_induced(is_path_on); }

/* ---------- independence ---------- */
static int alpha_best;
static void alpha_rec(U cand, int have) {
    if (have + pc(cand) <= alpha_best) return;
    if (!cand) { if (have > alpha_best) alpha_best = have; return; }
    int v = low(cand), bd = -1; U c = cand;
    while (c) { int u = low(c); c &= c - 1; int d = pc(adj[u] & cand); if (d > bd) { bd = d; v = u; } }
    alpha_rec(cand & ~((U)1 << v) & ~adj[v], have + 1);
    alpha_rec(cand & ~((U)1 << v), have);
}
static int alpha_on(U S) { alpha_best = 0; alpha_rec(S, 0); return alpha_best; }

/* ---------- domination ---------- */
static int gamma_c(void) {                       /* min connected dominating set */
    int k;
    for (k = 1; k <= N; k++) {
        U S = ((U)1 << k) - 1;
        while (S < ((U)1 << N)) {
            U cov = S, s = S;
            while (s) { int v = low(s); s &= s - 1; cov |= adj[v]; }
            if (cov == FULL && conn_on(S)) return k;
            U c = S & -S, r = S + c;
            S = (((r ^ S) >> 2) / c) | r;
            if (S >= ((U)1 << N)) break;
        }
    }
    return N;
}
static int gamma_t(void) {                       /* min total dominating set, -1 if none */
    int k;
    for (k = 1; k <= N; k++) {
        U S = ((U)1 << k) - 1;
        while (S < ((U)1 << N)) {
            U cov = 0, s = S;
            while (s) { int v = low(s); s &= s - 1; cov |= adj[v]; }
            if (cov == FULL) return k;
            U c = S & -S, r = S + c;
            S = (((r ^ S) >> 2) / c) | r;
            if (S >= ((U)1 << N)) break;
        }
    }
    return -1;
}

/* ---------- distances ---------- */
static int ecc_of(int s) {
    U seen = (U)1 << s, fr = seen; int d = 0;
    while (fr) { U nx = 0, f = fr;
        while (f) { int v = low(f); f &= f - 1; nx |= adj[v] & ~seen; }
        if (!nx) break; seen |= nx; fr = nx; d++; }
    return seen == FULL ? d : -1;
}
static int girth_of(void) {
    int best = 1 << 30, s;
    for (s = 0; s < N; s++) {
        int dist[24], par[24], q[24], qh = 0, qt = 0, i;
        for (i = 0; i < N; i++) { dist[i] = -1; par[i] = -1; }
        dist[s] = 0; q[qt++] = s;
        while (qh < qt) { int v = q[qh++]; U nb = adj[v];
            while (nb) { int u = low(nb); nb &= nb - 1;
                if (dist[u] < 0) { dist[u] = dist[v] + 1; par[u] = v; q[qt++] = u; }
                else if (u != par[v]) { int c = dist[u] + dist[v] + 1; if (c < best) best = c; } } }
    }
    return best == (1 << 30) ? -1 : best;
}
static int has_c4(void) {
    int u, v;
    for (u = 0; u < N; u++) for (v = u + 1; v < N; v++) if (pc(adj[u] & adj[v]) >= 2) return 1;
    return 0;
}
static int tri_at(int v) {
    int c = 0; U nb = adj[v];
    while (nb) { int a = low(nb); nb &= nb - 1;
        c += pc(adj[a] & adj[v] & ~(((U)1 << (a + 1)) - 1)); }
    return c;
}
static int ham_path(void) {
    static U reach[1 << 20];
    int sz = 1 << N, S, v;
    memset(reach, 0, (size_t)sz * sizeof(U));
    for (v = 0; v < N; v++) reach[1 << v] = (U)1 << v;
    for (S = 1; S < sz; S++) {
        U ends = reach[S];
        if (!ends) continue;
        if (S == sz - 1) return 1;
        U e = ends;
        while (e) { int u = low(e); e &= e - 1;
            U nb = adj[u] & ~(U)S;
            while (nb) { int wv = low(nb); nb &= nb - 1; reach[S | (1 << wv)] |= (U)1 << wv; } }
    }
    return reach[sz - 1] != 0;
}
static int cmpdesc(const void *a, const void *b) { return *(const int *)b - *(const int *)a; }
static int residue_of(void) {
    int d[24], n = N, i;
    for (i = 0; i < N; i++) d[i] = pc(adj[i]);
    while (1) { qsort(d, n, sizeof(int), cmpdesc);
        if (n == 0) return 0;
        if (d[0] == 0) return n;
        int k = d[0]; if (k >= n) return -1;
        for (i = 1; i <= k; i++) if (d[i] > 0) d[i]--;
        memmove(d, d + 1, (size_t)(n - 1) * sizeof(int)); n--; }
}
static int hh_zero_index(void) {
    int d[24], n = N, i, it = 0;
    for (i = 0; i < N; i++) d[i] = pc(adj[i]);
    while (1) { qsort(d, n, sizeof(int), cmpdesc);
        if (n == 0) return it;
        for (i = 0; i < n; i++) if (d[i] == 0) return it;
        int k = d[0]; if (k >= n) return it;
        for (i = 1; i <= k; i++) if (d[i] > 0) d[i]--;
        memmove(d, d + 1, (size_t)(n - 1) * sizeof(int)); n--; it++;
        if (it > 4 * N + 8) return it; }
}
static int minimal_tds_differ(void) {           /* are there two minimal TDS of different size? */
    int sz = 1 << N, S, first = -1;
    for (S = 1; S < sz; S++) {
        U cov = 0, s = (U)S;
        while (s) { int v = low(s); s &= s - 1; cov |= adj[v]; }
        if (cov != FULL) continue;
        int minimal = 1; U t = (U)S;
        while (t) { int v = low(t); t &= t - 1;
            U T = (U)S & ~((U)1 << v), c2 = 0, u = T;
            while (u) { int x = low(u); u &= u - 1; c2 |= adj[x]; }
            if (c2 == FULL) { minimal = 0; break; } }
        if (!minimal) continue;
        if (first < 0) first = pc((U)S);
        else if (pc((U)S) != first) return 1;
    }
    return 0;
}


/* ---------------- objectives: lhs - rhs, positive means candidate violation ---------- */
static int lv_[24], tri_[24], eccs_[24];
static int maxL_, sumL_, maxT_, minT_, freqT_, cC4_, diam_, rad_, sumEcc_, alpha_, girth_;

static void common(void) {
    int i;
    maxL_ = 0; sumL_ = 0; maxT_ = 0; minT_ = 1 << 30; freqT_ = 0;
    for (i = 0; i < N; i++) { lv_[i] = alpha_on(adj[i]); if (lv_[i] > maxL_) maxL_ = lv_[i]; sumL_ += lv_[i]; }
    for (i = 0; i < N; i++) { tri_[i] = tri_at(i); if (tri_[i] > maxT_) maxT_ = tri_[i]; if (tri_[i] < minT_) minT_ = tri_[i]; }
    for (i = 0; i < N; i++) if (tri_[i] == minT_) freqT_++;
    cC4_ = has_c4() ? 0 : 1;
    diam_ = 0; rad_ = 1 << 30; sumEcc_ = 0;
    for (i = 0; i < N; i++) { eccs_[i] = ecc_of(i); if (eccs_[i] > diam_) diam_ = eccs_[i];
                              if (eccs_[i] < rad_) rad_ = eccs_[i]; sumEcc_ += eccs_[i]; }
    alpha_ = alpha_on(FULL);
    girth_ = girth_of();
}

/* objective scaled by N so that averages stay integral */
static long long objective(int conj) {
    long long S = N;
    switch (conj) {
    case 19:  { int lhs = (sumEcc_ + maxL_ * N) / N; return (long long)(lhs - b_bipart()) * S; }
    case 40:  { int b = b_bipart(), f = f_forest();
                int lhs = (1 + b + 1 + 1) / 2;          /* p >= 1: a lower bound on the true lhs */
                return (long long)(lhs - f) * S; }
    case 61:  { int res = residue_of(); if (res < 0) return -1000 * S;
                return (long long)(res + (diam_ + 2) / 3 - f_forest()) * S; }
    case 100: { long long Sc = 0; int i;
                for (i = 0; i < N; i++) { long long dc = pc(FULL & ~adj[i] & ~((U)1 << i)); Sc += dc * dc; }
                int m = 0; while (1) { long long t = 4LL * m - 2LL * maxL_;
                                       if (t >= 0 && t * t >= Sc) break; m++; if (m > 100000) break; }
                return (long long)(alpha_ - m) * S; }
    case 133: { int fl = sumL_ / N, term = cC4_ ? fl : 1;
                return (long long)(rad_ + term - path_induced()) * S; }
    case 141: { if (girth_ < 0) return -1000 * S;
                return (long long)(girth_ / 2 - 1 + maxL_ - tree_induced()) * S; }
    case 160: { return (long long)(maxL_ + maxT_ * cC4_ - (N - gamma_c())) * S; }
    case 198: { /* want: b*N <= 2N + sumEcc (hypothesis) AND no Hamiltonian path */
                int b = b_bipart();
                long long slack = 2LL * N + sumEcc_ - (long long)b * N;   /* >= 0 = hypothesis holds */
                int ham = ham_path();
                if (!ham && slack >= 0) return 1;                       /* candidate */
                if (ham) return (slack >= 0 ? -1 : slack - 1) - S;      /* penalise traceability */
                return slack - 1; }
    case 291: { int gt = gamma_t(); if (gt < 0) return -1000 * S;
                return (long long)(gt - hh_zero_index() - freqT_) * S; }
    /* ---- POSITIVE CONTROLS: two conjectures already refuted in the literature.
       If the climber cannot rediscover a counterexample to these, then "flat" on the open
       conjectures says something about the searcher, not about the conjectures. ---- */
    case 194: { long long lhs = (long long)alpha_ * N, rhs = (long long)N + sumL_;
                int ham = ham_path();
                if (!ham && lhs <= rhs) return 1;
                if (ham) return (lhs <= rhs ? -1 : rhs - lhs - 1) - S;
                return rhs - lhs - 1; }
    case 200: { int tree = tree_induced();
                int rhs = 1 + (sumL_ + N - 1) / N;          /* ceil(1 + l_avg) */
                int ham = ham_path();
                long long d = -(long long)llabs(tree - rhs);
                if (!ham && tree == rhs) return 1;
                if (ham) return d - 1 - S;
                return d - 1; }
    case 314: { if (maxT_ > 0) return -(long long)maxT_ * S - S;        /* must be triangle-free */
                int p = path_induced();
                if (p > 4) return (long long)(4 - p) * S;               /* push the induced path down */
                return minimal_tds_differ() ? 1 : -1; }
    }
    return -1000 * S;
}

static unsigned long long rngstate;
static unsigned long long rnd(void) {
    rngstate ^= rngstate << 13; rngstate ^= rngstate >> 7; rngstate ^= rngstate << 17;
    return rngstate;
}

int main(int argc, char **argv) {
    if (argc >= 4 && !strcmp(argv[1], "--eval")) { /* handled below */ }
    else if (argc < 5) { fprintf(stderr,
        "usage: %s <conjecture:19|40|61|100|133|141|160|198|291|314|194|200> <n> <restarts> <steps> [seed]\n",
        argv[0]); return 2; }
    if (!strcmp(argv[1], "--eval")) {          /* --eval <conj> <graph6>: score one graph */
        int cj = atoi(argv[2]);
        if (g6_decode(argv[3], &N, adj) < 0) { fprintf(stderr, "bad graph6\n"); return 2; }
        FULL = ((U)1 << N) - 1; common();
        printf("conj %d on %s (n=%d): objective %lld\n", cj, argv[3], N, objective(cj));
        return 0;
    }
    int conj = atoi(argv[1]);
    N = atoi(argv[2]);
    int restarts = atoi(argv[3]), steps = atoi(argv[4]);
    rngstate = (argc > 5 ? strtoull(argv[5], NULL, 10) : 88172645463325252ULL) | 1;
    if (N < 3 || N > 20) { fprintf(stderr, "n out of range\n"); return 2; }
    FULL = ((U)1 << N) - 1;
    long long best_ever = -1LL << 40;
    int r, s, i, j;
    for (r = 0; r < restarts; r++) {
        /* Random connected start: a random spanning TREE plus sparse extra edges.
           An earlier version seeded with a random spanning PATH, which guarantees a
           Hamiltonian path and made the two positive controls (conjectures 194 and 200,
           whose counterexamples are non-traceable) unreachable by construction. A random
           attachment tree has many leaves, which is where the known counterexamples live. */
        int perm[24];
        for (i = 0; i < N; i++) perm[i] = i;
        for (i = N - 1; i > 0; i--) { int k = rnd() % (i + 1); int t = perm[i]; perm[i] = perm[k]; perm[k] = t; }
        for (i = 0; i < N; i++) adj[i] = 0;
        for (i = 1; i < N; i++) {
            int par = perm[rnd() % i];
            adj[perm[i]] |= (U)1 << par; adj[par] |= (U)1 << perm[i];
        }
        {
            int extra = rnd() % (N + 1);
            while (extra--) { i = rnd() % N; j = rnd() % N;
                if (i != j) { adj[i] |= (U)1 << j; adj[j] |= (U)1 << i; } }
        }
        common();
        long long cur = objective(conj);
        for (s = 0; s < steps; s++) {
            i = rnd() % N; j = rnd() % N;
            if (i == j) continue;
            adj[i] ^= (U)1 << j; adj[j] ^= (U)1 << i;             /* flip one edge */
            if (!conn_on(FULL)) { adj[i] ^= (U)1 << j; adj[j] ^= (U)1 << i; continue; }
            common();
            long long nxt = objective(conj);
            /* accept improvements always, equal moves often, worsening moves rarely */
            int accept = (nxt > cur) || (nxt == cur && (rnd() & 1)) ||
                         ((rnd() % 1000) < (unsigned)(3 + 40 * (steps - s) / (steps + 1)));
            if (accept) {
                cur = nxt;
                if (cur > best_ever) {
                    best_ever = cur;
                    fprintf(stderr, "conj %d n=%d restart %d step %d objective %lld\n",
                            conj, N, r, s, cur);
                }
                if (cur > 0) {
                    /* emit graph6 of a candidate and keep going */
                    char out[128]; int k = 0, bits = 0, acc = 0;
                    out[k++] = (char)(N + 63);
                    for (j = 1; j < N; j++) for (i = 0; i < j; i++) {
                        acc = (acc << 1) | ((adj[i] >> j) & 1); bits++;
                        if (bits == 6) { out[k++] = (char)(acc + 63); bits = 0; acc = 0; } }
                    if (bits) { acc <<= (6 - bits); out[k++] = (char)(acc + 63); }
                    out[k] = 0;
                    printf("wow2-%d %s objective=%lld\n", conj, out, cur);
                    fflush(stdout);
                }
            } else { adj[i] ^= (U)1 << j; adj[j] ^= (U)1 << i; common(); }
        }
    }
    fprintf(stderr, "conj %d n=%d: best objective over %d restarts x %d steps = %lld%s\n",
            conj, N, restarts, steps, best_ever,
            best_ever > 0 ? "  <-- CANDIDATE" : "  (flat: no violation found)");
    return 0;
}
