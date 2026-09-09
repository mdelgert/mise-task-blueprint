#!/usr/bin/env bash
set -euo pipefail

tagname="${1:?Usage: mise run development:git:tag <tagname> [message]}"
message="${2:-$tagname}"

git tag -a "$tagname" -m "$message"
echo "Created tag: $tagname"
