# Frozen verifier

Built once, in phase P3, before any search runs. Then locked with `scripts/freeze.sh`.

Each file in `checkers/` is standalone: it reads a witness file and exits 0 (accept) or
nonzero (reject). Before freezing, every checker must be tested against **both** a
known-true and a known-false input — an unvalidated checker is worse than no checker,
because it manufactures confidence.

After the freeze, this directory is read-only for the rest of the run. Search agents have
no write access here. Run `scripts/check-freeze.sh` before every verification.

If a checker rejects your witness, the witness is wrong.
