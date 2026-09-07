# Attack log: bound-ramsey-R3333

Target (from `mine/corpus/problems.jsonl`, id `bound-ramsey-R3333`): the 4-colour diagonal
Ramsey number R(3,3,3,3). Corpus entry states published range 51 <= R(3,3,3,3) <= 64
(lower bound 1970s construction, upper bound Sanchez-Flores 1995). Improving the lower
bound by one means exhibiting a 4-colouring of the edges of K_51 with no monochromatic
triangle in any of the 4 colours.

## Step 0: freeze check

```
$ bash scripts/check-freeze.sh
VERIFIER INTACT (40 files)
```

## Finding: the frozen checker cannot verify this family at all -- stopped at rung 0

`mine/verify/checkers/check_ramsey_lower.py` is the only Ramsey checker that exists
(`ls mine/verify/checkers/` -- confirmed no other `*ramsey*` or multicolor checker is
present: `grep -rl "multicolor\|4-colour\|R(3,3,3,3)" mine/verify/` returns nothing).

Reading its docstring and code (`mine/verify/checkers/check_ramsey_lower.py`), the witness
schema is:

```
{"family":"ramsey","s":<s>,"t":<t>,"n":<n>,"graph6":"<one graph>","published_lower_bound":<int>}
```

It decodes exactly ONE graph and checks two things against it: no K_s clique, and no
independent set of size t. That is the certificate shape for the **2-colour** Ramsey
number R(s,t) -- one graph's edges are colour A, its non-edges are colour B, and "no K_s in
colour A, no I_t (= K_t in colour B)" is exactly what a single graph6 string can encode.

R(3,3,3,3) is a **4-colour** Ramsey number. A witness for R(3,3,3,3) > n is an assignment
of one of 4 colours to each of the C(n,2) edges of K_n such that no colour class contains a
monochromatic triangle. That is not expressible as "one graph, clique-size s, independent-
size t" -- there is no way to encode 4 independent colour classes, each individually
triangle-free, into this checker's `{s,t,graph6}` schema. Passing e.g. `s=3,t=3` would only
ask the checker to verify a single 2-colouring (one graph vs. its complement) is
triangle-free both ways, which is the statement for R(3,3)=6, not R(3,3,3,3).

I confirmed this is not a workaround-able input-shape issue (e.g. "just call it once per
colour pair") by re-reading the checker end to end: it hard-codes a single `adj` array from
one `graph6` field and tests clique/independent-set membership against that one array only;
there is nowhere to hand it 4 colour classes or to ask it to jointly verify all C(4,2)=6
pairs of colours are simultaneously triangle-free on a shared vertex set.

Per the mission rules ("if a checker rejects your witness the witness is wrong... editing a
checker so a result passes invalidates the entire run"), the correct action when the
checker's *schema* -- not a witness -- cannot represent the target family is to **not touch
`mine/verify/`** and report the gap, not to bend a 4-colour construction into the 2-colour
shape by mislabeling colours. I did not attempt any witness construction for this target
because there is no schema to submit one against; any witness I built would be
unverifiable by the frozen tooling as it stands, and I have no ability (nor permission) to
add a new checker file under the frozen `mine/verify/` tree.

## Ladder rung reached

**Rung 0 (pre-attack, checker compatibility check).** Never reached rung 1 (reconstruct
known record) because there is no frozen checker this target's witness type can be run
against.

## Verdict

STOP. This is a triage/verifier-coverage gap, not a search failure: `bound-ramsey-R3333`
was scored `class: "A"` (finite-witness refutable) in the corpus and handed to a Class-C
Ramsey attack agent, but the multicolour Ramsey family has no corresponding checker in
`mine/verify/checkers/`. Only the 2-colour case (`check_ramsey_lower.py`) was built. No
compute was spent searching for a witness, because no witness of this shape could be
verified even if found. This should be reported to whoever owns P3/verifier-build as a
missing checker, and `bound-ramsey-R3333` should be considered **not attack-eligible**
until a multicolour-Ramsey checker exists and is frozen.

Time spent: ~3 minutes (reading the checker, corpus entry, and confirming no alternate
checker exists).
