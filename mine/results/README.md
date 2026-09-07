> **Run 1 (2026-09-06/07) shipped nothing, and this directory is empty on purpose.**
> No conjecture in the 1,541-problem corpus was refuted and no published bound was beaten,
> so there was nothing to promote. The verification tiers were exercised end to end on a
> *positive control* instead — a rediscovered counterexample to a conjecture that was
> already refuted in the literature — which passed T1 (frozen checker), T2 (blind
> independent reimplementation) and T3 (Lean, `#print axioms` clean). That control lives in
> `mine/attacks/t3-positive-control/`, deliberately **not** here, because it is not a
> discovery. See `mine/REPORT.md`.

# Results

One directory per result: `mine/results/<problem-id>/` containing

| file | contents |
|---|---|
| `statement.md` | the conjecture in natural language, its source URL, and who registered it |
| `witness.json` | the counterexample / construction / bound, in exact arithmetic — no floats |
| `checker.txt` | the exact frozen-verifier command that accepts this witness, and its output |
| `TIER` | one line: `T1`, `T2`, or `T3` |
| `prior-art.md` | what you searched to confirm this is not already known, and where |
| `lean/` | for T3: the formalization, compiling with no `sorry` |
| `backtranslation.md` | for T3: the Lean statement rendered back to English by a separate agent, diffed against `statement.md` |

Class A and B ship at T3 only. Class C ships at T2 and is flagged `needs-human-referee`.

Nothing here is described as "proved" or "disproved" until a human has signed off on the
**statement** — the dominant failure mode is correctly proving something nobody asked about.

CI re-verifies every witness in this directory from a clean checkout. If it does not
reproduce there, it is not a result.
