# Sourced by openroad.sh and syn.sh: the image the tools run in, and how.
#
# Default: the official OpenROAD-flow-scripts image, pinned. It carries
# OpenROAD (with the GUI, for snapshots), Yosys, and the RTL of the ORFS
# benchmark designs (/OpenROAD-flow-scripts/flow/designs/src).
#   OR_IMAGE  image             (default below)
#   OR_BIN    openroad binary   (default: the image's)
#   YOSYS_BIN yosys binary      (default: the image's)
# A local OpenROAD build works too, e.g. one built in its dev image:
#   OR_IMAGE=openroad/ubuntu26.04-dev:<tag> OR_BIN=$HOME/OpenROAD/install/bin/openroad
OR_IMAGE_DEFAULT=openroad/orfs:26Q4-368-g9ca2a9e76
OR_IMAGE=${OR_IMAGE:-$OR_IMAGE_DEFAULT}
OR_BIN=${OR_BIN:-/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad}
YOSYS_BIN=${YOSYS_BIN:-/OpenROAD-flow-scripts/tools/install/yosys/bin/yosys}

# in_image [docker run options --] cmd args...
# Runs cmd in $OR_IMAGE as the calling user, in the current directory. Mounted
# at the same paths: $HOME, this repository, $PDK_ROOT and the current
# directory (whichever are not inside another one), so every path an argument
# or an environment variable holds stays valid in the container.
in_image() {
    local opts=()
    while [ $# -gt 0 ] && [ "$1" != "--" ]; do opts+=("$1"); shift; done
    [ "${1:-}" = "--" ] && shift
    local repo mounts=() d m skip
    repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
    for d in "$HOME" "$repo" ${PDK_ROOT:+"$PDK_ROOT"} "$PWD"; do
        d=$(cd "$d" 2>/dev/null && pwd) || continue
        skip=0
        for m in "${mounts[@]}"; do case "$d/" in "$m"/*) skip=1 ;; esac; done
        [ $skip = 0 ] && mounts+=("$d")
    done
    local vols=()
    for m in "${mounts[@]}"; do vols+=(-v "$m:$m"); done
    local tty=()
    [ -t 0 ] && [ -t 1 ] && tty=(-it)
    # Qt draws offscreen (headless snapshots) unless OR_QT_PLATFORM says
    # otherwise (gui.sh: xcb, a real X display).
    docker run --rm --init "${tty[@]}" -u "$(id -u):$(id -g)" -e HOME="$HOME" \
        "${vols[@]}" -w "$PWD" -e QT_QPA_PLATFORM="${OR_QT_PLATFORM:-offscreen}" "${opts[@]}" "$OR_IMAGE" "$@"
}
