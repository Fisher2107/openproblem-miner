# What the frozen verifier can and cannot check

15 checkers. Each reads a witness JSON and exits 0 (ACCEPT: genuine counterexample /
valid certificate), 1 (REJECT), or 2 (REFUSE: malformed, oversized, or convention-dependent).

## Class A — WOWII / Graffiti.pc graph conjectures, all `@[category research open]`
| checker | conjecture | counterexample shape |
|---|---|---|
| `check_wow2_19.py`   | floor(avg_ecc + max l(v)) <= b(G) | connected, n>=2, floor(avg_ecc+maxL) > b |
| `check_wow2_40.py`   | ceil((p(G)+b(G)+1)/2) <= f(G) | connected, n>=2, ceil(...) > f |
| `check_wow2_61.py`   | residue(G) + ceil(diam/3) <= f(G) | connected, lhs > f |
| `check_wow2_100.py`  | alpha <= ceil((max l(v) + ||deg(G^c)||_2 / 2)/2) | connected, alpha > rhs |
| `check_wow2_133.py`  | rad + floor(l_avg)^cC4 <= path(G) | connected, lhs > largest induced path |
| `check_wow2_141.py`  | floor(girth/2) - 1 + max l(v) <= tree(G) | connected WITH a cycle, lhs > tree |
| `check_wow2_160.py`  | max l(v) + max T(v) * cC4 <= Ls(G) | connected, lhs > Ls |
| `check_wow2_198a.py` | b <= 2 + avg_ecc  =>  Hamiltonian path | hypothesis holds, no Hamiltonian path |
| `check_wow2_291.py`  | gamma_t <= k(G) + freq_min_T | connected, n>2, gamma_t > rhs |
| `check_wow2_314.py`  | triangle-free and induced path <= 4 => well totally dominated | hypotheses hold, two minimal TDS of different sizes |

## Test material only — conjectures already refuted in the literature
| checker | why it exists |
|---|---|
| `check_wow2_194.py` | exercises the ACCEPT path end-to-end on the published 18-vertex counterexample |
| `check_wow2_200.py` | same, on the published 11-vertex counterexample `J??FFBRq}N_` |

Nothing these two accept is a new result. They exist because a verifier whose accept path
has never fired is not a validated verifier.

## Class C — bound-record certificates
| checker | certifies |
|---|---|
| `check_ramsey_lower.py` | a graph on n vertices with no K_s and no independent t-set, so R(s,t) > n |
| `check_vdw_lower.py`    | an r-colouring of [1,n] with no monochromatic k-AP, so W(k,r) > n |
| `check_schur_lower.py`  | an r-colouring of [1,n] with no monochromatic x+y=z, so S(r) >= n |

These accept a certificate; whether it BEATS the published record is printed as a note and
is a human judgement, not a checker verdict.

## What this verifier CANNOT check, and therefore what this run cannot ship
- Anything in **Class B**: no Gröbner/CAS or SDP is installed, so no symbolic certificate
  for a parametric family can be closed.
- Any conjecture whose witness needs more than 22 vertices for the exhaustive invariants
  (`MAX_N_EXHAUSTIVE`), or more than 16 for the path cover number.
- Anything harvested after the freeze. The ordering constraint is deliberate: a checker
  written after seeing a candidate is not a checker, it is a rationalisation.
