#!/usr/bin/env bash
set -euo pipefail

path="${1:-${HOME}/.config/mise-blueprint/age-identity.txt}"
mkdir -p "$(dirname "$path")"
chmod 700 "$(dirname "$path")"

if [[ -e "$path" ]]; then
  echo "Refusing to overwrite existing age identity: $path" >&2
  exit 1
fi

umask 077
age-keygen -o "$path" >/dev/null

echo "Identity saved to: $path"
echo "Public recipient:"
age-keygen -y "$path"
