#!/usr/bin/env bash
set -euo pipefail

container="${1:-}"
if [[ -z "$container" ]]; then
  echo "Usage: mise run docker:container:shell <container>" >&2
  exit 2
fi

if docker exec "$container" test -x /bin/bash 2>/dev/null; then
  exec docker exec -it "$container" /bin/bash
else
  exec docker exec -it "$container" /bin/sh
fi
