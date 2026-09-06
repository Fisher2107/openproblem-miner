#!/usr/bin/env python3
"""
H1 harvest: Erdos open problems.

Joins two cloned sources:
  A) google-deepmind/formal-conjectures @ 8323e878b83fcd7f4a448256069352a265460d75
     FormalConjectures/ErdosProblems/<n>.lean  -- Lean statements + NL docstrings
  B) teorth/erdosproblems @ 7688a2b0fc70a4f68a897a7a6da7788681003888
     data/problems.yaml -- per-problem metadata (status, prize, tags, oeis, comments)

Emits one JSON object per line to mine/corpus/raw/h1_erdos.jsonl for every
`@[category research open]` theorem whose problem is still open per (B).

Run:  python3 mine/cache/h1_extract.py      (from repo root)
"""
import json, os, re, sys, unicodedata
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # mine/
REPO = os.path.dirname(ROOT)
FC_COMMIT = "8323e878"
EP_COMMIT = "7688a2b0"
LEAN_DIR = os.path.join(ROOT, "cache", "formal-conjectures",
                        "FormalConjectures", "ErdosProblems")
YAML_PATH = os.path.join(ROOT, "cache", "erdosproblems", "data", "problems.yaml")
OUT_PATH = os.path.join(ROOT, "corpus", "raw", "h1_erdos.jsonl")

# erdosproblems.com informal states. Per that repo's README:
#   falsifiable = open, but disprovable by a finite computation if false
#   verifiable  = open, but provable by a finite computation if true
#   decidable   = open, but reduced to a finite computation
#   not provable / not disprovable = one direction ruled out, other still open
OPEN_STATES = {"open", "falsifiable", "verifiable", "decidable",
               "not provable", "not disprovable"}
SETTLED_STATES = {"proved", "disproved", "solved", "independent"}
FINITE_COMPUTATION_STATES = {"falsifiable", "verifiable", "decidable"}

# ---------------------------------------------------------------- YAML source
def load_yaml():
    try:
        import yaml
    except ImportError:
        sys.exit("pyyaml required: pip install pyyaml")
    with open(YAML_PATH) as f:
        data = yaml.safe_load(f)
    return {p["number"]: p for p in data}

# ------------------------------------------------------------ Lean file parse
DECL_RE = re.compile(r"^\s*(private\s+)?(noncomputable\s+)?(theorem|lemma)\b")
DEF_RE = re.compile(r"^\s*(private\s+)?(noncomputable\s*\n?)?\s*(def|abbrev)\s+([A-Za-z_][\w'.]*)")
# a line that ends a declaration signature and starts the proof
TERM_RE = re.compile(r":=\s*(by)?\s*(sorry)?\s*$")
URL_RE = re.compile(r"https://www\.erdosproblems\.com/(\d+)")

def docstring_above(lines, idx):
    """Walk up from line idx (the attribute line), skipping blanks and `--`
    comment lines, and return (text, start_idx) of the `/-- ... -/` block, or
    (None, None)."""
    p = idx - 1
    while p >= 0 and (lines[p].strip() == "" or lines[p].lstrip().startswith("--")):
        p -= 1
    if p < 0 or not lines[p].rstrip().endswith("-/"):
        return None, None
    end = p
    while p >= 0 and "/--" not in lines[p]:
        p -= 1
    if p < 0:
        return None, None
    block = "\n".join(lines[p:end + 1])
    block = block[block.index("/--") + 3:]
    block = block[:block.rindex("-/")]
    return block.strip(), p

def formalisation_notes(lines, idx):
    """`--` comment lines sitting between the docstring and the attribute."""
    out, p = [], idx - 1
    while p >= 0 and (lines[p].strip() == "" or lines[p].lstrip().startswith("--")):
        if lines[p].lstrip().startswith("--"):
            out.append(lines[p].lstrip()[2:].strip())
        p -= 1
    return " ".join(reversed(out)).strip()

def balanced(s):
    pairs = {")": "(", "]": "[", "}": "{", "⟩": "⟨"}
    stack = []
    for ch in s:
        if ch in "([{⟨":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack

