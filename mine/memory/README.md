# Negative memory

`negative.jsonl` is the compounding asset of the run: every ansatz family that failed,
with a structured reason. Later waves read it and prune. Schema:

    {"problem_id": "...", "ansatz": "...", "why_failed": "...", "cost": "..."}

Attack agents write `negative-<agent>.jsonl` (one file each, to avoid interleaved appends)
and the orchestrator merges them into `negative.jsonl`.
