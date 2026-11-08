# SERV (bit-serial RV32I), top = serv_synth_wrapper (the register file RAM is
# outside, on the ports). No macros.
set DESIGN_TOP    serv_synth_wrapper
set CLK_PORT      clk
set CLK_PERIOD_NS 0.25
set UTIL          0.6