def signature(lines, start):
    """Return (text, end_idx) for the declaration signature beginning at
    line `start`, cutting off the `:= by sorry` proof body."""
    for end in range(start, min(start + 60, len(lines))):
        line = lines[end]
        m = TERM_RE.search(line.rstrip())
        if not m:
            continue
        cut = line.rstrip()[:m.start()].rstrip()
        body = lines[start:end] + ([cut] if cut else [])
        text = "\n".join(body).rstrip()
        if balanced(text) and text:
            return text, end
    # fallback: no terminator found within window
    text = "\n".join(lines[start:min(start + 12, len(lines))]).rstrip()
    return text, min(start + 12, len(lines)) - 1

def parse_lean(path):
    """Return dict with url, references, open_decls, solved_docs, defs."""
    lines = open(path, encoding="utf-8").read().split("\n")
    src = "\n".join(lines)

    m = URL_RE.search(src)
    url = m.group(0) if m else None

    # module header references block
    refs = []
    hm = re.search(r"/-!(.*?)-/", src, re.S)
    if hm:
        for ln in hm.group(1).split("\n"):
            ln = ln.strip()
            if ln.startswith("- [") and "erdosproblems.com" not in ln:
                refs.append(ln[2:].strip())
            elif ln.startswith("*Reference") and "erdosproblems.com" not in ln:
                refs.append(re.sub(r"^\*References?:\*\s*", "", ln))
        # continuation lines of a wrapped reference
        raw = [l.rstrip() for l in hm.group(1).split("\n")]
        merged, cur = [], None
        for ln in raw:
            s = ln.strip()
            if s.startswith("- ["):
                if cur: merged.append(cur)
                cur = s[2:].strip()
            elif cur is not None and s and not s.startswith("#") and not s.startswith("*"):
                cur += " " + s
            elif cur:
                merged.append(cur); cur = None
        if cur: merged.append(cur)
        if merged:
            refs = [r for r in merged if "erdosproblems.com" not in r]

    # definitions with docstrings (for making statements self-contained)
    defs = OrderedDict()
    for i, ln in enumerate(lines):
        dm = re.match(r"^\s*(?:(?:private|protected|noncomputable|partial|unsafe)\s+)*"
                      r"(?:def|abbrev)\s+([A-Za-z_][\w'!]*)", ln)
        if not dm:
            continue
        # `noncomputable` may sit on its own line above
        j = i
        doc, _ = docstring_above(lines, j)
        if doc is None and j > 0 and lines[j-1].strip() == "noncomputable":
            doc, _ = docstring_above(lines, j - 1)
        if doc:
            defs[dm.group(1)] = doc

    open_decls, solved_docs = [], []
    for i, ln in enumerate(lines):
        if not ln.lstrip().startswith("@[category "):
            continue
        attr = ln.strip()
        cat_open = "category research open" in attr
        cat_solved = "category research solved" in attr
        if not (cat_open or cat_solved):
            continue
        j = i + 1
        while j < len(lines) and not DECL_RE.match(lines[j]):
            if j > i + 6:
                break
            j += 1
        if j >= len(lines) or not DECL_RE.match(lines[j]):
            continue
        doc, _ = docstring_above(lines, i)
        if cat_solved:
            if doc:
                solved_docs.append(doc)
            continue
        sig, _end = signature(lines, j)
        name_m = re.match(r"^\s*(?:private\s+)?(?:noncomputable\s+)?(?:theorem|lemma)\s+([A-Za-z_][\w'.!]*)", lines[j])
        open_decls.append({
            "attr": attr,
            "name": name_m.group(1) if name_m else None,
            "line": i + 1,             # 1-based line of the attribute
            "doc": doc,
            "fnote": formalisation_notes(lines, i),
            "sig": sig,
        })
    return {"url": url, "refs": refs, "open": open_decls,
            "solved_docs": solved_docs, "defs": defs}

