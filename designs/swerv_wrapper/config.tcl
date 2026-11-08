# swerv_wrapper (SweRV EH1 with its memories) from OpenROAD-flow-scripts.
# SRAMs: fakeram45_2048x39 x8, 256x34 x16, 64x21 x4.
set DESIGN_TOP    swerv_wrapper
set CLK_PORT      clk
set CLK_PERIOD_NS 1.0
set UTIL          0.4
set MACROS        {fakeram45_2048x39 fakeram45_256x34 fakeram45_64x21}
