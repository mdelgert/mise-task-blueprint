#!/usr/bin/env bash
set -euo pipefail

#USAGE arg "<input>" help="Encrypted .age file to decrypt"
#USAGE arg "[output]" help="Output path (default: <input> with .age removed)"

# Identity is derived automatically from the same default path dev:age:keygen
# writes to, so callers only pass the encrypted filename.
identity="${MISE_AGE_IDENTITY:-${HOME}/.config/mise-blueprint/age-identity.txt}"

input="${1:?Usage: mise run dev:age:decrypt <input.age> [output]}"
output="${2:-}"

if [[ -z "$output" ]]; then
  if [[ "$input" == *.age ]]; then
    output="${input%.age}"
  else
    # Bug fix: previously this fell back to $input unchanged, which would
    # silently overwrite the encrypted file itself with plaintext.
    output="${input}.decrypted"
  fi
fi

if [[ "$output" == "$input" ]]; then
  echo "Refusing to decrypt $input onto itself; pass an explicit output path" >&2
  exit 1
fi

# `age -o` clobbers an existing file without asking, so decrypting foo.txt.age
# next to a locally edited foo.txt would destroy it. Match the "Refusing to
# overwrite" convention used by age-keygen.sh and ssh-keygen.sh instead.
if [[ -e "$output" ]]; then
  echo "Refusing to overwrite existing file: $output" >&2
  echo "Remove it or pass a different output path." >&2
  exit 1
fi

if [[ ! -f "$identity" ]]; then
  echo "No age identity found at: $identity" >&2
  echo "Generate one first: mise run dev:age:keygen" >&2
  exit 1
fi

age -d -i "$identity" -o "$output" "$input"
echo "Decrypted:  $input"
echo "Output:     $output"
