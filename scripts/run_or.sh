#!/bin/bash
# OpenROAD PnR run for i3dPDK_A16K.
# Usage: [env VAR=value ...] run_or.sh <design> <LIB> [clk_period_ns]
#   <design>: designs/<design>/config.tcl, netlist designs/<design>/<LIB>/<top>.v.gz
#   <LIB>:    NSFET_5T FSFET_5T FSFET_4T CFET_4T CFET_3T
# Output: out/<design>/<LIB>/<OUT_TAG, default base>/
# Parameters (env, override the design config; see flow/flow.tcl): see PARAMS.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
enab=$(cd "$here/.." && pwd)
# PDK_ROOT: the i3dPDK_A16K checkout (FE/ liberty); default the parent directory
pdk=$(cd "${PDK_ROOT:-$enab/..}" && pwd)
[ -d "$pdk/FE" ] || { echo "run_or.sh: no FE/ in $pdk; set PDK_ROOT to the i3dPDK_A16K checkout" >&2; exit 2; }
[ $# -ge 2 ] || { sed -n '2,8p' "$0"; exit 2; }
design=$1; lib=$2
[ $# -ge 3 ] && export CLK_PERIOD_NS=$3
tag=${OUT_TAG:-base}; tag=${tag#_}
out=$enab/out/$design/$lib/$tag
mkdir -p "$out"
export PDK_ROOT=$pdk DESIGN=$design LIB=$lib OUT_DIR=$out RUN_STARTED=$(date -Iseconds)
PARAMS="CLK_PERIOD_NS UTIL PLACE_DENSITY CORE_MARGIN_UM IO_PIN_LAYERS IO_PIN_TRACKS
        MACRO_HALO_UM MIN_CHANNEL_UM MPL_CHANNEL_UM MACRO_AREA_SLACK
        PG_M3_PITCH_UM PG_M3_WIDTH_UM SIGNAL_TOP_LAYER CLOCK_LAYERS ROUTE_UNIDIR PIN_ALIGNED_TRACKS TECH_LEF
        GPL_TIMING GPL_ROUTABILITY GRT_ADJUST GRT_ADJUST_M23 DRT_END_ITER REPAIR_TIMING REPAIR_MAX_BUFFER_PCT
        PG_CHECK_ABORT MIN_ROW_UM PG_MACRO_PITCH_UM CELL_PAD_SITES THREADS STOP_AFTER NETLIST PLACED_DEF SIGNAL_BOTTOM_LAYER"
export OR_ENV="PDK_ROOT DESIGN LIB OUT_DIR RUN_STARTED $(echo $PARAMS)"
git -C "$enab" rev-parse --short HEAD > "$out/flow_version" 2>/dev/null || echo unknown > "$out/flow_version"
[ -n "$(git -C "$enab" status --porcelain 2>/dev/null)" ] && sed -i 's/$/-dirty/' "$out/flow_version"
rm -f "$out/metrics.json"
start=$(date +%s)
export OR_NAME=or_${design}_${lib}_${tag}
echo "container $OR_NAME, log $out/openroad.log"
set +e
(cd "$out" && "$here/openroad.sh" -no_init -exit "$enab/flow/flow.tcl") > "$out/openroad.log" 2>&1
rc=$?
set -e
echo "runtime_s $(( $(date +%s) - start ))" >> "$out/flow_version"
# Success = exit 0 and metrics.json written by finish_run (an [ERROR line
# alone is not a failure: the PG check catches PSM errors it tolerates).
if [ $rc -ne 0 ] || [ ! -f "$out/metrics.json" ]; then
    grep -m5 -E '^\[ERROR|^Error' "$out/openroad.log" || tail -20 "$out/openroad.log"
    echo "FAILED: $out/openroad.log"; exit 1
fi
# Routed wirelength: DRT's last "Total wire length = N um" (odb's
# dbWire::getLength is not usable from Tcl).
python3 - "$out" <<'PY'
import json, re, sys, pathlib
d = pathlib.Path(sys.argv[1])
wl = re.findall(r"Total wire length = ([\d.]+) um", (d / "openroad.log").read_text())
m = json.loads((d / "metrics.json").read_text())
if wl and m.get("stage") == "route":
    m["wirelength_um"] = float(wl[-1])
    (d / "metrics.json").write_text(json.dumps(m, indent=2) + "\n")
    with open(d / "rpt" / "summary.txt", "a") as f:
        f.write("%-20s %s\n" % ("wirelength_um", wl[-1]))
PY
cat "$out/rpt/summary.txt"
echo "done: $out ($(( $(date +%s) - start )) s)"
