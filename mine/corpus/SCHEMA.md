# Corpus schema (one JSON object per line)

```json
{
  "id": "erdos-0707",
  "source": "erdosproblems.com",
  "url": "https://...",
  "provenance": "clone:<repo>@<commit>:<path>#L<line> | websearch:<url> | model-knowledge-unverified",
  "statement_nl": "precise natural-language statement, self-contained",
  "statement_formal": "Lean 4 declaration if available, else null",
  "quantifier_shape": "forall-graphs | forall-integers | exists-construction | bound | other",
  "witness_type": "finite-object | parametric-family | numeric-bound | none",
  "witness_check_cost": "trivial | poly | exponential | unknown",
  "known_cases": "what has been verified/proved so far",
  "current_bounds": {"lower": null, "upper": null},
  "prior_attempts": "notable attacks in the literature, if noted at source",
  "prize": null,
  "class": null,
  "tractability": null,
  "notes": ""
}
```

Rules:
- `provenance` is mandatory and must let a third party re-derive the entry.
- Only record `open` problems (or bound gaps). Solved ones are corpus ballast; skip.
- `statement_nl` must be self-contained. If you cannot state it precisely, drop the entry.
- Never invent a URL. If unsure, use `model-knowledge-unverified` and say so in `notes`.
