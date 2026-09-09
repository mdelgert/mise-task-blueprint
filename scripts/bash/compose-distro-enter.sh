#!/usr/bin/env bash
set -euo pipefail

# Bring up a single-service distro Compose file in the background, wait for the
# container to actually be running, then open an interactive shell inside it.
# Backs docker:compose:ubuntu:enter and docker:compose:debian:enter.
#
# The Compose file and the service inside it are both named after the distro,
# e.g. examples/docker-compose/ubuntu/compose.yaml -> service "ubuntu".

distro="${1:-}"
if [[ -z "${distro}" ]]; then
  echo "Usage: compose-distro-enter.sh <ubuntu|debian>" >&2
  exit 2
fi

compose_file="examples/docker-compose/${distro}/compose.yaml"
if [[ ! -f "${compose_file}" ]]; then
  echo "No Compose file for '${distro}': ${compose_file} not found." >&2
  exit 2
fi

compose=(docker compose -f "${compose_file}")

echo "Starting ${distro}..." >&2
"${compose[@]}" up -d

# `up -d` returns once the container is created, which is not quite the same as
# running, so poll briefly before exec'ing in.
cid=""
for _ in {1..20}; do
  cid="$("${compose[@]}" ps -q "${distro}" 2>/dev/null || true)"
  if [[ -n "${cid}" ]] && [[ "$(docker inspect -f '{{.State.Running}}' "${cid}" 2>/dev/null)" == "true" ]]; then
    break
  fi
  cid=""
  sleep 0.5
done

if [[ -z "${cid}" ]]; then
  echo "The ${distro} container did not reach the running state." >&2
  "${compose[@]}" ps >&2
  exit 1
fi

echo "Entering ${distro}. Exit the shell to leave it running in the background." >&2
echo "Stop and remove it with: mise run docker:compose:${distro}:down" >&2

if docker exec "${cid}" test -x /bin/bash 2>/dev/null; then
  exec docker exec -it "${cid}" /bin/bash
else
  exec docker exec -it "${cid}" /bin/sh
fi
