#!/usr/bin/env python3
"""Refresh the n=11 sweep numbers in mine/REPORT.md from the sweep log.

The n=11 exhaustive sweep is sliced by edge count so that an interrupted run still states
something exact ("every connected graph on 11 vertices with at most k edges") rather than
nothing. This script re-reads the log and rewrites the three places in the report that
quote its numbers, so the report can never drift from the log. Idempotent; run it whenever
the sweep has advanced. Exits nonzero if any slice reported a candidate, since that would
mean the report's headline negative needs revisiting rather than a number bump.
"""
import re, sys

LOG = "mine/attacks/wave2-wowii-families/n11_sweep.log"
REPORT = "mine/REPORT.md"

# every other exhaustive sweep in the run, fixed and finished
OTHER = {
    "n<=10, all ten WOWII conjectures": 11989762,
    "conj 141, all girth>=5 graphs, n=11..16": 20147011,
    "graffiti-3, all connected graphs n<=10": 11989762,
    "erdos-0064 (min degree>=3), n<=10": 5290114,
    "Erdos-Gyarfas (cubic), n<=20": 556470,
    "erdos-0023 (triangle-free), n=5,10": 9838,
    "generator families 1 and 2": 20908,
    "Barnette (cubic bipartite), n<=24": 34622,
}

lines = [l for l in open(LOG) if l.startswith("edges=")]
if not lines:
    print("no slices recorded yet"); sys.exit(0)
tot = sum(int(re.search(r"scanned (\d+)", l).group(1)) for l in lines)
maxe = max(int(re.search(r"edges=(\d+)", l).group(1)) for l in lines)
cands = sum(int(re.search(r"emitted (\d+)", l).group(1)) for l in lines)
text = open(LOG).read()
done = "N11 SLICED SWEEP COMPLETE" in text
stopped = "N11 SLICED SWEEP STOPPED" in text
grand = sum(OTHER.values()) + tot

s = open(REPORT).read()
status = "complete" if done else ("stopped partway, by choice" if stopped else "still running")
s = re.sub(r"\| exhaustive n = 11, cheap arms, sliced by edge count \([^)]*\) \| [0-9,]+ graphs[^|]*\| \d+ \|",
           "| exhaustive n = 11, cheap arms, sliced by edge count (%s) | %s graphs — every connected graph on 11 vertices with at most %d edges | %d |"
           % (status, format(tot, ","), maxe, cands), s)
s = re.sub(r"\| exhaustive n = 11 \(cheap arms\), edge counts 10\.\.\d+ — [^|]*\| [0-9,]+ \|",
           "| exhaustive n = 11 (cheap arms), edge counts 10..%d — %s | %s |"
           % (maxe, status, format(tot, ",")), s)
s = re.sub(r"\| \*\*total\*\* \| \*\*[0-9,]+\*\* \|", "| **total** | **%s** |" % format(grand, ","), s)
s = re.sub(r"\| graph-conjecture evaluations, exhaustive \| \*\*[0-9,]+\*\* \|",
           "| graph-conjecture evaluations, exhaustive | **%s** |" % format(grand, ","), s)
open(REPORT, "w").write(s)

print("n=11: %d slice(s), edges<=%d, %s graphs, %d candidates, %s"
      % (len(lines), maxe, format(tot, ","), cands, status))
print("grand total across all exhaustive sweeps: %s" % format(grand, ","))
if cands:
    print("A SLICE REPORTED A CANDIDATE — the negative needs revisiting, not a number bump")
    sys.exit(1)
