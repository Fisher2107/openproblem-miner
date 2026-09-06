# Verifier toolchain — what installed, what did not, and what that costs

Recorded before the freeze. A missing component narrows which problem classes can ship,
so this file is part of the run's honesty, not bookkeeping.

## Installed and working
| component | version / evidence | used for |
|---|---|---|
| Python | 3.11.15 | every checker; exact `int`/`fractions.Fraction` arithmetic only |
| nauty | 2.8.8 (`nauty-geng`, `nauty-listg`, `nauty-amtog`) | exhaustive graph generation; independent decoder cross-check |
| z3 | 4.8.12 | available to search; not used by any checker |
| python-sat | installed via pip | available to search; not used by any checker |
| sympy / mpmath / networkx / numpy | installed via pip | available to search; **deliberately not imported by any checker** |
| Lean 4 | 4.34.0-rc2, installed by hand from the GitHub release tarball | core-Lean T3 formalization |
| gcc | 13.x | `mine/tools/graphtool.c`, the search-side screener (not part of the verifier) |

## Missing, and the consequence
| component | why | consequence for this run |
|---|---|---|
| **mathlib olean cache** | `cache.mathlib.org`, `lakecache.blob.core.windows.net` and `releases.lean-lang.org` are all refused by the egress proxy (403 on all 8865 cache files, logged in `mine/logs/mathlib-build.log`) | mathlib must be compiled from source on 4 cores. A subset build was started in the background; T3 in mathlib vocabulary is available only if it finishes. The fallback is a **core-Lean-4 T3**: the statement and witness written against definitions unfolded from scratch, checked by kernel reduction with `#print axioms` clean. |
| `elan toolchain install` | same 403 | worked around by unpacking the GitHub release tarball directly into `~/.elan/toolchains/` |
| Gröbner CAS (Singular / Macaulay2 / msolve) | not in the Ubuntu archive set available here | **Class B cannot be closed symbolically.** Ansatz families cannot be decided; class B is therefore attacked only by numeric/enumerative means and cannot ship. |
| SDP solver for SOS certificates | `cvxpy`/`scs` install was not attempted after the class-B decision above | no sum-of-squares certificates; positivity-style problems are out of scope for this run |
| flint / arb interval arithmetic | not installed | not needed: every checker here is exact over the integers and rationals, and the single square root in the corpus (WOWII 100) is handled by exact integer comparison rather than interval arithmetic |

## Deliberate design constraints on the checkers
- **No floating point anywhere.** Counts are `int`, averages are `Fraction`, the one square
  root is compared exactly by squaring. There is no T0 float screen inside the verifier;
  floats appear only in the search-side C screener, whose output is never trusted.
- **Checkers do not import the search tooling.** `mine/tools/graphtool.c` (C, bitmask,
  fast) and `mine/verify/lib/exactgraph.py` (Python, exhaustive, exact) are independent
  implementations. Agreement between them is evidence; neither depends on the other.
- **Crash means REFUSE, never ACCEPT.** An uncaught exception in any checker is converted
  to exit code 2 by a hook in `lib/harness.py`.
- **Exhaustive ceiling.** `exactgraph.MAX_N_EXHAUSTIVE = 22`; a larger witness is refused
  rather than verified approximately.
