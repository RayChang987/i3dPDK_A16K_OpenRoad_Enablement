# RTL for scripts/syn.sh (read by flow/syn.tcl only). $ORFS_DESIGNS: the ORFS
# designs directory (in the default image: /OpenROAD-flow-scripts/flow/designs).
# cells_clkgate.v: the PDK has no clock-gating cell, so the gate is a wire
set RTL_FILES [list [file join [file dirname [info script]] .. swerv cells_clkgate.v] \
    $ORFS_DESIGNS/src/swerv/swerv_wrapper.sv2v.v $ORFS_DESIGNS/nangate45/swerv/macros.v]
