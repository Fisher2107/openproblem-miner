#!/usr/bin/env bash
# Exhaustive n=11 over ALL 1,006,700,565 connected graphs, cheap arms only.
# n=11 is where the first published WOWII counterexample lives, so it is the single
# highest-value range left after the n<=10 sweep.
cd /home/user/openproblem-miner
D=mine/attacks/wave2-wowii-families
echo "start $(date -u +%FT%TZ)" > $D/n11_sweep.log
nauty-geng -qc 11 2>/dev/null | ./mine/tools/wowscan --only 100,160,291,133,19,61,141,314 >> $D/n11_sweep.log 2>&1
echo "end $(date -u +%FT%TZ)" >> $D/n11_sweep.log
