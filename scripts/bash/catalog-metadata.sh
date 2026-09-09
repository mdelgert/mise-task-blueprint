#!/usr/bin/env bash
set -euo pipefail

root="${MISE_PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Use mise-managed Python so Bash remains just the wrapper/orchestrator.
exec python "$root/scripts/python/catalog_metadata.py" "$@"
