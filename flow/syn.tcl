# Yosys synthesis to an i3dPDK_A16K library (run through scripts/syn.sh).
# Env: PDK_ROOT DESIGN LIB OUT_DIR ORFS_DESIGNS [CLK_PERIOD_NS]
# Reads designs/<design>/config.tcl (top, clock, macros) and rtl.tcl (RTL
# files); writes OUT_DIR/<top>.v.gz, the netlist flow.tcl reads.
# The included netlists (designs/<design>/<LIB>/) were made by this script.
yosys -import
set enab   [file normalize [file join [file dirname [info script]] ..]]
set design $::env(DESIGN)
set lib    $::env(LIB)
set out    $::env(OUT_DIR)
set ORFS_DESIGNS $::env(ORFS_DESIGNS)
lassign [split $lib _] arch trk
set lib_file $::env(PDK_ROOT)/FE/$arch/$trk/i3dPDK_A16K_0V7_27C.lib
source $enab/designs/$design/config.tcl
source $enab/designs/$design/rtl.tcl
if {[info exists ::env(CLK_PERIOD_NS)] && $::env(CLK_PERIOD_NS) ne ""} { set CLK_PERIOD_NS $::env(CLK_PERIOD_NS) }
if {![info exists MACROS]} { set MACROS {} }
if {![info exists INCLUDE_DIRS]} { set INCLUDE_DIRS {} }
set macro_libs [lmap m $MACROS {file join $enab/platform/macros $m.lib}]

# dont_use: platform/dont_use.tcl (scan flops, and cells that cause P&R problems);
# DONT_USE (env) adds cells.
source $enab/platform/dont_use.tcl
set dont_use $DONT_USE_CELLS
if {[info exists ::env(DONT_USE)]} { lappend dont_use {*}$::env(DONT_USE) }
set du [concat {*}[lmap c $dont_use {list -dont_use $c}]]

read_liberty -lib $lib_file
foreach ml $macro_libs { read_liberty -lib $ml }
set incs [lmap d $INCLUDE_DIRS {string cat -I $d}]
foreach f $RTL_FILES { read_verilog -defer {*}$incs $f }
hierarchy -check -top $DESIGN_TOP
# Keep every macro: once flattened, a macro whose read data is unused would
# be removed with the logic around it.
foreach m $MACROS { setattr -set keep 1 t:$m }
synth -top $DESIGN_TOP -flatten
opt -purge
# The PDK has no set/reset flops (DFF_X1/X2 only): asynchronous set/reset
# becomes synchronous (it acts at the next clock edge). No-op for sync designs.
async2sync
dfflibmap -liberty $lib_file {*}$du
opt
abc -liberty $lib_file -D [expr {int($CLK_PERIOD_NS * 1000)}] {*}$du
opt_clean -purge
# No TIE cells: constants stay 1'b0/1'b1 (flow.tcl ties them to VSS/VDD).
setundef -zero
# Port-to-port feedthroughs get a buffer instead of an assign.
insbuf -buf BUF_X1 A Z
opt_clean -purge
check -assert
tee -o $out/stat.rpt stat -liberty $lib_file {*}[concat {*}[lmap ml $macro_libs {list -liberty $ml}]]
write_verilog -noattr -noexpr -nohex -nodec $out/${DESIGN_TOP}.v
