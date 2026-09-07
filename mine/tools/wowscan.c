/* wowscan.c — SEARCH-SIDE exhaustive screener for the ten open WOWII conjectures.
 *
 * Reads graph6 on stdin, writes candidate violations to stdout as
 *     <conjecture-id> <graph6>
 * This program is allowed to OVER-report (a candidate is only a suggestion) but must
 * never UNDER-report: every gate below is a provable necessary condition for violation,
 * and where no cheap necessary condition exists the quantity is computed exactly.
 * Every candidate it emits is then decided by the FROZEN checker in mine/verify/.
 * Nothing this program prints is a result.
 *
 * Build: gcc -O3 -march=native -o wowscan wowscan.c
 * Usage: nauty-geng -qc 9 | ./wowscan [--only 160,141,...]
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

/* ---- extra Class A targets attacked directly in wave 3 (see mine/attacks/) ---- */

/* Does G contain a cycle of length exactly L? DP over (subset, endpoint), anchored at the
   lowest vertex of the subset so each cycle is counted from one canonical start. */
static int has_cycle_len(int L) {
    if (L < 3 || L > N) return 0;
    static unsigned char reach[1 << 20][20];
    int sz = 1 << N, S, v, u;
    for (S = 0; S < sz; S++) for (v = 0; v < N; v++) reach[S][v] = 0;
    for (v = 0; v < N; v++) reach[1 << v][v] = 1;
    for (S = 1; S < sz; S++) {
        int anchor = low((U)S);
        if (pc((U)S) > L) continue;
        for (v = 0; v < N; v++) {
            if (!reach[S][v]) continue;
            if (pc((U)S) == L && (adj[v] >> anchor & 1) && v != anchor) return 1;
            U nb = adj[v] & ~(U)S;
            while (nb) { u = low(nb); nb &= nb - 1;
                if (u < anchor) continue;              /* keep the anchor lowest */
                reach[S | (1 << u)][u] = 1; }
        }
    }
    return 0;
}

/* max cut by exhaustive bipartition (n <= 20) */
static int max_cut(void) {
    int sz = 1 << N, S, best = 0;
    for (S = 0; S < sz / 2; S++) {
        int c = 0; U A = (U)S;
        U a = A;
        while (a) { int v = low(a); a &= a - 1; c += pc(adj[v] & ~A); }
        if (c > best) best = c;
    }
    return best;
}

static void emit(const char *id, const char *g6) { printf("%s %s\n", id, g6); emitted++; }

static int dump_mode = 0;

