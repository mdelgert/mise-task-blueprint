#!/usr/bin/env bash
set -euo pipefail

city="${1:-Phoenix}"
encoded="${city// /+}"
curl -fsSL "https://wttr.in/${encoded}?format=3"
printf '\n'
