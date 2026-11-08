#!/bin/bash
# Run OpenROAD in its docker image (see docker_env.sh: the official ORFS image
# by default, or OR_IMAGE / OR_BIN for a local build).
# Usage: openroad.sh [openroad args ...]
# Env: OR_NAME (container name), extra variables to pass in: OR_ENV="DESIGN LIB ..." (names).
set -euo pipefail
. "$(dirname "$0")/docker_env.sh"
envs=()
for v in ${OR_ENV:-}; do [ -n "${!v+x}" ] && envs+=(-e "$v"); done
# Named container (OR_NAME, default or_<pid>): stop a run with docker stop <name>.
# A container of that name still there (a stopped run being removed by
# --rm) is waited for, up to 30s; a running one is an error.
name=${OR_NAME:-or_$$}
for i in $(seq 30); do
    docker ps -a -q --filter "name=^/${name}\$" | grep -q . || break
    [ "$i" = 30 ] && { echo "openroad.sh: container $name exists (already running?)" >&2; exit 1; }
    sleep 1
done
in_image --name "$name" "${envs[@]}" -- "$OR_BIN" "$@"
