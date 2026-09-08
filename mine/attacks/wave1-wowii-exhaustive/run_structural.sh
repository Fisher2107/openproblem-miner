#!/usr/bin/env bash
# Structural exhaustive sweeps: use the conjecture's own hypotheses to shrink the class
# that geng must enumerate, pushing exhaustive coverage well past n=10.
cd /home/user/openproblem-miner
D=mine/attacks/wave1-wowii-exhaustive
{
echo "### conj 141 needs girth >= 6, so enumerating all girth >= 5 graphs is exhaustive for it"
for n in 16 17; do printf "n=%-3s " $n; nauty-geng -qc -tf $n 2>/dev/null | ./mine/tools/wowscan --only 141 2>&1 | tail -1; done
echo "### conj 314 needs triangle-free, so enumerating all triangle-free graphs is exhaustive for it"
for n in 11 12 13; do printf "n=%-3s " $n; nauty-geng -qc -t $n 2>/dev/null | ./mine/tools/wowscan --only 314 2>&1 | tail -1; done
echo "### conj 133/160/100/291 over girth>=5 graphs (cheap arms) at higher n"
for n in 16 17; do printf "n=%-3s " $n; nauty-geng -qc -tf $n 2>/dev/null | ./mine/tools/wowscan --only 133,160,100,291,19,61 2>&1 | tail -1; done
} > "$D/structural_sweeps.log" 2>&1
echo DONE >> "$D/structural_sweeps.log"
