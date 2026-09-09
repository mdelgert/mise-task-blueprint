#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null || {
  echo "jq is required" >&2
  exit 1
}

tasks_json="$(mise tasks --json)"
metadata_toml="$(mise config get _.tasks 2>/dev/null || true)"

metadata_json='{}'
current_task=''

while IFS= read -r line; do
  # Ignore blank lines and comments
  [[ -z "${line//[[:space:]]/}" ]] && continue
  [[ "$line" =~ ^[[:space:]]*# ]] && continue

  # [hello]
  if [[ "$line" =~ ^\[([^]]+)\]$ ]]; then
    current_task="${BASH_REMATCH[1]}"

    metadata_json="$(
      jq \
        --arg task "$current_task" \
        '. + {($task): {}}' \
        <<<"$metadata_json"
    )"

    continue
  fi

  [[ -z "$current_task" ]] && continue

  # key = value
  if [[ "$line" =~ ^[[:space:]]*([^=[:space:]]+)[[:space:]]*=[[:space:]]*(.*)$ ]]; then
    key="${BASH_REMATCH[1]}"
    value="${BASH_REMATCH[2]}"

    # Let jq parse TOML-compatible primitive values:
    # strings, numbers, booleans, arrays.
    parsed="$(
      jq -cn \
        --arg value "$value" '
          $value
          | if test("^\".*\"$") then
              fromjson
            elif . == "true" then
              true
            elif . == "false" then
              false
            elif test("^-?[0-9]+(\\.[0-9]+)?$") then
              tonumber
            elif test("^\\[.*\\]$") then
              fromjson
            else
              .
            end
        '
    )"

    metadata_json="$(
      jq \
        --arg task "$current_task" \
        --arg key "$key" \
        --argjson value "$parsed" \
        '.[$task][$key] = $value' \
        <<<"$metadata_json"
    )"
  fi
done <<<"$metadata_toml"

jq \
  --argjson metadata "$metadata_json" '
    map(
      . as $task
      | . + {
          metadata: ($metadata[$task.name] // {})
        }
    )
  ' <<<"$tasks_json"