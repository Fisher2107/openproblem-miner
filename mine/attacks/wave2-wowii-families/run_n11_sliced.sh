#!/usr/bin/env bash
# Exhaustive n=11 over all 1,006,700,565 connected graphs, sliced by edge count so that a
# partial run still yields a quantifiable statement ("all connected graphs on 11 vertices
# with at most k edges") instead of nothing. Cheap arms only.
cd /home/user/openproblem-miner
LOG=mine/attacks/wave2-wowii-families/n11_sweep.log
echo "restart (sliced) $(date -u +%FT%TZ)" >> "$LOG"
for e in $(seq 10 55); do
  out=$(nauty-geng -qc 11 ${e}:${e} 2>/dev/null | ./mine/tools/wowscan --only 100,160,291,133,19,61,141,314 2>&1 | tail -1)
  echo "edges=${e}  ${out}" >> "$LOG"
done
echo "N11 SLICED SWEEP COMPLETE $(date -u +%FT%TZ)" >> "$LOG"
