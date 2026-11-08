# ethmac (OpenCores Ethernet MAC) from OpenROAD-flow-scripts. No macros.
# Only the Wishbone clock wb_clk_i is constrained (the MII clocks are not).
set DESIGN_TOP    ethmac
set CLK_PORT      wb_clk_i
set CLK_PERIOD_NS 1.0
set UTIL          0.6
