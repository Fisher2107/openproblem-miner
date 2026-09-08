#!/usr/bin/env python3
"""Class C -- Schur number lower bound.

A witness is an r-colouring of {1,...,n} with no monochromatic solution of x + y = z
(x and y need not be distinct, per the standard definition of the Schur number S(r) as
the largest n for which such a colouring exists). It certifies S(r) >= n.

Witness format:
  {"family": "schur", "r": 3, "n": 13,
   "colouring": [...],                  # colouring[i] is the colour of the integer i+1
   "published_value": 13}               # optional
"""
import sys, json

ACCEPT, REJECT, REFUSE = 0, 1, 2
if len(sys.argv) != 2:
    print("usage: check_schur_lower.py <witness.json>", file=sys.stderr)
    sys.exit(REFUSE)
try:
    w = json.load(open(sys.argv[1]))
    r, n = int(w["r"]), int(w["n"])
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

bad = None
for x in range(1, n + 1):
    for y in range(x, n + 1):
        z = x + y
        if z > n:
            break
        if col[x - 1] == col[y - 1] == col[z - 1]:
            bad = (x, y, z, col[x - 1])
            break
    if bad:
        break

print(json.dumps({"r": r, "n": n, "monochromatic_sum_found":
                  None if bad is None else {"x": bad[0], "y": bad[1], "z": bad[2], "colour": bad[3]}},
                 indent=2))
if bad is None:
    pub = w.get("published_value")
    print("ACCEPT: no monochromatic x+y=z in this %d-colouring of [1,%d]; certifies S(%d) >= %d."
          % (r, n, r, n))
    if pub is not None:
        print("NOTE: published value supplied is %s; this witness %s it."
              % (pub, "BEATS" if n > int(pub) else "does not beat"))
    sys.exit(ACCEPT)
print("REJECT: monochromatic %d + %d = %d in colour %d" % bad, file=sys.stderr)
sys.exit(REJECT)
