#!/usr/bin/env bash
# Simulated annealing (post-positive-control-fix) across all ten open conjectures,
# n = 11..14. Bandit-style: every arm gets the same budget, and the log records the best
# objective each reached so flat arms are visible.
cd /home/user/openproblem-miner
OUT=mine/attacks/wave2-wowii-families/climb_results.log
: > "$OUT"
for conj in 19 40 61 100 133 141 160 198 291 314; do
  for n in 11 12 13 14; do
    ./mine/tools/wowclimb $conj $n 25 20000 $((conj*100+n)) 2>&1 >/dev/null | tail -1 >> "$OUT"
  done
done
echo "CLIMB DONE $(date -u +%FT%TZ)" >> "$OUT"
