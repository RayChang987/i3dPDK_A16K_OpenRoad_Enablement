# RTL for scripts/syn.sh (read by flow/syn.tcl only). $ORFS_DESIGNS: the ORFS
# designs directory (in the default image: /OpenROAD-flow-scripts/flow/designs).
set RTL_FILES [lsort [glob $ORFS_DESIGNS/src/aes/*.v]]
