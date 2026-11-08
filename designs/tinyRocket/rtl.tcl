# RTL for scripts/syn.sh (read by flow/syn.tcl only). $ORFS_DESIGNS: the ORFS
# designs directory (in the default image: /OpenROAD-flow-scripts/flow/designs).
# SRAMs through the *_ext wrappers of ORFS' nangate45 TinyConfig.v
set RTL_FILES [list \
    $ORFS_DESIGNS/src/tinyRocket/AsyncResetReg.v \
    $ORFS_DESIGNS/src/tinyRocket/ClockDivider2.v \
    $ORFS_DESIGNS/src/tinyRocket/ClockDivider3.v \
    $ORFS_DESIGNS/src/tinyRocket/plusarg_reader.v \
    $ORFS_DESIGNS/src/tinyRocket/freechips.rocketchip.system.TinyConfig.v \
    $ORFS_DESIGNS/nangate45/tinyRocket/freechips.rocketchip.system.TinyConfig.v]
