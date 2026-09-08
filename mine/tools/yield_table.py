#!/usr/bin/env python3
"""Compute the run's yield table from what is actually on disk.

Every number in mine/REPORT.md that this can compute, it computes, so the report cannot
drift from the artefacts. Run: python3 mine/tools/yield_table.py
"""
import json, os, re, collections, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

def jsonl(p):
    out = []
    if not os.path.exists(p):
        return out
    for line in open(p):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out

raw = {}
for fn in sorted(os.listdir("mine/corpus/raw")):
    if fn.endswith(".jsonl"):
        raw[fn] = len(jsonl("mine/corpus/raw/" + fn))

problems = jsonl("mine/corpus/problems.jsonl")
by_class = collections.Counter(r.get("class") for r in problems)
eligible = [r for r in problems if r.get("attack_eligible")]

# attacked = every directory under mine/attacks/ that carries a log
attacked = []
for d in sorted(os.listdir("mine/attacks")):
    p = os.path.join("mine/attacks", d)
    if os.path.isdir(p) and os.path.exists(os.path.join(p, "log.md")):
        attacked.append(d)
wave_dirs = [d for d in attacked if d.startswith("wave")]
problem_dirs = [d for d in attacked if not d.startswith("wave") and not d.startswith("t2") and not d.startswith("t3")]

# the ten open WOWII conjectures are attacked collectively by the wave directories
WOWII_OPEN = ["wow2-19", "wow2-40", "wow2-61", "wow2-100", "wow2-133",
              "wow2-141", "wow2-160", "wow2-198a", "wow2-291", "wow2-314"]

checkers = sorted(f for f in os.listdir("mine/verify/checkers") if f.endswith(".py"))
freeze = open("mine/verify/FREEZE.sha256").read().strip().split("\n") if os.path.exists("mine/verify/FREEZE.sha256") else []

# negative.jsonl is the merged file; the per-agent negative-*.jsonl files are its inputs,
# so counting both would double-count.
neg = jsonl("mine/memory/negative.jsonl")

results = [d for d in sorted(os.listdir("mine/results"))
           if os.path.isdir(os.path.join("mine/results", d))]

# attacked problems, broken down by the class the triage assigned them
by_id = {r.get("id"): r for r in problems}
attacked_ids = sorted(set(problem_dirs) | set(WOWII_OPEN))
attack_classes = collections.Counter()
unmatched = []
for a in attacked_ids:
    r = by_id.get(a)
    if r:
        attack_classes[r.get("class")] += 1
    else:
        unmatched.append(a)

report = {
    "corpus": {
        "raw_per_cluster": raw,
        "raw_total": sum(raw.values()),
        "after_dedupe": len(problems),
        "by_class": dict(by_class),
        "attack_eligible": len(eligible),
        "excluded": len(problems) - len(eligible),
    },
    "verifier": {
        "files_frozen": len(freeze),
        "checkers": len(checkers),
        "checker_names": checkers,
    },
    "attack": {
        "problems_attacked": sorted(set(problem_dirs) | set(WOWII_OPEN)),
        "problems_attacked_count": len(set(problem_dirs) | set(WOWII_OPEN)),
        "wave_dirs": wave_dirs,
        "negative_memory_entries": len(neg),
        "attacked_by_class": dict(attack_classes),
        "attacked_not_matched_to_a_corpus_row": unmatched,
    },
    "results_shipped": results,
}
print(json.dumps(report, indent=2))
