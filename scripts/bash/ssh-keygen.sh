#!/usr/bin/env bash
set -euo pipefail

#USAGE arg "[path]" help="Output key path (default: ~/.ssh/id_ed25519_mise_example)"

default_path="${HOME}/.ssh/id_ed25519_mise_example"
path="${1:-$default_path}"

mkdir -p "$(dirname "$path")"
chmod 700 "$(dirname "$path")"

if [[ -e "$path" || -e "${path}.pub" ]]; then
  echo "Refusing to overwrite existing key material: $path" >&2
  exit 1
fi

comment="${USER:-user}@$(hostname)-mise"
ssh-keygen -t ed25519 -a 100 -f "$path" -C "$comment"

echo
echo "Private key: $path"
echo "Public key:  ${path}.pub"
echo
echo "Public key:"
cat "${path}.pub"
