# bp_fe_top (BlackParrot front end: fetch, I$, BTB, I-TLB) from OpenROAD-flow-scripts.
# 11 SRAMs through ORFS' hard_mem wrappers: fakeram45_512x64 x9, 64x7, 64x96.
set DESIGN_TOP    bp_fe_top
set CLK_PORT      clk_i
set CLK_PERIOD_NS 1.0
set UTIL          0.5
set MACROS        {fakeram45_512x64 fakeram45_64x7 fakeram45_64x96}
