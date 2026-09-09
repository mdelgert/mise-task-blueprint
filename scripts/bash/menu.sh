#!/usr/bin/env bash
set -euo pipefail

# Derive categories dynamically from the live task list instead of
# hard-coding them, so this stays correct as tasks are added/removed.
# Root-level tasks (no colon in the name, e.g. "menu", "by-category")
# are grouped under "root".
categories="$(
  mise tasks ls --name-only \
    | awk -F: 'NF>1{print $1} NF==1{print "root"}' \
    | sort -u \
    | paste -sd, - \
    | sed 's/,/, /g'
)"

echo "Categories: ${categories}"
echo "See tasks in a category: mise cat <category>   (e.g. mise cat system)"
echo "See every task:          mise tasks ls"
