# RTL for scripts/syn.sh (read by flow/syn.tcl only). SERV is not in the ORFS
# image: clone it and point SERV_RTL at its rtl/ directory, e.g.
#   git clone https://github.com/olofk/serv && git -C serv checkout f200eb2
#   env SERV_RTL=$PWD/serv/rtl scripts/syn.sh serv CFET_3T
# (the included netlists were synthesized from f200eb2).
if {![info exists ::env(SERV_RTL)]} { error "set SERV_RTL to the rtl/ directory of a SERV checkout (see designs/serv/rtl.tcl)" }
set RTL_FILES [lsort [glob $::env(SERV_RTL)/*.v]]
