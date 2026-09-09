#!/usr/bin/env bash
set -euo pipefail

#USAGE arg "<unit>" help="systemd unit name, e.g. sshd or NetworkManager"
#USAGE arg "[lines]" help="Number of journal lines to show" default="200"

unit="${1:-}"
lines="${2:-200}"

if [[ -z "$unit" ]]; then
  echo "Usage: mise run system:logs:unit <systemd-unit> [lines]" >&2
  echo "Example: mise run system:logs:unit sshd 100" >&2
  exit 2
fi

journalctl -u "$unit" --no-pager -n "$lines"
