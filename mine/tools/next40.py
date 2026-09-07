#!/usr/bin/env python3
"""Rank the next 40 problems for run 2, using run 1's calibration rather than run 1's rubric.

The v2 rubric scored *classes*. Run 1's central finding is that what matters is the
FRONTIER: whether the search we can afford can exceed the search someone already published.
So v3 adds three terms that v2 did not have:

  +  frontier_headroom : can our reachable search plausibly go past the published one?
  -  already_swept     : is there evidence of a published exhaustive sweep at our reach?
  -  no_checker_shape  : is the witness a shape our verifier family can even express?

Run: python3 mine/tools/next40.py > mine/corpus/next40.md
"""
import json, re, collections

rows = [json.loads(l) for l in open("mine/corpus/problems.jsonl")]

# Problems attacked in run 1, with the frontier we reached.
RUN1 = {
    "wow2-141": ("exhausted to n=16 (all girth>=5 graphs)", "raise to n=18-19; the girth argument keeps it cheap"),
    "wow2-19": ("exhausted n<=10; annealing objective reaches 0 (tight) at n=11..13", "the tightest arm we found: equality is achieved but never exceeded, so it is the best candidate for a violation just past our reach"),
    "wow2-160": ("exhausted n<=10, families to n=18", "gate maxL+maxT*cC4 >= n is very restrictive; enumerate n=11..12 exhaustively"),
    "wow2-100": ("exhausted n<=10, families to n=18", "all invariants cheap; n=11 exhaustive is affordable"),
    "wow2-133": ("exhausted n<=10", "path>=diam+1 gate is strong; push n=11-12"),
    "wow2-291": ("exhausted n<=10", "all invariants cheap"),
    "wow2-314": ("exhausted n<=10", "triangle-free gate; enumerate triangle-free graphs to n=13"),
    "wow2-40": ("exhausted n<=10", "expensive arm (needs both f and b); needs a cheap necessary condition first"),
    "wow2-61": ("exhausted n<=10", "gate lhs>alpha; n=11 affordable"),
    "wow2-198a": ("exhausted n<=10", "gate alpha*n <= 2n+sum ecc"),
}

GRAPH_SHAPE = re.compile(r"\b(graph|graphs|digraph|tree|colou?ring|spanning|vertex|vertices|edge)\b", re.I)
SWEPT = re.compile(r"exhaustive|verified up to|checked for all|computer search|brute[- ]force|geng", re.I)
ARITH = re.compile(r"\b(integers?|n!|prime|factorial|diophantine|digits?)\b", re.I)

def score(r):
    s, why = float(r.get("tractability") or 0), []
    nl = (r.get("statement_nl") or "")
    txt = nl + " " + str(r.get("prior_attempts") or "") + " " + str(r.get("known_cases") or "")
    if r["id"] in RUN1:
        s += 2.0; why.append("run-1 arm with a measured frontier and a known way to extend it")
    if GRAPH_SHAPE.search(nl) and r.get("class") == "A":
        s += 1.5; why.append("witness is a graph: nauty makes our frontier concrete and extendable")
    if SWEPT.search(txt):
        s -= 2.5; why.append("evidence of a published exhaustive sweep at or beyond our reach")
    if ARITH.search(nl) and r.get("class") == "A":
        s -= 3.0; why.append("unbounded arithmetic witness: published frontiers are many orders of magnitude ahead")
    if r.get("class") == "B":
        s -= 2.0; why.append("class B needs a Groebner/SDP toolchain this environment could not install")
    if r.get("statement_formal"):
        s += 0.5; why.append("Lean statement already exists, so T3 is cheaper")
    return round(s, 2), why

scored = []
for r in rows:
    if not r.get("attack_eligible"):
        continue
    sc, why = score(r)
    scored.append((sc, r, why))
scored.sort(key=lambda t: (-t[0], t[1]["id"]))

print("# Recommended next 40 problems (run 2)\n")
print("Ranked by `mine/tools/next40.py`, which re-scores the corpus with run 1's calibration:")
print("frontier headroom counts, published exhaustive sweeps are a penalty, and a witness")
print("shape our verifier family cannot express is a penalty. **Write the checkers for all")
print("forty before freezing** -- run 1's largest process error was freezing mid-harvest.\n")
print("| # | id | class | score | statement (abridged) | why it is on the list |")
print("|---|---|---|---|---|---|")
for i, (sc, r, why) in enumerate(scored[:40], 1):
    nl = (r.get("statement_nl") or "").replace("\n", " ").replace("|", "/")[:110]
    reason = "; ".join(why[:2]) if why else "top of the re-scored corpus"
    if r["id"] in RUN1:
        reason = RUN1[r["id"]][1]
    print("| %d | `%s` | %s | %s | %s | %s |" % (i, r["id"], r.get("class"), sc, nl, reason))

print("\n## The ten run-1 arms and exactly where each stopped\n")
print("| id | frontier reached in run 1 | how to extend it |")
print("|---|---|---|")
for k, (front, ext) in RUN1.items():
    print("| `%s` | %s | %s |" % (k, front, ext))
