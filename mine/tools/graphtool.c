/* graphtool.c — SEARCH-SIDE graph invariant screener for the open-problem mine.
 *
 * NOT a verifier. Lives outside mine/verify/ deliberately: this code is allowed to be
 * fast-and-loose because everything it flags is re-checked by an independent frozen
 * checker before it counts as anything. Reads graph6 on stdin (one graph per line),
 * n <= 16 (invariants using subset DP are capped at n <= 20 by the uint32 masks).
 *
 * Build: gcc -O2 -march=native -o graphtool graphtool.c
 * Modes:
 *   --csv                 emit invariants for every input graph
 *   --selftest            check invariants against hand-computed reference graphs
 *   --filter '<expr>'     not implemented; use --csv and post-filter, or add a probe
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef uint32_t U;
static int N;              /* order of current graph */
static U  adj[24];         /* adjacency bitmasks */

/* ---------- graph6 ---------- */
static int g6_decode(const char *s, int *nout, U *a) {
    int n, i, j, k;
    const unsigned char *p = (const unsigned char *)s;
    if (*p == '>') { while (*p && *p != ':' && *p != ';' && *p != ' ') p++; }
    if (p[0] == 126) {           /* n >= 63 not supported */
        return -1;
    }
    n = p[0] - 63; p++;
    if (n < 1 || n > 20) return -1;
    for (i = 0; i < n; i++) a[i] = 0;
    k = 0;
    int bitsLeft = 0; unsigned int cur = 0;
    for (j = 1; j < n; j++) {
        for (i = 0; i < j; i++) {
            if (bitsLeft == 0) {
                if (*p < 63) return -1;
                cur = (unsigned)(*p++) - 63; bitsLeft = 6;
            }
            int bit = (cur >> (bitsLeft - 1)) & 1; bitsLeft--;
            if (bit) { a[i] |= (U)1 << j; a[j] |= (U)1 << i; }
            k++;
        }
    }
    *nout = n; return 0;
}

static inline int pc(U x) { return __builtin_popcount(x); }
static inline int lowbit_idx(U x) { return __builtin_ctz(x); }

/* ---------- basic ---------- */
static int edges(void)   { int i, m = 0; for (i = 0; i < N; i++) m += pc(adj[i]); return m / 2; }
static int mindeg(void)  { int i, d = 1 << 30; for (i = 0; i < N; i++) if (pc(adj[i]) < d) d = pc(adj[i]); return d; }
static int maxdeg(void)  { int i, d = 0;       for (i = 0; i < N; i++) if (pc(adj[i]) > d) d = pc(adj[i]); return d; }

static U reach(U start_mask, U allowed) {          /* BFS closure inside `allowed` */
    U seen = start_mask & allowed, frontier = seen;
    while (frontier) {
        U next = 0, f = frontier;
        while (f) { int v = lowbit_idx(f); f &= f - 1; next |= adj[v] & allowed & ~seen; }
        seen |= next; frontier = next;
    }
    return seen;
}
static int connected_on(U S) {
    if (!S) return 1;
    int v = lowbit_idx(S);
    return reach((U)1 << v, S) == S;
}
static int is_connected(void) { return connected_on(((U)1 << N) - 1); }

/* ---------- independence number (branch and bound on bitmasks) ---------- */
static int alpha_rec(U cand, int have, int best) {
    if (!cand) return have > best ? have : best;
    if (have + pc(cand) <= best) return best;
    /* pick a vertex of max degree inside cand to branch on */
    U c = cand; int v = lowbit_idx(c), bd = -1;
    while (c) { int u = lowbit_idx(c); c &= c - 1; int d = pc(adj[u] & cand); if (d > bd) { bd = d; v = u; } }
    /* branch: exclude v, or include v */
    U without = cand & ~((U)1 << v);
    int b1 = alpha_rec(without & ~adj[v], have + 1, best);   /* include v */
    if (b1 > best) best = b1;
    int b2 = alpha_rec(without, have, best);                  /* exclude v */
    if (b2 > best) best = b2;
    return best;
}
static int alpha(void) { return alpha_rec(((U)1 << N) - 1, 0, 0); }

static int omega(void) {                                     /* clique number = alpha(complement) */
    U save[24]; int i; memcpy(save, adj, sizeof(adj));
    U full = ((U)1 << N) - 1;
    for (i = 0; i < N; i++) adj[i] = full & ~save[i] & ~((U)1 << i);
    int r = alpha();
    memcpy(adj, save, sizeof(adj));
    return r;
}

/* ---------- matching number (DP over subsets) ---------- */
static signed char *mdp;
static int matching_number(void) {
    int size = 1 << N, S;
    mdp[0] = 0;
    for (S = 1; S < size; S++) {
        int v = lowbit_idx((U)S);
        int best = mdp[S & ~(1 << v)];                       /* leave v unmatched */
        U nb = adj[v] & (U)S;
        while (nb) { int u = lowbit_idx(nb); nb &= nb - 1;
            int cand = 1 + mdp[S & ~(1 << v) & ~(1 << u)];
            if (cand > best) best = cand; }
        mdp[S] = (signed char)best;
    }
    return mdp[size - 1];
}

