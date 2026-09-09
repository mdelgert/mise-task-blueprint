#!/usr/bin/env bash
set -euo pipefail

# Usage spec so `mise cat --help` documents the positional argument.
# mise also exports it as $usage_category.
#USAGE arg "<category>" help="Task category to list, e.g. system, docker, root"

if [[ $# -lt 1 ]]; then
  echo "Usage: mise cat <category>   (e.g. mise cat system, mise cat root)" >&2
  exit 2
fi

category="$1"

# Root-level tasks (defined in mise.toml rather than tasks/) have no colon in
# their name. menu.sh groups them under the pseudo-category "root", so accept
# that name here too.
if [[ "${category}" == "root" ]]; then
  matches="$(mise tasks ls --name-only | grep -v ':' || true)"
else
  matches="$(mise tasks ls --name-only | grep "^${category}:" || true)"
fi

if [[ -z "${matches}" ]]; then
  echo "No tasks found in category '${category}'." >&2
  echo "Run 'mise menu' to list available categories." >&2
  exit 1
fi

printf '%s\n' "${matches}"
