#!/bin/bash
# Synthesize one design for one library with Yosys (flow/syn.tcl), in the
# same image as OpenROAD (see docker_env.sh).
# Usage: [env VAR=value ...] syn.sh <design> <LIB> [clk_period_ns]
#   <design>: designs/<design>/ (config.tcl + rtl.tcl)
#   <LIB>:    NSFET_5T FSFET_5T FSFET_4T CFET_4T CFET_3T
# Output: out/<design>/<LIB>/syn/<top>.v.gz (+ stat.rpt, yosys.log). run_or.sh
# uses it when designs/<design>/<LIB>/ has no included netlist; otherwise pass
# NETLIST=<that file>.
# Env: PDK_ROOT (default: the parent directory), ORFS_DESIGNS (RTL of the ORFS
#      designs; default: the image's), SERV_RTL (serv only, see its rtl.tcl).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
enab=$(cd "$here/.." && pwd)
. "$here/docker_env.sh"
pdk=$(cd "${PDK_ROOT:-$enab/..}" && pwd)
[ -d "$pdk/FE" ] || { echo "syn.sh: no FE/ in $pdk; set PDK_ROOT to the i3dPDK_A16K checkout" >&2; exit 2; }
[ $# -ge 2 ] || { sed -n '2,12p' "$0"; exit 2; }
design=$1; lib=$2
[ -f "$enab/designs/$design/rtl.tcl" ] || { echo "syn.sh: no designs/$design/rtl.tcl" >&2; exit 2; }
[ $# -ge 3 ] && export CLK_PERIOD_NS=$3
out=$enab/out/$design/$lib/syn
mkdir -p "$out"
export PDK_ROOT=$pdk DESIGN=$design LIB=$lib OUT_DIR=$out
export ORFS_DESIGNS=${ORFS_DESIGNS:-/OpenROAD-flow-scripts/flow/designs}
envs=(-e PDK_ROOT -e DESIGN -e LIB -e OUT_DIR -e ORFS_DESIGNS)
for v in CLK_PERIOD_NS SERV_RTL DONT_USE; do [ -n "${!v:-}" ] && envs+=(-e "$v"); done
echo "yosys: $design $lib -> $out (log yosys.log)"
if ! in_image "${envs[@]}" -- "$YOSYS_BIN" -c "$enab/flow/syn.tcl" > "$out/yosys.log" 2>&1; then
    grep -m5 -E 'ERROR|Error' "$out/yosys.log" || tail -20 "$out/yosys.log"
    echo "FAILED: $out/yosys.log"; exit 1
fi
top=$(grep -m1 -oE '^set DESIGN_TOP +[^ ]+' "$enab/designs/$design/config.tcl" | awk '{print $3}')
gzip -f "$out/$top.v"
grep -E 'Chip area|cells$' "$out/stat.rpt" | head -3
echo "netlist: $out/$top.v.gz"
if [ -f "$enab/designs/$design/$lib/$top.v.gz" ]; then
    echo "(an included netlist exists; to use this one: env NETLIST=$out/$top.v.gz scripts/run_or.sh $design $lib)"
fi