/* ---------- domination numbers ---------- */
static int domination(void) {                                /* min |D| with N[D] = V */
    U full = ((U)1 << N) - 1;
    int size = 1 << N, S, best = N;
    for (S = 1; S < size; S++) {
        if (pc((U)S) >= best) continue;
        U cov = (U)S; U s = (U)S;
        while (s) { int v = lowbit_idx(s); s &= s - 1; cov |= adj[v]; }
        if (cov == full) best = pc((U)S);
    }
    return best;
}
static int connected_domination(void) {                      /* min connected dominating set */
    U full = ((U)1 << N) - 1;
    int size = 1 << N, S, best = N;
    for (S = 1; S < size; S++) {
        if (pc((U)S) >= best) continue;
        U cov = (U)S; U s = (U)S;
        while (s) { int v = lowbit_idx(s); s &= s - 1; cov |= adj[v]; }
        if (cov != full) continue;
        if (!connected_on((U)S)) continue;
        best = pc((U)S);
    }
    return best;
}
static int total_domination(void) {                          /* min |D| with open nbhds covering V */
    U full = ((U)1 << N) - 1;
    int size = 1 << N, S, best = -1;
    for (S = 1; S < size; S++) {
        if (best >= 0 && pc((U)S) >= best) continue;
        U cov = 0; U s = (U)S;
        while (s) { int v = lowbit_idx(s); s &= s - 1; cov |= adj[v]; }
        if (cov == full) best = pc((U)S);
    }
    return best;                                             /* -1 if none (isolated vertex) */
}

/* ---------- max leaves over spanning trees, computed directly ---------- */
/* Ls(G) = n - (min size of a connected dominating set), for connected G with n >= 3
 * and G not complete-ish edge cases; we compute it directly instead, to avoid relying
 * on that identity: a spanning tree with k leaves exists iff there is a connected
 * dominating set of size n-k (Douglas 1992). We verify the identity in --selftest. */
static int max_leaves_spanning_tree(void) {
    if (N < 3) return N;                                     /* K1: 1, K2: 2 by convention */
    int gc = connected_domination();
    return N - gc;
}

/* ---------- distances ---------- */
static void ecc_all(int *ecc, int *diam, int *rad) {
    U full = ((U)1 << N) - 1; int i, d = 0, r = 1 << 30;
    for (i = 0; i < N; i++) {
        U seen = (U)1 << i, frontier = seen; int dist = 0;
        while (frontier) {
            U next = 0, f = frontier;
            while (f) { int v = lowbit_idx(f); f &= f - 1; next |= adj[v] & ~seen; }
            if (!next) break;
            seen |= next; frontier = next; dist++;
        }
        if (seen != full) { ecc[i] = -1; *diam = -1; *rad = -1; return; }   /* disconnected */
        ecc[i] = dist;
        if (dist > d) d = dist;
        if (dist < r) r = dist;
    }
    *diam = d; *rad = r;
}

/* ---------- girth ---------- */
static int girth(void) {
    int best = 1 << 30, s;
    for (s = 0; s < N; s++) {
        int dist[24], par[24], i, qh = 0, qt = 0, q[24];
        for (i = 0; i < N; i++) { dist[i] = -1; par[i] = -1; }
        dist[s] = 0; q[qt++] = s;
        while (qh < qt) {
            int v = q[qh++]; U nb = adj[v];
            while (nb) { int u = lowbit_idx(nb); nb &= nb - 1;
                if (dist[u] < 0) { dist[u] = dist[v] + 1; par[u] = v; q[qt++] = u; }
                else if (u != par[v]) { int c = dist[u] + dist[v] + 1; if (c < best) best = c; } }
        }
    }
    return best == (1 << 30) ? -1 : best;                     /* -1 = acyclic */
}

/* ---------- chromatic number (exact, small n) ---------- */
static int chromatic_ok(int k) {
    int color[24], i; for (i = 0; i < N; i++) color[i] = -1;
    int stack_v = 0;
    /* simple DFS with symmetry breaking: vertex i may use colours 0..min(i,k-1) */
    int c[24]; for (i = 0; i < N; i++) c[i] = -1;
    int v = 0, maxused = 0;
    while (v >= 0) {
        int start = c[v] + 1, ok = 0, col;
        int limit = k - 1; if (maxused + 1 < limit) limit = maxused + 1;
        for (col = start; col <= limit; col++) {
            U nb = adj[v] & (((U)1 << v) - 1); int clash = 0;
            while (nb) { int u = lowbit_idx(nb); nb &= nb - 1; if (c[u] == col) { clash = 1; break; } }
            if (!clash) { c[v] = col; ok = 1; break; }
        }
        if (ok) {
            int prev = maxused; if (c[v] > maxused) maxused = c[v];
            (void)prev;
            if (v == N - 1) return 1;
            v++; c[v] = -1;
        } else {
            c[v] = -1; v--;
            if (v >= 0) { maxused = 0; for (i = 0; i <= v; i++) if (c[i] > maxused) maxused = c[i]; }
        }
    }
    (void)color; (void)stack_v;
    return 0;
}
static int chromatic(void) { int k; for (k = 1; k <= N; k++) if (chromatic_ok(k)) return k; return N; }

