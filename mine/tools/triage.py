#!/usr/bin/env python3
"""Triage the harvested corpus into classes A/B/C/D with a tractability score.

Rubric is deliberately explicit and auditable: every score is a sum of named
contributions, and every entry carries the list of contributions that produced it,
so the calibration section of the report can ask which signals were wrong.

Usage:
  python3 mine/tools/triage.py            # writes mine/corpus/problems.jsonl + triage.json
"""
import json, re, os, sys, hashlib, collections

RAW = "mine/corpus/raw"
OUT = "mine/corpus/problems.jsonl"
SUMMARY = "mine/corpus/triage.json"

# ---------------------------------------------------------------- normalisation
def norm_statement(s):
    """Semantic-ish normalisation for dedupe: strip LaTeX noise, case, punctuation,
    and the invariant *names* people vary on, keeping the mathematical skeleton."""
    s = (s or "").lower()
    s = re.sub(r"\$+", " ", s)
    s = re.sub(r"\\[a-z]+", " ", s)
    s = re.sub(r"[^a-z0-9<>=+*/^(){}\[\]., -]", " ", s)
    s = re.sub(r"\b(the|a|an|of|for|every|all|any|is|are|be|that|which|with|and|or|if|then|let|such|there|exists?)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def dedupe_key(r):
    return hashlib.sha1(norm_statement(r.get("statement_nl", ""))[:400].encode()).hexdigest()

# ---------------------------------------------------------------- classification
def classify(r):
    """A finite-witness refutable | B parametric-construction | C bound-improvable | D proof-only."""
    wt = (r.get("witness_type") or "none").strip()
    qs = (r.get("quantifier_shape") or "other").strip()
    cb = r.get("current_bounds") or {}
    has_gap = cb.get("lower") is not None and cb.get("upper") is not None and cb.get("lower") != cb.get("upper")
    if wt == "finite-object":
        return "A"
    if wt == "numeric-bound" or has_gap or qs == "bound":
        return "C"
    if wt == "parametric-family":
        return "B"
    return "D"

# ---------------------------------------------------------------- tractability
SOLVED = re.compile(r"\bREFUTED\b|research solved|status: reported SOLVED|already (proved|disproved|solved)|believed a theorem|almost certainly NOT open", re.I)
# A witness that is an integer/tuple of integers in an unbounded arithmetic search space is
# not something this run can enumerate: the published searches already reach 10^9+ and our
# 4 cores add nothing. Distinct from a combinatorial class enumerable at small order.
ARITH_UNBOUNDED = re.compile(r"\b(integers?|n!|prime|divisor|powerful|squarefree|perfect number|amicable|digits?|decimal|base 10|fibonacci|factorial|diophantine|rational (number|point)s?)\b", re.I)
COMBINATORIAL = re.compile(r"\b(graph|graphs|digraph|hypergraph|colou?ring|matrix|design|latin square|permutation|lattice|polytope|code|configuration|tournament|poset)\b", re.I)

NEG_PRIOR = re.compile(r"exhaustive|brute[- ]force|computer search|sat solver|verified up to|checked for all|geng|extensive computation|machine search", re.I)
ENUMERABLE = re.compile(r"\b(graph|graphs|tree|trees|digraph|matrix|matrices|colou?ring|set of integers|subset|permutation|design|code|lattice|polygon|configuration)\b", re.I)
ASYMPTOTIC = re.compile(r"sufficiently large|infinitely many|as n\b|asymptotic|for all large|limit|\blim\b|density|o\(|O\(|\bepsilon\b", re.I)

def tractability(r, cls):
    """0-10. Returns (score, [contributions]). Every term is named so the report can
    audit which signals were predictive."""
    c = []
    text = " ".join(str(r.get(k) or "") for k in ("statement_nl", "known_cases", "prior_attempts", "notes"))
    # base by class: A is refutable by one object, C has a gradient, B needs a CAS, D has no witness
    base = {"A": 4.0, "C": 3.0, "B": 1.5, "D": 0.0}[cls]
    c.append(("class-base:" + cls, base))
    s = base

    # a checker that is easy to write correctly is worth a lot; exponential checks are not fatal
    wcc = (r.get("witness_check_cost") or "unknown").strip()
    d = {"trivial": 1.5, "poly": 1.0, "exponential": -0.5, "unknown": -0.5}.get(wcc, -0.5)
    c.append(("check-cost:" + wcc, d)); s += d

    # already formalized in Lean = the T3 cost is partly pre-paid
    if r.get("statement_formal"):
        c.append(("has-lean-statement", 1.5)); s += 1.5

    # quantified over an enumerable structured class => brute force over first sizes is meaningful
    if ENUMERABLE.search(r.get("statement_nl") or ""):
        c.append(("enumerable-class", 1.0)); s += 1.0

    # machine-generated conjecture over graphs: structurally the easiest ore in the mine
    src = (r.get("source") or "") + (r.get("id") or "")
    if re.search(r"graffiti|wowii|wow2|WrittenOnTheWall|txgraffiti|autographix", src, re.I):
        c.append(("machine-generated-graph-conjecture", 1.5)); s += 1.5

    # asymptotic statements have no finite witness however they were tagged
    if ASYMPTOTIC.search(r.get("statement_nl") or ""):
        c.append(("asymptotic-language", -1.5)); s -= 1.5

    # heavy prior machine search is a NEGATIVE signal: the cheap seam is already mined
    if NEG_PRIOR.search(text):
        c.append(("prior-machine-search", -2.0)); s -= 2.0

    # a big prize means decades of attention: the mispricing this run wants is the opposite
    prize = r.get("prize")
    if prize and str(prize).strip() not in ("", "no", "None", "null"):
        c.append(("prize-attention", -1.0)); s -= 1.0

    # unverified provenance may not be attacked at all (policy), so it is not a target
    if str(r.get("provenance", "")).startswith("model-knowledge-unverified"):
        c.append(("unverified-provenance-not-attackable", -3.0)); s -= 3.0

    # an unbounded arithmetic witness space is out of reach here; published searches are
    # already many orders of magnitude past what 4 cores add in an hour
    nl_only = r.get("statement_nl") or ""
    if cls == "A" and ARITH_UNBOUNDED.search(nl_only) and not COMBINATORIAL.search(nl_only):
        c.append(("unbounded-arithmetic-witness", -3.0)); s -= 3.0

    # very long statements are usually not self-contained enough to encode correctly
    nl = r.get("statement_nl") or ""
    if len(nl) > 900:
        c.append(("statement-too-long", -1.0)); s -= 1.0
    elif len(nl) < 320:
        c.append(("statement-compact", 0.5)); s += 0.5

    if SOLVED.search(text):
        c.append(("already-solved-or-refuted:not-a-target", -99.0))
        return 0.0, c

    s = max(0.0, min(10.0, s))
    return round(s, 2), c

# ---------------------------------------------------------------- main
def main():
    rows, per_file = [], collections.Counter()
    for fn in sorted(os.listdir(RAW)):
        if not fn.endswith(".jsonl"):
            continue
        for line in open(os.path.join(RAW, fn)):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            r["_cluster"] = fn.split("_")[0]
            rows.append(r); per_file[fn] += 1

    # dedupe on statement semantics, recording merged aliases
    by_key = {}
    for r in rows:
        k = dedupe_key(r)
        if k in by_key:
            by_key[k].setdefault("aliases", []).append({"id": r.get("id"), "source": r.get("source"), "url": r.get("url")})
        else:
            r["aliases"] = []
            by_key[k] = r
    merged = list(by_key.values())

    for r in merged:
        cls = classify(r)
        sc, contribs = tractability(r, cls)
        r["class"] = cls
        r["tractability"] = sc
        r["tractability_terms"] = [{"signal": a, "delta": b} for a, b in contribs]
        blocked = [t for t, _ in contribs if t.startswith("already-solved") or t.startswith("unverified-provenance")]
        r["attack_eligible"] = not blocked
        r["pool_note"] = ("excluded: " + ", ".join(blocked)) if blocked else ""

    merged.sort(key=lambda r: (-r["tractability"], r.get("id") or ""))
    with open(OUT, "w") as f:
        for r in merged:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    summary = {
        "raw_entries": len(rows),
        "per_cluster_raw": dict(per_file),
        "after_dedupe": len(merged),
        "duplicates_merged": len(rows) - len(merged),
        "by_class": dict(collections.Counter(r["class"] for r in merged)),
        "by_cluster": dict(collections.Counter(r["_cluster"] for r in merged)),
        "tractability_hist": dict(collections.Counter(int(r["tractability"]) for r in merged)),
        "attack_eligible": sum(1 for r in merged if r.get("attack_eligible")),
        "excluded_solved_or_unverified": sum(1 for r in merged if not r.get("attack_eligible")),
        "top40": [{"id": r["id"], "class": r["class"], "t": r["tractability"], "src": r.get("source"),
                   "nl": (r.get("statement_nl") or "")[:120]}
                  for r in merged if r.get("attack_eligible")][:40],
    }
    json.dump(summary, open(SUMMARY, "w"), indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "top40"}, indent=2))

if __name__ == "__main__":
    main()