# ------------------------------------------------------- LaTeX -> readable NL
GREEK = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\varepsilon": "ε", r"\zeta": "ζ", r"\eta": "η",
    r"\theta": "θ", r"\iota": "ι", r"\kappa": "κ", r"\lambda": "λ",
    r"\mu": "μ", r"\nu": "ν", r"\xi": "ξ", r"\pi": "π", r"\rho": "ρ",
    r"\sigma": "σ", r"\tau": "τ", r"\upsilon": "υ", r"\phi": "φ",
    r"\varphi": "φ", r"\chi": "χ", r"\psi": "ψ", r"\omega": "ω",
    r"\Gamma": "Γ", r"\Delta": "Δ", r"\Theta": "Θ", r"\Lambda": "Λ",
    r"\Xi": "Ξ", r"\Pi": "Π", r"\Sigma": "Σ", r"\Phi": "Φ",
    r"\Psi": "Ψ", r"\Omega": "Ω", r"\aleph": "ℵ",
}
SYMS = {
    r"\leqslant": "≤", r"\geqslant": "≥", r"\leq": "≤", r"\geq": "≥",
    r"\le": "≤", r"\ge": "≥", r"\neq": "≠", r"\ne": "≠", r"\equiv": "≡",
    r"\sim": "~", r"\approx": "≈", r"\ll": "≪", r"\gg": "≫",
    r"\in": "∈", r"\notin": "∉", r"\subseteq": "⊆", r"\subset": "⊂",
    r"\supseteq": "⊇", r"\cap": "∩", r"\cup": "∪", r"\emptyset": "∅",
    r"\setminus": "\\", r"\mid": "|", r"\nmid": "∤", r"\times": "×",
    r"\cdot": "·", r"\pm": "±", r"\infty": "∞", r"\to": "→",
    r"\rightarrow": "→", r"\mapsto": "↦", r"\implies": "⟹",
    r"\iff": "⟺", r"\forall": "∀", r"\exists": "∃", r"\lor": "∨",
    r"\land": "∧", r"\neg": "¬", r"\sum": "Σ", r"\prod": "Π",
    r"\int": "∫", r"\liminf": "liminf", r"\limsup": "limsup",
    r"\lim": "lim", r"\log": "log", r"\exp": "exp", r"\min": "min",
    r"\max": "max", r"\inf": "inf", r"\sup": "sup", r"\gcd": "gcd",
    r"\bmod": "mod", r"\dots": "...", r"\ldots": "...", r"\cdots": "...",
    r"\dotsb": "...", r"\ldotsb": "...", r"\lfloor": "floor(",
    r"\rfloor": ")", r"\lceil": "ceil(", r"\rceil": ")",
    r"\langle": "<", r"\rangle": ">", r"\colon": ":",
    r"\lvert": "|", r"\rvert": "|", r"\lVert": "||", r"\rVert": "||",
    r"\|": "||", r"\ast": "*", r"\asymp": "≍", r"\sub": "⊂",
    r"\ell": "ℓ", r"\oplus": "⊕", r"\otimes": "⊗", r"\cos": "cos",
    r"\sin": "sin", r"\tan": "tan", r"\mod": "mod", r"\choose": " choose ",
    r"\bigl": "", r"\bigr": "", r"\Bigl": "", r"\Bigr": "",
    r"\big": "", r"\Big": "", r"\sb": "_", r"\sp": "^",
    r"\#": "#", r"\varnothing": "∅", r"\ln": "ln", r"\lg": "lg",
    r"\mathbb{R}": "ℝ", r"\mathbb{N}": "ℕ", r"\mathbb{Z}": "ℤ",
    r"\mathbb{Q}": "ℚ", r"\mathbb{C}": "ℂ", r"\mathbb{F}": "F",
    r"\R": "ℝ", r"\N": "ℕ", r"\Z": "ℤ", r"\Q": "ℚ",
    r"\left": "", r"\right": "", r"\!": "", r"\,": " ", r"\;": " ",
    r"\quad": " ", r"\qquad": " ", r"\ ": " ", r"\displaystyle": "",
    r"\nonumber": "", r"\notag": "", r"\limits": "",
}

def _brace_arg(s, i):
    """s[i] == '{'; return (content, index just past matching '}')."""
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)

def _two_arg(s, macro, fmt):
    out, i = [], 0
    while True:
        k = s.find(macro, i)
        if k < 0:
            out.append(s[i:]); break
        out.append(s[i:k])
        j = k + len(macro)
        while j < len(s) and s[j] == " ":
            j += 1
        if j < len(s) and s[j] == "{":
            a, j = _brace_arg(s, j)
            while j < len(s) and s[j] == " ":
                j += 1
            if j < len(s) and s[j] == "{":
                b, j = _brace_arg(s, j)
                out.append(fmt.format(_delatex(a), _delatex(b)))
                i = j
                continue
        out.append(macro)
        i = k + len(macro)
    return "".join(out)

