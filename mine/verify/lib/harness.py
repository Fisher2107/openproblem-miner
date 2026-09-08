"""Shared plumbing for the frozen checkers.

Contract for every checker in mine/verify/checkers/:
  usage:  python3 <checker>.py <witness.json>
  exit 0  the witness IS a counterexample to the stated conjecture (ACCEPT)
  exit 1  the witness is NOT a counterexample, or a claimed value is wrong (REJECT)
  exit 2  the witness is malformed, or too large to verify exactly (REFUSE)

Witness format (JSON):
  {"conjecture": "wow2-160",
   "graph6":     "IheA@GUAo",           # or "edges": [[0,1],...] with "n": <int>
   "claimed_values": {"Ls": 6, ...}}    # optional; every entry is re-checked exactly

REFUSE is never silently upgraded to ACCEPT. If this checker cannot verify something
exactly, it rejects. A checker that guesses is worse than no checker.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exactgraph as E     # noqa: E402

ACCEPT, REJECT, REFUSE = 0, 1, 2


def _refuse_on_crash(exc_type, exc, tb):
    """Any uncaught exception in a checker becomes REFUSE (2), never ACCEPT.

    The failure mode this guards against is a checker that dies part-way through --
    on an oversized witness, an arithmetic guard, a malformed field -- and whose
    nonzero-but-unspecified exit status gets read as something other than what it is.
    A verifier that crashes has verified nothing.
    """
    import traceback
    print("REFUSE: checker aborted: %s: %s" % (exc_type.__name__, exc), file=sys.stderr)
    traceback.print_exception(exc_type, exc, tb, file=sys.stderr)
    sys.stderr.flush()
    sys.stdout.flush()
    os._exit(REFUSE)


sys.excepthook = _refuse_on_crash


def load(argv):
    if len(argv) != 2:
        print("usage: %s <witness.json>" % argv[0], file=sys.stderr)
        sys.exit(REFUSE)
    try:
        w = json.load(open(argv[1]))
    except Exception as e:
        print("REFUSE: cannot parse witness: %s" % e, file=sys.stderr)
        sys.exit(REFUSE)
    try:
        if "graph6" in w:
            n, adj = E.decode_graph6(w["graph6"])
        elif "edges" in w and "n" in w:
            n, adj = E.from_edge_list(int(w["n"]), w["edges"])
        else:
            raise ValueError("witness needs 'graph6' or ('n' and 'edges')")
    except Exception as e:
        print("REFUSE: %s" % e, file=sys.stderr)
        sys.exit(REFUSE)
    return w, n, adj


def require_connected(n, adj):
    if not E.is_connected(n, adj):
        print("REJECT: the conjecture is quantified over CONNECTED graphs and this "
              "witness is disconnected", file=sys.stderr)
        sys.exit(REJECT)


def check_claims(w, computed):
    """Every claimed value must match the exact recomputation."""
    claims = w.get("claimed_values") or {}
    bad = []
    for k, v in claims.items():
        if k not in computed:
            bad.append("%s: checker does not compute this quantity" % k)
            continue
        got = computed[k]
        if str(got) != str(v) and got != v:
            bad.append("%s: witness claims %r, exact recomputation gives %r" % (k, v, got))
    if bad:
        for b in bad:
            print("REJECT (claim mismatch): " + b, file=sys.stderr)
        sys.exit(REJECT)


def verdict(is_counterexample, computed, lhs_desc, rhs_desc):
    print(json.dumps({k: str(v) for k, v in computed.items()}, indent=2, sort_keys=True))
    print("statement side A: %s" % lhs_desc)
    print("statement side B: %s" % rhs_desc)
    if is_counterexample:
        print("ACCEPT: the conjecture's conclusion FAILS on this witness while its "
              "hypotheses HOLD -- this is a counterexample.")
        sys.exit(ACCEPT)
    print("REJECT: the conjecture holds on this witness (or its hypotheses do not apply).")
    sys.exit(REJECT)
