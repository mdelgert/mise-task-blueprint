#!/usr/bin/env bash
set -euo pipefail

#USAGE arg "[city]" help="City to report weather for" default="Phoenix"

city="${1:-Phoenix}"
encoded="${city// /+}"
curl -fsSL "https://wttr.in/${encoded}?format=3"
printf '\n'
