"""
Target: lit-numbertheory-legendre-weakening-sequence
Source corpus entry: mine/corpus/raw/h6_literature.jsonl (arXiv:2602.22502, "Weakening
the Legendre Conjecture")

Statement (restated exactly, all symbols defined):
  Define the sequence of primes q_1, q_2, q_3, ... by q_1 = 2, and for n >= 1,
  q_(n+1) := the least prime strictly exceeding q_n^2.
  Conjecture: q_(n+1) < (q_n + 1)^2 for all n >= 1.

This is EXACT integer arithmetic (sympy.nextprime), no floats. A counterexample is a
single n with q_(n+1) >= (q_n+1)^2, i.e. sympy.nextprime(q_n**2) >= (q_n+1)**2.

NOTE: q_n grows doubly-exponentially (q_1=2, q_2=5, q_3=~26, q_4=~677, q_5=~458330,
q_6 ~ 2.1e11, q_7 ~ 4.4e22, ...). nextprime on a ~23-digit number (q_7's input q_6^2)
is still fast with sympy's Miller-Rabin+BPSW primality test; q_8 needs nextprime on a
~45-digit number, still fast (sub-second to a few seconds); q_9 needs nextprime on a
~90-digit number -- sympy nextprime does trial division + Miller-Rabin, which stays fast
even at that size since we only need ONE prime above q_n^2, not a full sieve.
"""
import time
from sympy import nextprime, isprime

def q_sequence(n_terms):
    qs = [2]
    for _ in range(n_terms - 1):
        qs.append(nextprime(qs[-1] ** 2))
    return qs

if __name__ == "__main__":
    N = 12
    t0 = time.time()
    qs = q_sequence(N)
    counterexample = None
    for n in range(1, len(qs)):
        qn = qs[n - 1]
        qn1 = qs[n]
        lhs = qn1
        rhs = (qn + 1) ** 2
        ok = lhs < rhs
        print(f"n={n}: q_n={qn} ({len(str(qn))} digits)  q_(n+1)={qn1} ({len(str(qn1))} digits)  "
              f"(q_n+1)^2={rhs}  holds={ok}")
        if not ok:
            counterexample = (n, qn, qn1, rhs)
    t1 = time.time()
    print(f"\nchecked n=1..{len(qs)-1}, wall={t1-t0:.2f}s")
    if counterexample:
        n, qn, qn1, rhs = counterexample
        print(f"COUNTEREXAMPLE at n={n}: q_(n+1)={qn1} >= (q_n+1)^2={rhs}")
    else:
        print(f"NO COUNTEREXAMPLE found for n=1..{len(qs)-1} (conjecture holds on this finite range)")