int main(int argc, char **argv) {
    int i;
    for (i = 0; i < 400; i++) want[i] = 1;
    for (i = 1; i < argc; i++) if (!strcmp(argv[i], "--dump")) dump_mode = 1;
    for (i = 1; i + 1 < argc; i++) if (!strcmp(argv[i], "--only")) {
        int j; for (j = 0; j < 400; j++) want[j] = 0;
        char *tok = strtok(argv[i + 1], ",");
        while (tok) { int id = atoi(tok); if (id > 0 && id < 400) want[id] = 1; tok = strtok(NULL, ","); }
    }
    char line[512];
    while (fgets(line, sizeof line, stdin)) {
        char *nl = strchr(line, '\n'); if (nl) *nl = 0;
        if (!*line) continue;
        if (g6_decode(line, &N, adj) < 0) continue;
        FULL = ((U)1 << N) - 1;
        seen_graphs++;
        if (N < 3) continue;
        if (!conn_on(FULL)) continue;

        /* cheap shared quantities */
        int lv[24], maxL = 0, sumL = 0, tri[24], maxT = 0, minT = 1 << 30, freqT = 0;
        for (i = 0; i < N; i++) { lv[i] = alpha_on(adj[i]); if (lv[i] > maxL) maxL = lv[i]; sumL += lv[i]; }
        for (i = 0; i < N; i++) { tri[i] = tri_at(i); if (tri[i] > maxT) maxT = tri[i]; if (tri[i] < minT) minT = tri[i]; }
        for (i = 0; i < N; i++) if (tri[i] == minT) freqT++;
        int cC4 = has_c4() ? 0 : 1;
        int eccs[24], diam = 0, rad = 1 << 30, sumEcc = 0;
        for (i = 0; i < N; i++) { eccs[i] = ecc_of(i); if (eccs[i] > diam) diam = eccs[i];
                                  if (eccs[i] < rad) rad = eccs[i]; sumEcc += eccs[i]; }
        int alpha = alpha_on(FULL);
        int girth = girth_of();

        if (dump_mode) {
            printf("%s cyc4=%d cyc5=%d cyc6=%d cyc8=%d maxcut=%d ", line,
                has_cycle_len(4), has_cycle_len(5), has_cycle_len(6), has_cycle_len(8), max_cut());
            printf("%s n=%d alpha=%d maxL=%d sumL=%d maxT=%d minT=%d freqT=%d cC4=%d "
                   "diam=%d rad=%d sumEcc=%d girth=%d Ls=%d f=%d b=%d tree=%d path=%d "
                   "gt=%d res=%d hh=%d ham=%d mtdsdiff=%d\n",
                   line, N, alpha, maxL, sumL, maxT, minT, freqT, cC4, diam, rad, sumEcc,
                   girth, N - gamma_c(), f_forest(), b_bipart(), tree_induced(), path_induced(),
                   gamma_t(), residue_of(), hh_zero_index(), ham_path(), minimal_tds_differ());
            continue;
        }

        /* ---- 160: maxL + maxT*cC4 <= Ls.   Ls <= N-1 for N>=3, so gate on lhs >= N. */
        if (want[160] && maxL + maxT * cC4 >= N) {
            int Ls = N - gamma_c();
            if (maxL + maxT * cC4 > Ls) emit("wow2-160", line);
        }
        /* ---- 141: floor(girth/2)-1+maxL <= tree.  tree >= maxL+1 (star at a vertex),
                 so violation forces floor(girth/2) > 2, i.e. girth >= 6. */
        if (want[141] && girth >= 6) {
            int tr = tree_induced();
            if (girth / 2 - 1 + maxL > tr) emit("wow2-141", line);
        }
        /* ---- 133: rad + floor(l_avg)^cC4 <= path.  path >= diam+1 (a shortest path is
                 induced), so gate on rhs-lower-bound. */
        if (want[133]) {
            int fl = sumL / N;                       /* floor of the average */
            int term = cC4 ? fl : 1;                 /* x^1 or x^0 */
            if (rad + term > diam + 1) {
                int p = path_induced();
                if (rad + term > p) emit("wow2-133", line);
            }
        }
        /* ---- 19: floor(avg_ecc + maxL) <= b.  b >= alpha, so gate on lhs > alpha. */
        if (want[19] && N >= 2) {
            int lhs = (sumEcc + maxL * N) / N;       /* floor((sumEcc/N) + maxL) */
            if (lhs > alpha) {
                int b = b_bipart();
                if (lhs > b) emit("wow2-19", line);
            }
        }
        /* ---- 61: residue + ceil(diam/3) <= f.  f >= alpha, so gate on lhs > alpha. */
        if (want[61]) {
            int res = residue_of();
            int lhs = res + (diam + 2) / 3;
            if (res >= 0 && lhs > alpha) {
                int f = f_forest();
                if (lhs > f) emit("wow2-61", line);
            }
        }
        /* ---- 100: alpha <= ceil((maxL + sqrt(S_c)/2)/2), all cheap. Exact integer test:
                 the smallest m with 4m - 2*maxL >= 0 and (4m-2maxL)^2 >= S_c. */
        if (want[100]) {
            long long Sc = 0;
            for (i = 0; i < N; i++) { long long dc = (long long)pc(FULL & ~adj[i] & ~((U)1 << i)); Sc += dc * dc; }
            int m = 0;
            while (1) { long long t = 4LL * m - 2LL * maxL;
                        if (t >= 0 && t * t >= Sc) break; m++; if (m > 100000) break; }
            if (alpha > m) emit("wow2-100", line);
        }
        /* ---- 198a: b <= 2 + avg_ecc  =>  Hamiltonian path.  b >= alpha, so the
                 hypothesis forces alpha*N <= 2N + sumEcc. */
        if (want[198] && (long long)alpha * N <= 2LL * N + sumEcc) {
            int b = b_bipart();
            if ((long long)b * N <= 2LL * N + sumEcc && !ham_path()) emit("wow2-198a", line);
        }
        /* ---- 291: gamma_t <= k + freq_min_T, all cheap enough to compute exactly. */
        if (want[291] && N > 2) {
            int gt = gamma_t();
            if (gt > 0 && gt > hh_zero_index() + freqT) emit("wow2-291", line);
        }
        /* ---- 314: triangle-free and induced path <= 4 => well totally dominated.
                 path >= diam+1 forces diam <= 3. */
        if (want[314] && maxT == 0 && diam <= 3) {
            if (path_induced() <= 4 && minimal_tds_differ()) emit("wow2-314", line);
        }
        /* ---- graffiti-3: alpha(G) >= rad(G) for connected G. Cheap, exact. ---- */
        if (want[900] && alpha < rad) emit("graffiti-3", line);

        /* ---- erdos-0064: every graph of min degree >= 3 has a cycle of length 2^k, k>=2.
                A counterexample has min degree >= 3 and no cycle of length 4, 8, 16, ... ---- */
        if (want[901]) {
            int mind = N, i2;
            for (i2 = 0; i2 < N; i2++) { int d = pc(adj[i2]); if (d < mind) mind = d; }
            if (mind >= 3) {
                int L, bad = 0;
                for (L = 4; L <= N; L *= 2) if (has_cycle_len(L)) { bad = 1; break; }
                if (!bad) emit("erdos-0064", line);
            }
        }

        /* ---- erdos-0023: every triangle-free graph on 5k vertices can be made bipartite
                by deleting at most k^2 edges. Violation: m - maxcut > k^2. ---- */
        if (want[902] && maxT == 0 && N % 5 == 0) {
            int k = N / 5, m = 0, i3;
            for (i3 = 0; i3 < N; i3++) m += pc(adj[i3]);
            m /= 2;
            if (m - max_cut() > k * k) emit("erdos-0023", line);
        }

        /* ---- 40: ceil((p+b+1)/2) <= f.  No cheap necessary condition is available
                 (f and b are both needed), so this one is computed exactly and is the
                 expensive arm; it is gated by --only in practice. */
        if (want[40] && N >= 2) {
            int f = f_forest(), b = b_bipart();
            int lhs1 = (1 + b + 1 + 1) / 2;          /* p >= 1 gives a lower bound on lhs */
            if (lhs1 > f) emit("wow2-40?p", line);   /* '?p' = needs the exact path cover number */
        }
    }
    fprintf(stderr, "scanned %lld graphs, emitted %lld candidate(s)\n", seen_graphs, emitted);
    return 0;
}
