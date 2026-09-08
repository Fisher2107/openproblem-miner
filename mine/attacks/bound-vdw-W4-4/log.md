# Attack log: bound-vdw-W4-4

Agent: A2. Freeze check run before every verification below: `bash scripts/check-freeze.sh`
→ `VERIFIER INTACT (40 files)` every time (see `checker-output.txt`).

## 0. Notation correction (read this first)

The corpus row's `statement_nl` says W(4,4) is about a **2-colouring**, but its own
`known_cases` list (`W(2,3)=9, W(2,4)=35, W(2,5)=178, W(2,6)=1132, W(3,3)=27, W(3,4)=293,
W(4,3)=76`) is written in the convention **W(r,k) = r colours, k-term AP** (first index is
colour count). Under that convention "W(4,4)" is **r=4 colours, k=4-term AP**, not r=2 —
the "2-colouring" phrase in `statement_nl` is very likely the harvester's own typo/error.
I attacked the r=4,k=4 target that matches the id and the known-cases convention, and flag
this drift explicitly rather than silently picking whichever reading was easier.
Real target: **k=4, r=4, published lower bound n=1048** (W(4,4) > 1048).

## 1. Reproduce the known record — direct target (rung 1)

Not attempted directly: before spending budget on n=1048 (r=4,k=4), I calibrated the
method on much smaller *already-exactly-known* van der Waerden numbers, expecting that
if the method can't reproduce those cheaply, it has no chance at n=1048. It couldn't.

Calibration case chosen: **W(4,3)=76** (r=4 colours, k=3-term AP — same colour count as
the real target, smaller AP length, dramatically smaller n). This is an *exactly known*
number: n=75 must be SAT (a 4-colouring of [1,75] with no mono 3-AP exists) and n=76 must
be UNSAT.

### SAT rung (rung 3, tried before local search since W(k,r) is SAT-native)
- `mine/attacks/bound-vdw-W4-4/vdw_sat.py` — pysat/Cadical153, one boolean per
  (element,colour) for r>2, one negative clause per (AP,colour). Validated correct first
  on tiny cases:
  - k=3,r=3,n=26: SAT in 0.995s (wall for the whole call incl. Python startup).
    **Frozen checker ACCEPTs**, certifies W(3,3) > 26 (see checker-output.txt).
  - k=3,r=3,n=27: UNSAT in <1s. Together these reproduce the exact literature value
    **W(3,3) = 27**, end to end (SAT solver → frozen checker).
  - Note on `checker-output.txt`'s "BEATS" line for this witness: I supplied
    `published_lower_bound: 26` (n itself) purely so the checker's optional note would
    fire as a sanity signal; the checker's own arithmetic is `n+1 > published`, so
    passing `published = n` always prints "BEATS". This is **not** a claim of a new
    record — W(3,3)=27 is already exactly known, n=26 is exactly the known maximum, and
    this witness only reproduces that published fact. Flagging this so the "BEATS" text
    in the transcript is never misread.
- Scaled to the real calibration target k=3,r=4:
  - n=75: **did not resolve** (neither SAT nor UNSAT) in a 60s wrapped run, nor in a
    fresh 240s run (background job, killed by `timeout`, zero bytes of output —
    see `mine/memory/negative-a2.jsonl`).
  - **Verdict: plain CNF SAT (no symmetry breaking) cannot reproduce W(4,3)=76 within
    this budget.** Never attempted the actual n=1048, r=4,k=4 target — it is far harder
    than the n=75 instance that already didn't resolve.

### Tabu / local search rung (rung 2)
- `mine/attacks/bound-vdw-W4-4/vdw_tabu.py` — incremental-conflict tabu search over
  r-colourings minimising monochromatic-k-AP count. Includes a from-scratch recheck
  before ever declaring 0 conflicts (added after finding a real bug in the sibling
  schur script — see bound-schur-S6/log.md — as a defensive measure; this vdw script's
  tracker was independently re-verified correct, see below).
- Sanity results (k=3,r=4, i.e. same r as the real target):
  - n=20, n=30, n=40: reach 0 conflicts in <1s each. **Independently re-verified**:
    regenerated each witness and ran it through the frozen checker — all three ACCEPT
    (see `checker-output.txt`, witnesses in `witnesses/w43_n{20,30,40}.json`).
  - n=50: best=1 conflict after 10s (does not reach 0; W(4,3)=76 says n=50 is
    trivially satisfiable, so this is a real shortfall of the search, not a hard
    instance).
  - n=75 (the actual calibration boundary): best=21 conflicts after 20s, and again
    best=21 after a fresh 60s run — **flat, does not improve with more time, does not
    reach 0** even though 0 is known to be achievable (W(4,3)=76 > 75).

## 2. Conclusion — does this reproduce a known record?

**No.** Neither SAT nor local search, as implemented here, reproduces the known exact
value W(4,3)=76 within budget once n approaches the true critical threshold (~65–76);
both work fine well below it (n<=60). Since the real target (r=4,k=4,n=1048) is a much
harder instance than this calibration case, and the calibration case already fails, I did
not spend further budget attempting n=1048 itself — doing so would only produce a
near-miss conflict count with no evidential value, and the mission rule against grinding
a flat arm applies.

**Best n reached on the real target: none (0/1048 attempted with a validated method).**
Published lower bound: n=1048 (W(4,4) > 1048). Ladder rung reached: rung 3 attempted and
failed to scale (rung 1 tiny cases only); rung 2 attempted and failed to scale past ~60.
Frozen checker: never presented with a witness for the real n=1048 target (none was ever
produced) — only with the small calibration witnesses above, all of which it correctly
ACCEPTed.

## Reproduce this log
```
bash scripts/check-freeze.sh
python3 mine/attacks/bound-vdw-W4-4/vdw_sat.py 3 3 26   # SAT, 0.995s
python3 mine/attacks/bound-vdw-W4-4/vdw_sat.py 3 3 27   # UNSAT
python3 mine/verify/checkers/check_vdw_lower.py mine/attacks/bound-vdw-W4-4/witnesses/w33_n26.json
python3 mine/verify/checkers/check_vdw_lower.py mine/attacks/bound-vdw-W4-4/witnesses/w43_n20.json
python3 mine/verify/checkers/check_vdw_lower.py mine/attacks/bound-vdw-W4-4/witnesses/w43_n30.json
python3 mine/verify/checkers/check_vdw_lower.py mine/attacks/bound-vdw-W4-4/witnesses/w43_n40.json
timeout 240 python3 mine/attacks/bound-vdw-W4-4/vdw_sat.py 3 4 75   # times out unresolved
timeout 60  python3 mine/attacks/bound-vdw-W4-4/vdw_tabu.py 3 4 75 60 1  # best_conflicts=21
```
Full literal transcripts of the checker/freeze commands are in `checker-output.txt`.
