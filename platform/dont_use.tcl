# Cells no step may use, per library; sourced with $lib set (e.g. CFET_4T) by
# flow/syn.tcl (synthesis) and flow/flow.tcl (CTS, timing and design repair).
#   SDFF_X1/X2  scan flops: no test_cell in the liberty, no scan flow.
#   The rest: cells that cause problems later in place and route (no pin
#   access point in TritonRoute, DRT-0073, or a pin with no geometry).
set DONT_USE_CELLS {SDFF_X1 SDFF_X2}
switch -- $lib {
    CFET_4T  { lappend DONT_USE_CELLS NOR2_X4 }
    FSFET_4T { lappend DONT_USE_CELLS AND2_X2 INV_X4 }
    FSFET_5T { lappend DONT_USE_CELLS AOI21_X1 OAI222_X1 XOR2_X1 MUX2_X1 }
    NSFET_5T { lappend DONT_USE_CELLS AOI21_X1 }
}
