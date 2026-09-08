#!/usr/bin/env python3
"""Class C -- van der Waerden number lower bound.

A witness is an r-colouring of {1,...,n} with no monochromatic arithmetic progression of
length k; it certifies W(k,r) > n. Checked by direct enumeration of every AP of length k
inside [1,n], which is O(n^2 k) and leaves no room for a clever mistake.

Witness format:
  {"family": "vdw", "k": 3, "r": 2, "n": 8,
   "colouring": [0,0,1,1,0,0,1,1],      # colouring[i] is the colour of the integer i+1
   "published_lower_bound": 8}          # optional
"""
import sys, json

ACCEPT, REJECT, REFUSE = 0, 1, 2
if len(sys.argv) != 2:
    print("usage: check_vdw_lower.py <witness.json>", file=sys.stderr)
    sys.exit(REFUSE)
try:
    w = json.load(open(sys.argv[1]))
    k, r, n = int(w["k"]), int(w["r"]), int(w["n"])
    col = list(w["colouring"])
except Exception as e:
    print("REFUSE: %s" % e, file=sys.stderr)
    sys.exit(REFUSE)
if len(col) != n:
    print("REJECT: colouring has %d entries but n = %d" % (len(col), n), file=sys.stderr)
    sys.exit(REJECT)
if any(not (0 <= c < r) for c in col):
    print("REJECT: a colour is outside 0..%d" % (r - 1), file=sys.stderr)
    sys.exit(REJECT)
if k < 3:
    print("REFUSE: k must be at least 3", file=sys.stderr)
    sys.exit(REFUSE)

bad = None
for a in range(1, n + 1):
    for d in range(1, (n - a) // (k - 1) + 1 if k > 1 else 1):
        terms = [a + i * d for i in range(k)]
        if terms[-1] > n:
            break
        cs = {col[x - 1] for x in terms}
        if len(cs) == 1:
            bad = (terms, col[a - 1])
            break
    if bad:
        break

print(json.dumps({"k": k, "r": r, "n": n,
                  "monochromatic_AP_found": None if bad is None else
                  {"terms": bad[0], "colour": bad[1]}}, indent=2))
if bad is None:
    pub = w.get("published_lower_bound")
    print("ACCEPT: no monochromatic %d-term AP in an %d-colouring of [1,%d]; this certifies "
          "W(%d,%d) > %d." % (k, r, n, k, r, n))
    if pub is not None:
        print("NOTE: published lower bound supplied is %s; this witness %s it."
              % (pub, "BEATS" if n + 1 > int(pub) else "does not beat"))
    sys.exit(ACCEPT)
print("REJECT: monochromatic AP %s in colour %d" % (bad[0], bad[1]), file=sys.stderr)
sys.exit(REJECT)
