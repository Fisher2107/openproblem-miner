#!/usr/bin/env python3
"""H2 (formal corpus) extractor.

Emits one JSON object per line to mine/corpus/raw/h2_formal.jsonl following
mine/corpus/SCHEMA.md.

Sources:
  1. mine/cache/formal-conjectures @ 8323e878b83fcd7f4a448256069352a265460d75
     every `@[category research open ...]` declaration outside ErdosProblems/
     and WrittenOnTheWallII/.
  2. mine/cache/mathlib4 @ (commit recorded below) -- strict sweep for
     open-problem markers.

Run:  python3 mine/cache/h2_extract.py
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FC = os.path.join(ROOT, "mine", "cache", "formal-conjectures")
FC_COMMIT = "8323e878"
FC_BASE = os.path.join(FC, "FormalConjectures")
ML = os.path.join(ROOT, "mine", "cache", "mathlib4")
ML_COMMIT = "80cbd049"
OUT = os.path.join(ROOT, "mine", "corpus", "raw", "h2_formal.jsonl")

EXCLUDE_DIRS = {"ErdosProblems", "WrittenOnTheWallII"}

STATS = {"files_scanned": 0, "open_attrs": 0, "emitted": 0, "dropped_no_doc": 0,
         "dropped_dup": 0}


# ---------------------------------------------------------------- lean parsing

def match_bracket(text, i):
    """text[i] == '['; return index just past the matching ']'."""
    depth = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            i += 1
            while i < n and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def clean_doc(s):
    """Normalise a Lean docstring body to flowing text."""
    s = s.strip()
    lines = [ln.strip() for ln in s.split("\n")]
    out = []
    for ln in lines:
        if not ln:
            out.append("")
            continue
        ln = re.sub(r"^[*+-]\s+", "- ", ln)
        out.append(ln)
    txt = "\n".join(out)
    # join soft-wrapped lines inside paragraphs
    txt = re.sub(r"(?<![\n])\n(?![\n\-])", " ", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    txt = re.sub(r"[ \t]{2,}", " ", txt)
    return txt.strip()


def preceding_docstring(text, attr_start):
    """Docstring block immediately before attr_start (only whitespace / `--` between)."""
    head = text[:attr_start]
    m = None
    for m2 in re.finditer(r"/--(.*?)-/", head, re.S):
        m = m2
    if not m:
        return None
    between = head[m.end():]
    for ln in between.split("\n"):
        t = ln.strip()
        if t and not t.startswith("--"):
            return None
    return clean_doc(m.group(1))


def signature_after(text, pos):
    """Lean declaration signature starting at pos, up to `:= by` / `:= sorry` / `:=`."""
    m = re.compile(r"\b(theorem|lemma|def|abbrev|instance|example)\b").search(text, pos)
    if not m or m.start() - pos > 200:
        return None
    start = m.start()
    # find the terminator
    end = None
    for term in (r":=\s*by\b", r":=\s*sorry\b", r":=\s*$"):
        t = re.compile(term, re.M).search(text, start)
        if t and (end is None or t.start() < end):
            end = t.start()
    if end is None:
        nxt = re.compile(r"\n\s*\n|\n/--|\n@\[").search(text, start)
        end = nxt.start() if nxt else min(len(text), start + 2000)
    sig = text[start:end].rstrip()
    sig = re.sub(r"[ \t]+\n", "\n", sig)
    return sig


def module_doc(text):
    m = re.search(r"/-!(.*?)^-/", text, re.S | re.M)
    return m.group(1) if m else ""


def parse_header(md):
    """(title, prose, refs_block) from the module docstring."""
    title = ""
    tm = re.search(r"^#\s+(.*)$", md, re.M)
    if tm:
        title = tm.group(1).strip()
    # references block: from *Reference(s):* to end
    rm = re.search(r"\*References?:?\*", md)
    refs = md[rm.end():] if rm else ""
    prose = md[:rm.start()] if rm else md
    prose = re.sub(r"^#+\s+.*$", "", prose, flags=re.M)
    return title, clean_doc(prose), refs


URL_RE = re.compile(r"https?://[^\s)\]\"',]+")


def pick_url(refs, whole, subdir):
    urls = URL_RE.findall(refs) or URL_RE.findall(whole)
    urls = [u.rstrip(".,;") for u in urls
            if "apache.org/licenses" not in u and "github.com/google-deepmind" not in u]
    if not urls:
        return None
    prefs = {"Wikipedia": "wikipedia.org", "OEIS": "oeis.org",
             "Mathoverflow": "mathoverflow.net", "Millenium": "claymath.org",
             "GreensOpenProblems": "greenbj", "Arxiv": "arxiv.org",
             "Kourovka": "arxiv.org"}
    key = prefs.get(subdir)
    if key:
        for u in urls:
            if key in u:
                return u
    return urls[0]


def derive_source(subdir, title, refs, path, url):
    if subdir == "OEIS":
        a = re.search(r"A\d{6}", refs + " " + path)
        anum = a.group(0) if a else "A" + os.path.basename(path).split(".")[0]
        return "OEIS %s" % anum
    if subdir == "Wikipedia":
        page = ""
        if url and "wikipedia.org/wiki/" in url:
            page = url.split("/wiki/")[-1].replace("_", " ")
            try:
                from urllib.parse import unquote
                page = unquote(page)
            except Exception:
                pass
        return "Wikipedia: %s" % (page or title)
    if subdir == "GreensOpenProblems":
        return "Ben Green's open problems list (%s)" % (title or os.path.basename(path))
    if subdir == "Millenium":
        return "Clay Millennium Prize Problems: %s" % title
    if subdir == "HilbertProblems":
        return "Hilbert's problems: %s" % title
    if subdir == "Kourovka":
        return "The Kourovka Notebook: %s" % title
    if subdir == "Mathoverflow":
        return "MathOverflow question %s" % os.path.basename(path).replace(".lean", "")
    if subdir == "Arxiv":
        return "arXiv:%s (%s)" % (os.path.basename(os.path.dirname(path)), title)
    if subdir == "OpenQuantumProblems":
        return "Open Quantum Problems list: %s" % title
    if subdir == "OptimizationConstants":
        return "Tao's optimization constants list: %s" % title
    if subdir == "LittProblems":
        return "Litt problems list: %s" % title
    if subdir == "Books":
        lbl = re.search(r"^\s*[-*]\s+(.+)$", refs, re.M)
        return "Book: %s" % (lbl.group(1).strip() if lbl else title)
    return title or subdir


# --------------------------------------------------------------- classification

FINITE_HINT = re.compile(r"Finset|Fin \d|Fin n|SimpleGraph \(Fin|Matrix \(Fin|"
                         r"List |Multiset|Finite |Set\.Finite|Fintype")
GRAPH_HINT = re.compile(r"SimpleGraph|Graph\b|Digraph")
NUM_LIT = re.compile(r"(?<![\w.])\d+\.\d+(?![\w])")


def split_sig(sig):
    """(binders, conclusion) split at the first top-level `:` after the decl name."""
    m = re.match(r"\s*(?:theorem|lemma|def|abbrev|instance|example)\s+[\w'.\u2080-\u2089]+", sig)
    i = m.end() if m else 0
    depth = 0
    while i < len(sig):
        c = sig[i]
        if c in "([{\u27e6\u2983\u2e28":
            depth += 1
        elif c in ")]}\u27e7\u2984\u2e29":
            depth -= 1
        elif c == ":" and depth == 0 and sig[i:i + 2] != ":=":
            return sig[:i], sig[i + 1:]
        i += 1
    return sig, sig


NUMTYPE = re.compile(r"\u211d|\u211a|\u2115|\u2124|NNReal|ENNReal|EReal")


ARROW = "\u2192"
SCALAR = re.compile(r"^\s*\(?\s*(\u211d|\u211a|\u2115|\u2124|NNReal|ENNReal|EReal|"
                    r"\u211d\u2265*0*[\u221e]*)\s*\)?\s*$")



INF_BODY = re.compile(r"\u2200|atTop|Tendsto|Filter|=o\[|=O\[|Set\.Infinite|"
                      r"\u2200\u1d43\u1da0|Asymptotic")
FAMILY_BINDER = re.compile(r"[:(]\s*(\u2115|\u2124)\s*\)?\s*\u2192|"
                           r"\(\s*\w+\s*:\s*(\u2115|\u2124)\s*\)\s*\u2192")
HARD_CHECK = re.compile(r"\u211d|\u2102|Transcendental|Irrational|Real\.|Complex\.|"
                        r"Measure|Integral")


def leading_exists(c):
    """(binder_text, body) of a leading \u2203, or (None, None)."""
    m = re.match(r"\s*\u2203\s*(.*?),", c, re.S)
    if not m:
        return None, None
    return m.group(1), c[m.end():]


def finite_witness(c):
    """Does one concrete finite object settle the leading \u2203?"""
    binder, body = leading_exists(c)
    if binder is None:
        return None
    if not FINITE_HINT.search(binder):
        return None
    if FAMILY_BINDER.search(binder):
        return None
    if INF_BODY.search(body):
        return None
    return "unknown" if HARD_CHECK.search(body) else "poly"


def answer_slot_type(concl, deftypes):
    """Coarse type of the object `answer(sorry)` stands for.

    Returns "num" (a single number), "fam" (a function/family), "fin" (a finite
    object), "prop", or None when it cannot be read off syntactically.
    """
    c = concl
    if "answer(" not in c:
        return None
    # explicit ascription: (answer(sorry) : T)
    m = re.search(r"\(\s*answer\(sorry\)\s*:\s*([^)]+)\)", c)
    if not m:
        # let x : T := answer(sorry)
        m = re.search(r"let\s+[\w'\u2080-\u2089]+\s*:\s*([^:=]+):=\s*answer\(sorry\)", c)
    if m:
        t = m.group(1).strip()
        if ARROW in t or "\u2200" in t:
            return "fam"
        if SCALAR.match(t):
            return "num"
        if re.search(r"Finset|Fin\b|List|Multiset", t):
            return "fin"
        return None
    if re.search(r"answer\(sorry\)\s*\u2208\s*Set\.I[co][co]", c):
        return "num"
    if re.search(r"Is(Greatest|Least)\b[^\n]*answer\(sorry\)", c):
        return "num"
    # X = answer(sorry)  /  answer(sorry) = X
    m = re.search(r"([^\n=\u2194]+?)=\s*answer\(sorry\)", c) or \
        re.search(r"answer\(sorry\)\s*=([^\n=\u2194]+)", c)
    if m:
        rhs = m.group(1).strip()
        if re.match(r"^[-\d]", rhs):
            return "num"
        h = re.match(r"([A-Za-z_][\w'.\u2080-\u2089]*)", rhs)
        if h and h.group(1) in deftypes:
            ret = deftypes[h.group(1)].split(ARROW)[-1].strip()
            if SCALAR.match(ret):
                return "num"
            if re.search(r"Finset|Fin\b|List|Multiset", ret):
                return "fin"
            return None
        if rhs.startswith("{") or rhs.startswith("Set"):
            return None
    return None


def classify(sig, doc, deftypes=None):
    deftypes = deftypes or {}
    binders, concl = split_sig(sig)
    c = concl.strip()
    has_answer = "answer(" in sig

    # A leading `answer(sorry) \u2194 ...` is a yes/no question: the "witness" is a
    # truth value, not an object. Classify the right-hand side instead.
    yesno = bool(re.match(r"\s*answer\(sorry\)\s*\u2194", c))
    if yesno:
        c = c.split("\u2194", 1)[1].strip()

    # what kind of object does `answer(sorry)` stand for?
    slot = answer_slot_type(concl, deftypes) if (has_answer and not yesno) else None
    numeric_answer = slot == "num"

    forall_int = bool(re.search(r"[({\u2983]\s*[A-Za-z_][\w',\s\u2080-\u2089]*:\s*"
                                r"(\u2115|\u2124|\u211a|\u211d)\b", binders)) or \
        bool(re.match(r"\s*\u2200\s*[^,]*(\u2115|\u2124)", c)) or \
        bool(re.search(r"\u2200\s*[\w'\u2080-\u2089]+\s*[:>]", c))
    ex_head = bool(re.match(r"\s*\u2203", c))
    ex_head_rhs = ex_head

    # ---- quantifier shape
    if GRAPH_HINT.search(sig):
        shape = "forall-graphs"
    elif numeric_answer or (NUM_LIT.search(c) and re.search(r"\u2264|<|\u2265|>", c)) or \
            re.search(r"IsGreatest|IsLeast|sSup|sInf", c):
        shape = "bound"
    elif forall_int:
        shape = "forall-integers"
    elif ex_head:
        shape = "exists-construction"
    elif "\u2203" in c:
        shape = "exists-construction"
    else:
        shape = "other"

    # ---- witness type
    fin_cost = finite_witness(c)
    family_ex = bool(re.search(r"\u2203\s*\(?[\w'\u2080-\u2089]+\s*:\s*"
                               r"(\u2115|\u2124|\u211d|Fin\b)[^,]*\u2192", c))
    if yesno:
        wt, cost = ("finite-object", fin_cost) if fin_cost else ("none", "unknown")
    elif slot == "num":
        wt, cost = "numeric-bound", "unknown"
    elif slot == "fam":
        wt, cost = "parametric-family", "unknown"
    elif slot == "fin":
        wt, cost = "finite-object", "unknown"
    elif fin_cost:
        wt, cost = "finite-object", fin_cost
    elif family_ex:
        wt, cost = "parametric-family", "unknown"
    elif NUM_LIT.search(c) and re.search(r"\u2264|<|\u2265|>", c):
        wt, cost = "numeric-bound", "unknown"
    else:
        wt, cost = "none", "unknown"
    return shape, wt, cost


DEF_TYPE_RE = re.compile(
    r"^\s*(?:noncomputable\s+|private\s+|protected\s+|partial\s+)*"
    r"(?:def|abbrev)\s+([\w'.\u2080-\u2089]+)([^\n]*?):\s*([^\n:=]+?)\s*(?::=|$)", re.M)


def def_types(text):
    return {m.group(1): m.group(3) for m in DEF_TYPE_RE.finditer(text)}


BOUND_LOW = re.compile(r"^\s*\(?\s*([0-9][0-9_.]*)\s*(?:\)?\s*)(?:≤|<)\s*([A-Za-z_][\w'.₀-₉]*)\s*$")
BOUND_UP = re.compile(r"^\s*([A-Za-z_][\w'.₀-₉]*)\s*(?:≤|<)\s*\(?\s*([0-9][0-9_.]*)\s*\)?\s*$")


def sibling_bounds(sig, siblings):
    """current_bounds from sibling theorems asserting a numeric inequality on a
    constant that appears in this open statement."""
    lo = up = None
    for s in siblings:
        m = re.search(r":\s*(.*)$", s.replace("\n", " "), re.S)
        if not m:
            continue
        body = m.group(1).strip()
        a = BOUND_LOW.match(body)
        b = BOUND_UP.match(body)
        if a and a.group(2) in sig:
            lo = a.group(1)
        elif b and b.group(1) in sig:
            up = b.group(2)
    return {"lower": lo, "upper": up}


# ------------------------------------------------------------------- extraction

def theorem_name(sig):
    m = re.match(r"\s*(?:theorem|lemma|def|abbrev|instance|example)\s+([\w'.₀-₉]+)", sig)
    return m.group(1) if m else None


def defs_used(text, sig):
    """Docstrings of `def`s in the file whose name occurs in the signature."""
    out = []
    for m in re.finditer(r"/--(.*?)-/\s*\n(?:@\[[^\]]*\]\s*\n)?\s*"
                         r"(?:noncomputable\s+|private\s+|protected\s+)*"
                         r"(?:def|abbrev)\s+([\w'.₀-₉]+)", text, re.S):
        name = m.group(2)
        if re.search(r"(?<![\w.])" + re.escape(name) + r"(?![\w])", sig):
            out.append("`%s`: %s" % (name, clean_doc(m.group(1))))
    return out


def scan_fc():
    entries = []
    for dirpath, dirnames, filenames in os.walk(FC_BASE):
        rel_top = os.path.relpath(dirpath, FC_BASE).split(os.sep)[0]
        if rel_top in EXCLUDE_DIRS:
            dirnames[:] = []
            continue
        for fn in sorted(filenames):
            if not fn.endswith(".lean"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, FC)
            subdir = os.path.relpath(path, FC_BASE).split(os.sep)[0]
            if subdir in EXCLUDE_DIRS:
                continue
            text = open(path, encoding="utf-8").read()
            if "category research open" not in text:
                continue
            STATS["files_scanned"] += 1
            md = module_doc(text)
            dtypes = def_types(text)
            title, prose, refs = parse_header(md)
            url = pick_url(refs, text, subdir)
            source = derive_source(subdir, title, refs, path, url)

            # all attribute blocks in this file
            blocks = []
            for m in re.finditer(r"@\[", text):
                s = m.start()
                e = match_bracket(text, s + 1)
                if e < 0:
                    continue
                blocks.append((s, e, text[s:e]))
            solved_sigs, solved_docs = [], []
            for (s, e, attr) in blocks:
                if "category research solved" in attr or "category research" in attr and "open" not in attr:
                    sg = signature_after(text, e)
                    if sg:
                        solved_sigs.append(sg)
                        d = preceding_docstring(text, s)
                        if d:
                            solved_docs.append(d)

            opens = [(s, e, a) for (s, e, a) in blocks if "category research open" in a]
            STATS["open_attrs"] += len(opens)
            multi = len(opens) > 1
            base_id = "fc-%s-%s" % (subdir.lower(), fn[:-5])
            if subdir == "Arxiv":
                base_id = "fc-arxiv-%s-%s" % (
                    os.path.basename(dirpath).replace(".", ""), fn[:-5])
            elif os.path.basename(dirpath) != subdir:
                base_id = "fc-%s-%s-%s" % (subdir.lower(), os.path.basename(dirpath), fn[:-5])

            for i, (s, e, attr) in enumerate(opens):
                doc = preceding_docstring(text, s)
                sig = signature_after(text, e)
                if sig is None:
                    STATS["dropped_no_doc"] += 1
                    continue
                line = text[:s].count("\n") + 1
                ams = re.search(r"AMS\s+([\d\s]+)", attr)
                ams = ams.group(1).strip() if ams else None
                tname = theorem_name(sig)

                # statement_nl: header title + doc + used definitions + prose fallback
                parts = []
                if doc:
                    parts.append(doc)
                elif prose:
                    parts.append(prose)
                else:
                    STATS["dropped_no_doc"] += 1
                    continue
                dfs = defs_used(text, sig)
                if dfs:
                    parts.append("Definitions used: " + " ".join(dfs))
                nl = "Context (%s). %s" % (title, "\n\n".join(parts)) if title else \
                     "\n\n".join(parts)
                if len(nl) > 3000:
                    nl = nl[:3000].rsplit(" ", 1)[0] + " ..."

                shape, wt, cost = classify(sig, doc or "", dtypes)
                bounds = sibling_bounds(sig, solved_sigs)

                known = None
                if solved_docs:
                    known = " | ".join(d[:300] for d in solved_docs[:6])
                # prior attempts: bibliography lines without a bare URL-only entry
                bib = []
                for ln in refs.split("\n"):
                    t = ln.strip().lstrip("*-").strip()
                    if len(t) > 30 and not t.startswith("["):
                        bib.append(t)
                    elif re.match(r"^\[[A-Z][\w']*\d", t):
                        bib.append(t)
                prior = " ".join(bib)[:900] or None
                todos = re.findall(r"^\s*--\s*TODO.*$", text, re.M)

                notes = []
                if ams:
                    notes.append("AMS %s" % ams)
                if subdir == "OEIS":
                    a = re.search(r"A\d{6}", refs + " " + text)
                    if a:
                        notes.append("OEIS %s" % a.group(0))
                notes.append("formal-conjectures subdir %s" % subdir)
                if tname:
                    notes.append("lean decl `%s`" % tname)
                if "answer(sorry)" in sig:
                    notes.append("statement uses `answer(sorry)` placeholder: the task is to "
                                 "supply the missing object/value, not just prove a proposition")
                if todos:
                    notes.append("file TODOs: " + " ".join(t.strip() for t in todos)[:300])
                notes.append("witness_type/quantifier_shape assigned by regex heuristic in "
                             "mine/cache/h2_extract.py (classify()); treat as a first pass")

                suf = chr(97 + i) if i < 26 else "%d" % (i + 1)
                eid = base_id + ("-" + suf if multi else "")
                entries.append({
                    "id": eid,
                    "source": source,
                    "url": url,
                    "provenance": "clone:google-deepmind/formal-conjectures@%s:%s#L%d"
                                  % (FC_COMMIT, rel, line),
                    "statement_nl": nl,
                    "statement_formal": (attr + "\n" + sig).strip(),
                    "quantifier_shape": shape,
                    "witness_type": wt,
                    "witness_check_cost": cost,
                    "known_cases": known,
                    "current_bounds": bounds,
                    "prior_attempts": prior,
                    "prize": None,
                    "class": None,
                    "tractability": None,
                    "notes": "; ".join(notes),
                })
    return entries


# ----------------------------------------------------------------- mathlib4

MATHLIB_KEYWORDS = re.compile(r"open problem|Open problem|conjecture|Conjecture|CONJECTURE")


def scan_mathlib():
    """Strict sweep: `sorry` in non-test files, plus TODO/conjecture comments.
    Returns (candidates_looked_at, entries)."""
    looked = 0
    entries = []
    hits = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(ML, "Mathlib")):
        for fn in filenames:
            if not fn.endswith(".lean"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ML)
            try:
                text = open(path, encoding="utf-8").read()
            except Exception:
                continue
            for m in re.finditer(r"(?<![\w.])sorry(?![\w])", text):
                line = text[:m.start()].count("\n") + 1
                ctx = text[max(0, m.start() - 1500):m.start() + 200]
                looked += 1
                if MATHLIB_KEYWORDS.search(ctx):
                    hits.append((rel, line, ctx[-900:]))
    return looked, hits, entries


def main():
    entries = scan_fc()
    # dedupe by id and by (statement_formal)
    seen_id, seen_sig, final = set(), set(), []
    for e in entries:
        if e["id"] in seen_id:
            STATS["dropped_dup"] += 1
            continue
        # dedupe on formal statement AND the NL statement together: many OEIS
        # files share a syntactically identical `conjecture` line while `a`/`A`
        # denote different sequences, so the signature alone is not a key.
        key = (re.sub(r"\s+", " ", e["statement_formal"]),
               re.sub(r"\s+", " ", e["statement_nl"]))
        if key in seen_sig:
            STATS["dropped_dup"] += 1
            continue
        seen_id.add(e["id"])
        seen_sig.add(key)
        final.append(e)
    STATS["emitted"] = len(final)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for e in final:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    sys.stderr.write(json.dumps(STATS, indent=2) + "\n")
    from collections import Counter
    sys.stderr.write("per-subdir: %s\n" % json.dumps(
        dict(Counter(e["notes"].split("formal-conjectures subdir ")[1].split(";")[0]
                     for e in final)), indent=2))
    sys.stderr.write("witness_type: %s\n" % json.dumps(
        dict(Counter(e["witness_type"] for e in final))))
    sys.stderr.write("quantifier_shape: %s\n" % json.dumps(
        dict(Counter(e["quantifier_shape"] for e in final))))


if __name__ == "__main__":
    main()
