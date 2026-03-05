#!/usr/bin/env bash

set -euo pipefail

# determine repo root (assumes script is in repo/scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SIM_SRC="$REPO_ROOT/simulations/manet_simulation.cc"
DATA_DIR="$REPO_ROOT/dataset"

NS3_DIR="${NS3_DIR:-$HOME/ns-3-dev}"

mkdir -p "$DATA_DIR"

# copy simulation into ns-3 scratch
cp "$SIM_SRC" "$NS3_DIR/scratch/"

NUM_RUNS=30

for seed in $(seq 1 $NUM_RUNS); do
  echo "=== Run seed=$seed ==="
  cd "$NS3_DIR"
  ./ns3 run "scratch/manet_simulation --RngRun=$seed --outDir=$DATA_DIR --runId=$seed"
done

echo "All runs finished. Flow XML + position/RSSI CSVs should be in $DATA_DIR"