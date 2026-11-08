# Layout snapshot of an OpenROAD database (headless; run with openroad -gui).
#   scripts/openroad.sh -gui -no_init -exit scripts/snapshot.tcl   with env:
#   SNAP_ODB    database to read (e.g. out/serv/CFET_3T/base/route.odb)
#   SNAP_PNG    image to write
#   SNAP_AREA   optional "x1 y1 x2 y2" in um (default: the whole die)
#   SNAP_RES    optional um per pixel (default: SNAP_WIDTH pixels across)
#   SNAP_WIDTH  optional width in pixels (default 1600)
#   SNAP_VIEW   route (default) | place (no signal wires) | pdn (no cells, no
#               signal wires) | congestion (GRT congestion heat map)
#   SNAP_LAYERS optional layers to draw (e.g. "BPR M0 M1 M2 M3"; default all)
proc env_or {name default} { expr {[info exists ::env($name)] ? $::env($name) : $default} }
read_db $::env(SNAP_ODB)
set view [env_or SNAP_VIEW route]
gui::set_display_controls "Misc/Scale bar" visible true
gui::set_display_controls "Tracks/*" visible false
gui::set_display_controls "Misc/Instances/Names" visible false
switch $view {
    place { gui::set_display_controls "Nets/Signal" visible false
            gui::set_display_controls "Nets/Clock" visible false }
    pdn   { gui::set_display_controls "Nets/Signal" visible false
            gui::set_display_controls "Nets/Clock" visible false
            gui::set_display_controls "Instances/*" visible false }
    congestion { gui::set_display_controls "Nets/*" visible false
            gui::set_display_controls "Heat Maps/Routing Congestion" visible true }
}
set layers [env_or SNAP_LAYERS ""]
if {$layers ne ""} {
    gui::set_display_controls "Layers/*" visible false
    foreach l $layers { gui::set_display_controls "Layers/$l" visible true }
}
set args {}
set area [env_or SNAP_AREA ""]
if {$area ne ""} { lappend args -area $area }
set res [env_or SNAP_RES ""]
if {$res ne ""} { lappend args -resolution $res } else { lappend args -width [env_or SNAP_WIDTH 1600] }
save_image {*}$args $::env(SNAP_PNG)
