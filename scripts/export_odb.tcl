# Write the DEF and Verilog of an OpenROAD database (e.g. cts.odb, the hand-off
# point of the cross-tool runs). Env: EXP_ODB EXP_DEF EXP_V
read_db $env(EXP_ODB)
write_def $env(EXP_DEF)
write_verilog $env(EXP_V)