def _one_arg(s, macro, fmt):
    out, i = [], 0
    while True:
        k = s.find(macro, i)
        if k < 0:
            out.append(s[i:]); break
        out.append(s[i:k])
        j = k + len(macro)
        while j < len(s) and s[j] == " ":
            j += 1
        if j < len(s) and s[j] == "{":
            a, j = _brace_arg(s, j)
            out.append(fmt.format(_delatex(a)))
            i = j
            continue
        out.append(macro)
        i = k + len(macro)
    return "".join(out)

def _delatex(s):
    s = _two_arg(s, r"\frac", "({0})/({1})")
    s = _two_arg(s, r"\dfrac", "({0})/({1})")
    s = _two_arg(s, r"\tfrac", "({0})/({1})")
    s = _two_arg(s, r"\binom", "C({0},{1})")
    s = _one_arg(s, r"\sqrt", "sqrt({0})")
    s = _one_arg(s, r"\pmod", "(mod {0})")
    s = _one_arg(s, r"\text", "{0}")
    s = _one_arg(s, r"\textrm", "{0}")
    s = _one_arg(s, r"\mathrm", "{0}")
    s = _one_arg(s, r"\operatorname", "{0}")
    s = _one_arg(s, r"\mathcal", "{0}")
    s = _one_arg(s, r"\mathbf", "{0}")
    s = _one_arg(s, r"\overline", "overline({0})")
    s = _one_arg(s, r"\floor", "floor({0})")
    s = _one_arg(s, r"\mathfrak", "{0}")
    s = _one_arg(s, r"\substack", "{0}")
    s = _one_arg(s, r"\hat", "{0}^")
    s = _one_arg(s, r"\tilde", "{0}~")
    for k in sorted(list(SYMS) + list(GREEK), key=len, reverse=True):
        s = s.replace(k, SYMS.get(k, GREEK.get(k)))
    s = s.replace(r"\{", "{").replace(r"\}", "}").replace(r"\%", "%")
    s = s.replace(r"\H{o}", "ő").replace(r"\H o", "ő")
    for a, b in ((r"\'{e}", "é"), (r"\'{o}", "ó"), (r"\'{a}", "á"),
                 (r'\"{o}', "ö"), (r'\"{u}', "ü"), (r'\"{a}', "ä"),
                 (r"\'e", "é"), (r"\'o", "ó"), (r"\'a", "á"), (r"\'u", "ú"),
                 (r'\"o', "ö"), (r'\"u', "ü"), (r'\"a', "ä"), (r"\~n", "ñ")):
        s = s.replace(a, b)
    s = s.replace("\\not≡", "≢").replace("\\not∈", "∉").replace("\\not|", "∤")
    s = re.sub(r"\\frac\s*\{?(\w)\}?\s*\{?(\w)\}?", r"(\1)/(\2)", s)
    s = re.sub(r"\\sqrt\s*\{?(\w+)\}?", r"sqrt(\1)", s)
    s = s.replace("\\not", "not ")
    return s

