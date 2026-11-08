#!/bin/bash
# Run the OpenROAD build in ~/OpenROAD/install (built in the openroad/ubuntu
# dev image; the host lacks its shared libraries) inside that image.
# Usage: openroad.sh [openroad args ...]   (cwd and $HOME are mounted as is)
# Env: OR_NAME (container name), OR_IMAGE (default openroad/ubuntu26.04-dev:47319c), OR_BIN, extra
#      variables to pass in: OR_ENV="DESIGN LIB ..." (names).
set -euo pipefail
img=${OR_IMAGE:-openroad/ubuntu26.04-dev:47319c}
bin=${OR_BIN:-$HOME/OpenROAD/install/bin/openroad}
envs=()
for v in ${OR_ENV:-}; do [ -n "${!v+x}" ] && envs+=(-e "$v"); done
tty=(); [ -t 0 ] && [ -t 1 ] && tty=(-it)
# Named container (OR_NAME, default or_<pid>): stop a run with docker stop <name>.
# A container of that name still there (a stopped run being removed by
# --rm) is waited for, up to 30s; a running one is an error.
name=${OR_NAME:-or_$$}
for i in $(seq 30); do
    docker ps -a -q --filter "name=^/${name}\$" | grep -q . || break
    [ "$i" = 30 ] && { echo "openroad.sh: container $name exists (already running?)" >&2; exit 1; }
    sleep 1
done
exec docker run --rm --init --name "$name" "${tty[@]}" -u "$(id -u):$(id -g)" -e HOME="$HOME" \
     -v "$HOME:$HOME" -w "$PWD" "${envs[@]}" -e QT_QPA_PLATFORM=offscreen \
     "$img" "$bin" "$@"
