# bp_be_top (BlackParrot back end) from OpenROAD-flow-scripts.
# SRAMs through ORFS' hard_mem wrappers: fakeram45_512x64 x8, 64x15, 64x96.
set DESIGN_TOP    bp_be_top
set CLK_PORT      clk_i
set CLK_PERIOD_NS 1.0
set UTIL          0.6
set MACROS        {fakeram45_512x64 fakeram45_64x15 fakeram45_64x96}
