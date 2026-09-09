#!/usr/bin/env bash
set -euo pipefail

container="${1:-}"
lines="${2:-200}"

if [[ -z "$container" ]]; then
  echo "Usage: mise run docker:container:logs <container> [lines]" >&2
  exit 2
fi

docker logs --tail "$lines" "$container"
