# Front-side PDN (sourced by flow.tcl), built with pdngen:
#  - M8/M9 core ring in the core margin (width 0.10, spacing 0.06, offset 0.06 um)
#  - BPR follow-pin rails, extended to the ring, BPR->M9 via stacks on the
#    ring only (outside the core: inside, the stack pads would hit the dense
#    M1 pins)
#  - M3 VDD/VSS stripe pairs every PG_M3_PITCH_UM (width and VDD-VSS gap
#    PG_M3_WIDTH_UM), tied to every rail they cross by BPR->M3 stacks
#    (PG_M3_PITCH_UM 0: none)
set_voltage_domain -name CORE -power VDD -ground VSS
define_pdn_grid -name core_grid -voltage_domains CORE
add_pdn_ring -grid core_grid -layers {M8 M9} -widths 0.10 -spacings 0.06 -core_offsets 0.06
add_pdn_stripe -grid core_grid -layer $rail_layer -width $rail_w -followpins -extend_to_core_ring
add_pdn_connect -grid core_grid -layers [list $rail_layer M9]
if {$m3_pitch_um > 0} {
    add_pdn_stripe -grid core_grid -layer M3 -width $m3_width_um -spacing $m3_width_um \
        -pitch $m3_pitch_um -offset [expr {$m3_pitch_um / 2}]
    add_pdn_connect -grid core_grid -layers [list $rail_layer M3]
}
if {[llength $blocks]} {
    # Macro PG (fakeram: VDD/VSS straps on M5). pdngen keeps a macro grid's
    # straps within the macro + halo, so they cannot reach the ring on their
    # own. Instead the core grid
    # gets M8 VDD/VSS stripe pairs every PG_MACRO_PITCH_UM (default 3um, below
    # the shortest macro, fakeram45_64x7 at 3.24um) tied to the M9 sides of
    # the ring, and each macro's M5 straps are stacked up to the M8 stripes
    # crossing it. Over the standard cells the M8 stripes connect to nothing
    # below (no M3->M8 stacks among the cells).
    add_pdn_stripe -grid core_grid -layer M8 -width 0.10 -spacing 0.10 \
        -pitch [design_param PG_MACRO_PITCH_UM 3.0] -offset 1.0 -extend_to_core_ring
    add_pdn_connect -grid core_grid -layers {M8 M9}
    define_pdn_grid -name macro_grid -voltage_domains CORE -macro -cells $MACROS \
        -halo [lrepeat 4 $halo_um]
    add_pdn_connect -grid macro_grid -layers {M5 M8}
}
pdngen
