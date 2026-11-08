#!/bin/bash
# Run an OpenROAD-flow-scripts reference design on one of its platforms, in the
# same image as this flow (docker_env.sh), for the technology roadmap
# (scripts/roadmap.py). Results: out/_orfs/<platform>_<design>/ (+ .log).
# Usage: [NUM_CORES=n] orfs_ref.sh <platform> <design>   e.g. orfs_ref.sh gt2n aes
#   platforms in the image: asap7 nangate45 sky130hd gf180 ihp-sg13g2 gt2n ...
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
. "$here/docker_env.sh"
[ $# -eq 2 ] || { sed -n '2,7p' "$0"; exit 2; }
p=$1; d=$2
w=$(cd "$here/.." && pwd)/out/_orfs/${p}_$d
mkdir -p "$w"
in_image -e WORK_HOME="$w" -- bash -c \
    "cd /OpenROAD-flow-scripts/flow && make DESIGN_CONFIG=designs/$p/$d/config.mk NUM_CORES=${NUM_CORES:-4}" > "$w.log" 2>&1
echo "$p $d: done ($w.log)"
