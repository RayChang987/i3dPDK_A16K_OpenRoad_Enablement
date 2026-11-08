#!/bin/bash
# Open a database in OpenROAD's viewer, in its docker image (docker_env.sh).
# Usage: [GUI=web|x11] [WEB_PORT=8765] gui.sh <file.odb>
#        e.g. scripts/gui.sh out/serv/NSFET_5T/fx4/route.odb
# GUI=web (default): OpenROAD's web viewer (openroad -web). It listens on this
#   host's 127.0.0.1 only and needs the token in the printed url. From your
#   own machine, forward the port first (VS Code: Ports > Forward a Port, or
#   ssh -L 8765:localhost:8765 <host>), then open the url. Ctrl-C stops it.
# GUI=x11: the Qt GUI on an X display. Needs an X server where you sit (Linux
#   desktop, XQuartz, MobaXterm, VcXsrv) and `ssh -X`/-Y into this host.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
. "$here/docker_env.sh"
[ $# -eq 1 ] && [ -f "$1" ] || { sed -n '2,11p' "$0"; exit 2; }
odb=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
case ${GUI:-web} in
  web)
    # --network host: the container's 127.0.0.1 is the host's, so the
    # viewer stays local to this machine.
    in_image --network host --name "or_web_$$" -- \
        "$OR_BIN" -web -web_port "${WEB_PORT:-8765}" -web_no_browser -no_init -db "$odb" ;;
  x11)
    [ -n "${DISPLAY:-}" ] || { echo "gui.sh: DISPLAY is not set (ssh -X, or GUI=web)" >&2; exit 2; }
    export OR_QT_PLATFORM=xcb
    xauth=${XAUTHORITY:-$HOME/.Xauthority}
    opts=(--network host -e DISPLAY="$DISPLAY")
    [ -f "$xauth" ] && opts+=(-v "$xauth:/tmp/.Xauthority:ro" -e XAUTHORITY=/tmp/.Xauthority)
    [ -d /tmp/.X11-unix ] && opts+=(-v /tmp/.X11-unix:/tmp/.X11-unix)
    in_image "${opts[@]}" --name "or_gui_$$" -- "$OR_BIN" -gui -no_init -db "$odb" ;;
  *) echo "gui.sh: GUI must be web or x11" >&2; exit 2 ;;
esac
