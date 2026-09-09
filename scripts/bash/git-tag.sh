#!/usr/bin/env bash
set -euo pipefail

#USAGE arg "<tagname>" help="Annotated tag name to create, e.g. v1.2.0"
#USAGE arg "[message]" help="Tag annotation message (defaults to the tag name)"

tagname="${1:?Usage: mise run dev:git:tag <tagname> [message]}"
message="${2:-$tagname}"

git tag -a "$tagname" -m "$message"
echo "Created tag: $tagname"
