#!/usr/bin/env bash
set -euo pipefail

category="${1:?Usage: mise run dev:tasks:by-category <category>}"

mise tasks ls --name-only | grep "^${category}:"
