# riscv32i (single-cycle RV32I) from OpenROAD-flow-scripts, top = riscv_top.
# Data memory: 4x fakeram7_256x32 (platform/macros, an abstract model).
set DESIGN_TOP    riscv_top
set CLK_PORT      clk
set CLK_PERIOD_NS 1.0
set UTIL          0.6
set MACROS        {fakeram7_256x32}
set MIN_CHANNEL_UM 10.0
