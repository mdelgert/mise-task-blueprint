#!/usr/bin/env bash
set -euo pipefail

# Recipient is derived automatically from the local age identity (same
# default path dev:age:keygen writes to), so callers only pass a filename.
identity="${MISE_AGE_IDENTITY:-${HOME}/.config/mise-blueprint/age-identity.txt}"

input="${1:?Usage: mise run dev:age:encrypt <input> [output]}"
output="${2:-${input}.age}"

if [[ ! -f "$identity" ]]; then
  echo "No age identity found at: $identity" >&2
  echo "Generate one first: mise run dev:age:keygen" >&2
  exit 1
fi

recipient="$(age-keygen -y "$identity")"

age -r "$recipient" -o "$output" "$input"
echo "Encrypted:  $input"
echo "Output:     $output"
echo "Recipient:  $recipient"
