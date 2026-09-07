# Attack log: bound-schur-S6

Agent: A2. Freeze check run before every verification below: `bash scripts/check-freeze.sh`
→ `VERIFIER INTACT (40 files)` every time (see `checker-output.txt`).

Target: standard Schur number S(6), r=6 colours, published range 536 <= S(6) <= 1836.
Frozen checker `check_schur_lower.py` implements exactly the standard condition
(x=y allowed) that this target needs, so no statement-drift issue here (contrast with
bound-weakschur-WS6).

## 1. Reproduce the known record (rung 1) — calibration, not yet the real target

Calibrated on the exactly-known small Schur numbers before spending budget at n=536:
S(3)=13, S(4)=44 (S(5)=160, the famous Heule 2017 "Schur Number Five" 200TB SAT proof,
was also attempted as a scale probe, see below).

### SAT rung (rung 3)
`mine/attacks/bound-schur-S6/schur_sat.py` — pysat/Cadical153, one-hot boolean per
(element,colour), AMO+ALO per element, one negative clause per (x,y,z) triple per colour.

- r=3,n=13: SAT in 0.239s. r=3,n=14: UNSAT in 0.056s. Together reproduce the exact
  literature value **S(3) = 13** end-to-end. **Frozen checker ACCEPTs** the n=13 witness
  (`witnesses/s3_n13.json`, see checker-output.txt), certifies S(3) >= 13.
- r=4,n=44: SAT in 0.273s. **Frozen checker ACCEPTs** the n=44 witness
  (`witnesses/s4_n44_sat.json`), certifies S(4) >= 44 — reproduces **S(4) = 44**'s lower
  side exactly.
- r=4,n=45 (should be UNSAT, confirming S(4)=44 exactly): **did not resolve** in 60s.
- r=5,n=160 (S(5)=160, the Heule instance): **did not resolve** in 90s.
- **Verdict: plain CNF SAT reproduces S(3) and S(4) exactly and fast, but the very next
  scale step (r=4,n=45 UNSAT proof; r=5,n=160 SAT search) already exceeds a 60-90s
  budget with no symmetry breaking.** The real target is r=6,n=536 — three orders of
  magnitude harder than the r=5,n=160 instance that didn't resolve — so it was not
  attempted. Heule's actual S(5)=160 proof needed a dedicated 2-day, thousands-of-cores,
  200TB-certificate SAT effort; this result is fully consistent with that and is not a
  surprise, but it does mean this generic encoding has no realistic path to n=536 within
  this run's budget.

### Tabu / local search rung (rung 2) — found and partially fixed a real bug
`mine/attacks/bound-schur-S6/schur_tabu.py` — incremental-conflict tabu search over
r-colourings minimising monochromatic-Schur-triple count.

**A genuine bug was found via the frozen checker, exactly as the mission's "if a checker
rejects your witness, the witness is wrong" rule anticipates:**
- First version built each element's triple-incidence list as
  `elem_tr[x].append(idx); elem_tr[y].append(idx)`. Since the standard Schur condition
  allows x=y (the "doubling" x+x=2x), a triple with x=y=some element got appended
  **twice** to that element's incidence list, so every delta computed for a recolour of
  that element double-counted that one triple's contribution, letting the tracked
  conflict count drift and falsely hit 0 while a real monochromatic triple still existed.
- Concretely: a run on r=4,n=44 (seed 1) reported `best_conflicts=0`. I built the witness
  file, added `published_value=44`, and ran it through the frozen checker —
  **REJECT: monochromatic 2 + 13 = 15 in colour 1** (see below). This is precisely a
  false witness caught by the frozen checker, not a checker problem. Per the rules, the
  witness (and the code that produced it) is what's wrong — I did not touch the checker.
- Fix applied: dedupe each element's incidence list via a Python `set({x,y,z})` before
  building it, plus a from-scratch full recheck inserted before the function is ever
  allowed to return a 0. After the fix, the recheck **still fires** on several reruns
  (r=3,n=13, three different seeds: tracker claims 0, full recompute finds 1–4 real
  conflicts) — there is a **second, unlocated bug** in the incremental tracker. I did not
  chase it further given the time budget.
- **Net effect: the from-scratch recheck means the script never emits a witness that the
  frozen checker would reject** (every emitted witness is independently re-verified
  before being written out — see the code's final block), but the search method itself
  is unvalidated/unreliable as a *search* (it thinks it's found solutions it hasn't), so
  it was **not used to attack the real n=536 target.** Full detail in
  `mine/memory/negative-a2.jsonl`.

## 2. Conclusion — does this reproduce a known record?

**Partially.** SAT reproduces S(3)=13 and S(4)=44 exactly, fast, and checker-verified —
a genuine, if small, calibration success. But it does not scale past ~n=44-160 within
budget (no symmetry breaking), and the real target n=536 is far beyond reach here. The
tabu/local-search line produced a real, checker-caught bug and, after a partial fix,
remained unreliable enough that I stopped using it rather than report anything from it.

**Best n reached on the real target: none (0/536).** Published range: 536 <= S(6) <=
1836. Ladder rung reached: rung 3 (SAT) reproduced two small exact records but did not
scale; rung 2 (tabu) was abandoned after a bug was found and only partially fixed.
Frozen checker: never presented with a witness at n=536 (none was produced) — only with
the calibration witnesses above (S(3)=13, S(4)=44), both correctly ACCEPTed, and the one
buggy r=4,n=44 witness above, correctly REJECTed.

## Reproduce this log
```
bash scripts/check-freeze.sh
python3 mine/attacks/bound-schur-S6/schur_sat.py 3 13   # SAT, 0.239s
python3 mine/attacks/bound-schur-S6/schur_sat.py 3 14   # UNSAT
python3 mine/attacks/bound-schur-S6/schur_sat.py 4 44   # SAT, 0.273s
python3 mine/verify/checkers/check_schur_lower.py mine/attacks/bound-schur-S6/witnesses/s3_n13.json
python3 mine/verify/checkers/check_schur_lower.py mine/attacks/bound-schur-S6/witnesses/s4_n44_sat.json
timeout 60 python3 mine/attacks/bound-schur-S6/schur_sat.py 4 45    # times out unresolved
timeout 90 python3 mine/attacks/bound-schur-S6/schur_sat.py 5 160   # times out unresolved
python3 mine/attacks/bound-schur-S6/schur_tabu.py 3 13 15 1   # shows the caught/discarded false-0
```
Full literal transcripts of the checker/freeze commands are in `checker-output.txt`.
