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

# Filter the normal `mise tasks ls` table rather than --name-only, so each row
# keeps its description. Matching is on the first column only, since a
# description may itself contain a colon.
#
# Root-level tasks (defined in mise.toml rather than tasks/) have no colon in
# their name. menu.sh groups them under the pseudo-category "root", so accept
# that name here too.
matches="$(
  mise tasks ls --no-header | awk -v category="${category}" '
    category == "root" { if ($1 !~ /:/) print; next }
    index($1, category ":") == 1 { print }
  '
)"

if [[ -z "${matches}" ]]; then
  echo "No tasks found in category '${category}'." >&2
  echo "Run 'mise menu' to list available categories." >&2
  exit 1
fi

printf '%s\n' "${matches}"
