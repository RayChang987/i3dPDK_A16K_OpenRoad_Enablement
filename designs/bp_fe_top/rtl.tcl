# RTL for scripts/syn.sh (read by flow/syn.tcl only). $ORFS_DESIGNS: the ORFS
# designs directory (in the default image: /OpenROAD-flow-scripts/flow/designs).
# SRAMs through ORFS' nangate45 hard_mem wrappers (fakeram45_* in platform/macros)
set RTL_FILES [list $ORFS_DESIGNS/src/bp_fe_top/pickled.v $ORFS_DESIGNS/nangate45/bp_fe_top/macros.v]