def clean_nl(doc):
    """Docstring -> readable, self-contained-ish natural language."""
    s = doc
    s = re.sub(r"\$\$(.+?)\$\$", lambda m: " " + m.group(1).strip() + " ", s, flags=re.S)
    s = s.replace("\\$", "\x00USD\x00")
    s = s.replace("$", "")
    s = s.replace("\x00USD\x00", "$")
    s = _delatex(s)
    s = re.sub(r"\s*\n\s*\n\s*", "\n\n", s)
    s = re.sub(r"[ \t]*\n[ \t]*", " ", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\s+([,.;:?])", r"\1", s)
    return s.strip()

# ------------------------------------------------------------- classification
GRAPHY = ("SimpleGraph", "chromaticNumber", "chromatic", "cliqueNum",
          "IsClique", "Subgraph", "Coloring", "hypergraph")

def top_level_exists(sig):
    """Does the conclusion lead with an existential construction?"""
    body = sig.split(":", 1)[-1]
    body = body.replace("answer(sorry) ↔", "").replace("answer(sorry)↔", "")
    body = body.strip()
    return body.startswith("∃") or bool(re.match(r"^\(?\s*∃", body))

def classify_quantifier(sig, nl):
    s = sig
    if any(g in s for g in GRAPHY):
        if re.search(r"∃\s*\(?\s*\w*\s*:?\s*[^,]*SimpleGraph", s):
            return "exists-construction"
        return "forall-graphs"
    if top_level_exists(s):
        return "exists-construction"
    if re.search(r"=[oO]\[|IsLittleO|IsBigO|Tendsto|limsup|liminf|HasDensity|"
                 r"IsLeast|IsGreatest|sInf|sSup|≤|<|≥|>", s):
        return "bound"
    if re.search(r"ℕ|ℤ|Nat\.|Prime|Set\.Infinite|Finite|∀ n|∀ᶠ", s):
        return "forall-integers"
    return "other"

def classify_witness(sig, informal_state, qshape):
    if informal_state in FINITE_COMPUTATION_STATES:
        return "finite-object"
    if qshape == "exists-construction":
        return "parametric-family"
    # asks for a specific constant / function value with no outer binders
    head = sig.split("\n")[0]
    binderless = not re.search(r"\(\w+\s*:\s*(ℕ|ℤ|ℝ)\)", head)
    if "answer(sorry)" in sig and binderless and "answer(sorry) ↔" not in sig \
       and not re.search(r"answer\(sorry\)\s*↔", sig):
        return "numeric-bound"
    return "none"

def classify_cost(wtype, sig):
    if wtype == "none":
        return "unknown"
    if wtype == "finite-object":
        # verifying a candidate needs a search over subsets / configurations
        if any(g in sig for g in GRAPHY):
            return "exponential"
        if re.search(r"IsLeast|IsGreatest|sInf|sSup|Set\.ncard|Finset\.card|"
                     r"ℝ²|Collinear|Cospherical|Convex|∀", sig):
            return "exponential"
        if "∃" in sig:
            return "poly"
        return "unknown"
    if wtype == "parametric-family":
        return "unknown"
    return "unknown"

# --------------------------------------------------------------------- driver
def main():
    ymap = load_yaml()
    files = sorted((f for f in os.listdir(LEAN_DIR) if f.endswith(".lean")),
                   key=lambda f: int(f[:-5]) if f[:-5].isdigit() else 10**9)
    entries = []
    stats = Counter()
    disagreements = []      # (number, yaml informal state, lean decl names)
    missing_in_yaml = []
    skipped_no_nl = []
    seen_names = set()

    for fn in files:
        if not fn[:-5].isdigit():
            continue
        num = fn[:-5]
        path = os.path.join(LEAN_DIR, fn)
        parsed = parse_lean(path)
        if not parsed["open"]:
            continue
        stats["files_with_open_decls"] += 1
        stats["open_decls_seen"] += len(parsed["open"])

        y = ymap.get(num)
        if y is None:
            missing_in_yaml.append((num, [d["name"] for d in parsed["open"]]))
            informal = None
        else:
            informal = y["informal_status"]["state"]
            if informal in SETTLED_STATES:
                disagreements.append((num, informal, y["status"]["state"],
                                      [d["name"] for d in parsed["open"]]))
                stats["skipped_settled_decls"] += len(parsed["open"])
                continue
            if informal not in OPEN_STATES:
                disagreements.append((num, informal, y["status"]["state"],
                                      [d["name"] for d in parsed["open"]]))
                stats["skipped_unknown_state_decls"] += len(parsed["open"])
                continue

        # keep only decls with a usable NL statement
        usable = []
        for d in parsed["open"]:
            if d["name"] and d["name"] in seen_names:
                stats["dedup_dropped"] += 1
                continue
            if not d["doc"]:
                skipped_no_nl.append((num, d["name"], "no docstring"))
                stats["skipped_no_nl"] += 1
                continue
            nl = clean_nl(d["doc"])
            # self-containment: append docstrings of file-level defs the Lean
            # statement actually mentions, BEFORE judging whether the entry is
            # usable (several docstrings are terse because the def carries the
            # substance).
            extra = []
            for dname, ddoc in parsed["defs"].items():
                if re.search(r"\b" + re.escape(dname) + r"\b", d["sig"]):
                    extra.append("%s: %s" % (dname, clean_nl(ddoc)))
            if extra:
                nl += "  [Definitions used in the formal statement — " + \
                      " ".join(extra) + "]"
            if len(nl) < 30:
                skipped_no_nl.append((num, d["name"], "statement too terse: " + nl))
                stats["skipped_no_nl"] += 1
                continue
            d["nl"] = nl
            if d["name"]:
                seen_names.add(d["name"])
            usable.append(d)
        if not usable:
            continue

        multi = len(usable) > 1
        for k, d in enumerate(usable):
            suffix = "-" + chr(ord("a") + k) if multi else ""
            pid = "erdos-%04d%s" % (int(num), suffix)

            nl = d["nl"]

            qshape = classify_quantifier(d["sig"], nl)
            wtype = classify_witness(d["sig"], informal, qshape)
            cost = classify_cost(wtype, d["sig"])

            known = " ".join(clean_nl(x) for x in parsed["solved_docs"])
            prior = " ".join(parsed["refs"])

            notes = []
            if y:
                if y.get("tags"):
                    notes.append("tags: " + ", ".join(y["tags"]))
                if y.get("oeis"):
                    notes.append("oeis: " + ", ".join(y["oeis"]))
                if y.get("comments"):
                    notes.append("erdosproblems comment: " + y["comments"])
                notes.append("erdosproblems informal_status: " + informal)
                if y["status"]["state"] != informal:
                    notes.append("erdosproblems derived status: " + y["status"]["state"])
                if informal in FINITE_COMPUTATION_STATES:
                    notes.append("NOTE: erdosproblems classifies this as '%s' — open, "
                                 "but settleable by a finite computation." % informal)
            else:
                notes.append("problem number absent from teorth/erdosproblems "
                             "data/problems.yaml @ %s; open status taken from the "
                             "formal-conjectures 'research open' tag alone" % EP_COMMIT)
            if d["fnote"]:
                notes.append("formalisation note: " + d["fnote"])
            if multi:
                notes.append("Lean decl: " + (d["name"] or "?"))
            notes.append("quantifier_shape/witness_type/witness_check_cost are "
                         "heuristic (see mine/logs/harvest-h1.md)")

            entries.append(OrderedDict([
                ("id", pid),
                ("source", "erdosproblems.com (via formal-conjectures)"),
                ("url", parsed["url"] or "https://www.erdosproblems.com/" + num),
                ("provenance", "clone:google-deepmind/formal-conjectures@%s:"
                               "FormalConjectures/ErdosProblems/%s#L%d"
                               % (FC_COMMIT, fn, d["line"])),
                ("statement_nl", nl),
                ("statement_formal", d["attr"] + "\n" + d["sig"]),
                ("quantifier_shape", qshape),
                ("witness_type", wtype),
                ("witness_check_cost", cost),
                ("known_cases", known),
                ("current_bounds", {"lower": None, "upper": None}),
                ("prior_attempts", prior),
                ("prize", (y.get("prize") if y and y.get("prize") not in (None, "no")
                           else None)),
                ("class", None),
                ("tractability", None),
                ("notes", " | ".join(notes)),
            ]))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    # ---- report to stdout (also pasted into mine/logs/harvest-h1.md)
    print("entries written:", len(entries), "->", OUT_PATH)
    for k, v in sorted(stats.items()):
        print("  %-28s %s" % (k, v))
    print("\nwitness_type:", dict(Counter(e["witness_type"] for e in entries)))
    print("quantifier_shape:", dict(Counter(e["quantifier_shape"] for e in entries)))
    print("witness_check_cost:", dict(Counter(e["witness_check_cost"] for e in entries)))
    print("\nSTATUS DISAGREEMENTS (Lean 'research open' vs YAML settled): %d files"
          % len(disagreements))
    for num, inf, der, names in disagreements:
        print("  erdos-%04d  yaml=%s (derived: %s)  lean=%s" %
              (int(num), inf, der, ",".join(n or "?" for n in names)))
    print("\nIN LEAN BUT NOT IN YAML: %d" % len(missing_in_yaml))
    for num, names in missing_in_yaml:
        print("  %s  %s" % (num, ",".join(n or "?" for n in names)))
    print("\nSKIPPED FOR UNUSABLE NL: %d" % len(skipped_no_nl))
    for num, name, why in skipped_no_nl:
        print("  %s %s  (%s)" % (num, name, why[:90]))

if __name__ == "__main__":
    main()