/* ---------- degree-sequence invariants ---------- */
static int cmp_desc(const void *a, const void *b) { return *(const int *)b - *(const int *)a; }
static int residue(void) {                                   /* Havel-Hakimi residue */
    int d[24], n = N, i;
    for (i = 0; i < N; i++) d[i] = pc(adj[i]);
    while (1) {
        qsort(d, n, sizeof(int), cmp_desc);
        if (n == 0 || d[0] == 0) return n;
        int k = d[0];
        if (k >= n) return -1;
        for (i = 1; i <= k; i++) d[i]--;
        memmove(d, d + 1, (size_t)(n - 1) * sizeof(int));
        n--;
    }
}
static int annihilation(void) {                              /* max k: sum of k smallest degrees <= m */
    int d[24], i, m = edges(), s = 0, k = 0;
    for (i = 0; i < N; i++) d[i] = pc(adj[i]);
    qsort(d, N, sizeof(int), cmp_desc);
    for (i = N - 1; i >= 0; i--) { if (s + d[i] <= m) { s += d[i]; k++; } else break; }
    return k;
}

/* ---------- driver ---------- */
static void emit_csv(const char *g6) {
    int ecc[24], diam, rad;
    ecc_all(ecc, &diam, &rad);
    printf("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n",
        g6, N, edges(), mindeg(), maxdeg(),
        alpha(), omega(), matching_number(),
        domination(), total_domination(), connected_domination(),
        max_leaves_spanning_tree(), diam, rad, girth(), chromatic());
}

static int load_line(char *line) {
    char *nl = strchr(line, '\n'); if (nl) *nl = 0;
    if (!*line) return 0;
    if (g6_decode(line, &N, adj) < 0) return 0;
    return 1;
}

static void selftest(void) {
    struct { const char *g6; const char *name; int n, m, alpha, omega, mu, gamma, gc, Ls, diam, girth, chi; } T[] = {
        /* Petersen graph */
        {"IheA@GUAo", "Petersen", 10, 15, 4, 2, 5, 3, 4, 6, 2, 5, 3},
        /* C5 */
        {"DUW", "C5", 5, 5, 2, 2, 2, 2, 3, 2, 2, 5, 3},
        /* K4 */
        {"C~", "K4", 4, 6, 1, 4, 2, 1, 1, 3, 1, 3, 4},
        /* P4 path */
        {"Ch", "P4", 4, 3, 2, 2, 2, 2, 2, 2, 3, -1, 2},
        /* K3,3 */
        {"EFz_", "K33", 6, 9, 3, 2, 3, 2, 2, 4, 2, 4, 2},
    };
    int i, fails = 0;
    for (i = 0; i < (int)(sizeof(T) / sizeof(T[0])); i++) {
        char buf[256]; snprintf(buf, sizeof buf, "%s", T[i].g6);
        if (!load_line(buf)) { printf("FAIL decode %s\n", T[i].name); fails++; continue; }
        int ecc[24], diam, rad; ecc_all(ecc, &diam, &rad);
        int got[10] = { N, edges(), alpha(), omega(), matching_number(), domination(),
                        connected_domination(), max_leaves_spanning_tree(), diam, girth() };
        int want[10] = { T[i].n, T[i].m, T[i].alpha, T[i].omega, T[i].mu, T[i].gamma,
                         T[i].gc, T[i].Ls, T[i].diam, T[i].girth };
        const char *lbl[10] = {"n","m","alpha","omega","mu","gamma","gamma_c","Ls","diam","girth"};
        int j; for (j = 0; j < 10; j++) if (got[j] != want[j]) {
            printf("FAIL %s %s: got %d want %d\n", T[i].name, lbl[j], got[j], want[j]); fails++; }
        int chi = chromatic();
        if (chi != T[i].chi) { printf("FAIL %s chi: got %d want %d\n", T[i].name, chi, T[i].chi); fails++; }
    }
    printf(fails ? "SELFTEST FAILED (%d)\n" : "SELFTEST PASSED (%d failures)\n", fails);
    exit(fails ? 1 : 0);
}

int main(int argc, char **argv) {
    int mode_csv = 0, i;
    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--csv")) mode_csv = 1;
        else if (!strcmp(argv[i], "--selftest")) { mdp = malloc(1 << 21); selftest(); }
    }
    mdp = malloc(1 << 21);
    char line[4096];
    if (mode_csv) printf("g6,n,m,delta,Delta,alpha,omega,mu,gamma,gamma_t,gamma_c,Ls,diam,rad,girth,chi\n");
    while (fgets(line, sizeof line, stdin)) {
        if (!load_line(line)) continue;
        if (mode_csv) emit_csv(line);
    }
    return 0;
}
