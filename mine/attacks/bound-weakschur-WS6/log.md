# Attack log: bound-weakschur-WS6

Agent: A2. Freeze check run before verification below: `bash scripts/check-freeze.sh` →
`VERIFIER INTACT (40 files)` (see `checker-output.txt`).

## The checker cannot certify this target — stated plainly, not glossed over

The corpus target is the **weak** Schur number WS(6): the largest N such that
{1,...,N} splits into 6 classes with no monochromatic **x < y < z**, x+y=z (strict
inequality — a monochromatic "doubling" x+x=2x is explicitly *allowed*). Published
lower bound: WS(6) >= 646.

The only frozen checker for this family, `mine/verify/checkers/check_schur_lower.py`,
implements the **standard** Schur condition: its inner loop is
`for y in range(x, n+1)` — i.e. **x=y is included**, so it rejects any monochromatic
doubling. That is the correct, deliberate behaviour for `bound-schur-S6` (the standard
Schur number), but it is **the wrong condition for weak Schur**: standard-Schur-valid
colourings are a strict subset of weak-Schur-valid colourings (weak forbids strictly
fewer patterns), so a colouring that legitimately witnesses a weak-Schur bound can
contain doublings and would be **wrongly rejected** by this checker, and — more
importantly for the direction that matters — a colouring the checker *does* ACCEPT would
only ever certify the (unrelated, much smaller) standard Schur number S(6), never WS(6).

**No search was run against the real n=646 target for this reason: there is nothing
this checker's acceptance would mean about weak Schur, so no amount of local search or
SAT solving against it could produce a certifiable weak-Schur result.** This is exactly
the statement-drift failure the pipeline is built to catch, and per instructions I am
reporting it rather than attacking a target the frozen tooling cannot verify.

## Concrete demonstration

To make the mismatch checkable rather than asserted, I ran the smallest possible
counterexample: the known exact value **WS(1) = 2** (from the corpus's own
`known_cases` for this row) is witnessed, under the *weak* definition, by the trivial
1-colouring of {1,2}: colour = [0,0]. Under weak Schur this is valid — the only sum
1+1=2 has x=y, which weak Schur explicitly allows since it requires x<y strictly.

Running it through the frozen (standard-Schur) checker:
```
$ python3 mine/verify/checkers/check_schur_lower.py mine/attacks/bound-weakschur-WS6/witnesses/ws1_n2_demo.json
{
  "r": 1,
  "n": 2,
  "monochromatic_sum_found": {"x": 1, "y": 1, "z": 2, "colour": 0}
}
REJECT: monochromatic 1 + 1 = 2 in colour 0
```
The frozen checker **rejects a witness that correctly certifies a known-true weak-Schur
statement** (WS(1) >= 2, in fact WS(1) = 2 exactly). This is the sharpest, smallest
possible demonstration that "the frozen checker accepts this witness" and "this witness
certifies a weak-Schur bound" are different, unrelated claims, and that acceptance by
this checker must never be read as a weak-Schur result.

## Conclusion

**Not attacked.** No SAT or local-search run was performed against n=646 (or any n) for
the actual weak-Schur objective, because the only available frozen checker does not
implement the weak-Schur condition and cannot be edited (mine/verify/ is frozen). Ladder
rung reached: 0 (blocked before rung 1 by a verified statement/checker mismatch).
Best n reached vs published: not applicable / not attempted, 0 vs 646.

If this target is to be attacked, the correct next step is for a future verifier-build
phase to add a *separate*, properly frozen `check_weak_schur_lower.py` (x<y strict) —
not to touch the existing `check_schur_lower.py`, which is correct for its own,
different target (`bound-schur-S6`).

## Reproduce this log
```
bash scripts/check-freeze.sh
python3 mine/verify/checkers/check_schur_lower.py mine/attacks/bound-weakschur-WS6/witnesses/ws1_n2_demo.json
```
Full literal transcript in `checker-output.txt`.
