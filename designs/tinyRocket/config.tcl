# tinyRocket (Rocket RV64 tile, TinyConfig) from OpenROAD-flow-scripts, top = RocketTile.
# SRAMs: the I$ and D$ data arrays, fakeram45_64x32 x2.
set DESIGN_TOP    RocketTile
set CLK_PORT      clock
set CLK_PERIOD_NS 1.0
set UTIL          0.6
set MACROS        {fakeram45_64x32}
