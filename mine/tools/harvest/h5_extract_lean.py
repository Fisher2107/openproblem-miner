import re, os, json, sys
WOW = "/home/user/openproblem-miner/mine/cache/formal-conjectures/FormalConjectures/WrittenOnTheWallII"
out = {}
for fn in sorted(os.listdir(WOW)):
    if not fn.endswith(".lean") or fn == "Test.lean": continue
    m = re.match(r"GraphConjecture(.+)\.lean$", fn) or re.match(r"(\d+)\.lean$", fn)
    num = m.group(1)
    src = open(os.path.join(WOW, fn)).read()
    lines = src.split("\n")
    # find the research-category attribute and the theorem that follows
    status = None
    for i, ln in enumerate(lines):
        if ln.startswith("@[category research"):
            status = "open" if "research open" in ln else ("solved" if "research solved" in ln else ln)
            # attribute may span lines; find next 'theorem'
            j = i
            while j < len(lines) and not lines[j].lstrip().startswith("theorem "):
                j += 1
            sig = []
            while j < len(lines):
                sig.append(lines[j])
                if ":= by" in lines[j] or lines[j].rstrip().endswith(":="):
                    break
                j += 1
            out[num] = {"file": fn, "status": status, "signature": "\n".join(sig).strip()}
            break
    if num not in out:
        out[num] = {"file": fn, "status": "MISSING", "signature": None}
json.dump(out, open("/home/user/openproblem-miner/mine/cache/h5_lean_sigs.json","w"), indent=1)
print(len(out), "files")
for k,v in out.items():
    print(k, v["status"], "|", (v["signature"] or "")[:70].replace("\n"," "))
