# Mise Task Authoring Guide

## Short command: TOML

```toml
["system:uptime"]
description = "Show uptime and load averages"
run = "uptime"
```

## Logic: script

Use a script if the task needs:

- arguments
- conditionals
- loops
- OS detection
- multiple API calls
- structured JSON
- substantial shell code

Example:

```toml
["system:pkg:install-core"]
description = "Install the baseline package set"
file = "scripts/bash/install-packages.sh"
```

## Public naming

Use:

```text
category:group:action
```

Examples:

```text
system:logs:errors
network:http:weather
docker:compose:up
dev:ssh:keygen
omarchy:hypr:monitors
```

## Required metadata

Every public task gets:

```toml
description = "..."
```

Add when appropriate:

```toml
alias = "..."
dir = "{{cwd}}"
tools = { python = "3.14" }
env = { MODE = "demo" }
depends = ["..."]
confirm = "..."
timeout = "..."
usage = "..."
```

Use only mise-supported properties. Keep future UI/plugin metadata separate.

## Arguments must be declared

`mise tasks ls --json` reports `args: []` for a task that reads `$1` without a
declared spec, so nothing but a human reading the source can discover its
parameters. Declare them.

In a `file =` script, use `#USAGE` comments:

```bash
#!/usr/bin/env bash
set -euo pipefail

#USAGE arg "<unit>" help="systemd unit name, e.g. sshd"
#USAGE arg "[lines]" help="Number of journal lines to show" default="200"

unit="${1:-}"
lines="${2:-200}"
```

The script keeps its positional `$1`/`$2` and also gains `$usage_unit` and
`$usage_lines` with defaults already applied.

For an inline `run`, use the `usage` property:

```toml
["network:trace"]
description = "Trace route to a host; pass host name or IP"
usage = '''
arg "<host>" help="Host name or IP address to trace a route to"
'''
run = 'traceroute "$usage_host"'
```

**Inline tasks behave differently:** once a `usage` spec exists, mise passes
arguments as `$usage_<name>` **only**. `$1` is empty. This fails silently, so the
validator rejects a `usage` spec combined with `$1`/`$2` in an inline `run`.

Either form gives you real CLI help and a machine-readable parameter list:

```bash
mise system:logs:unit --help
mise tasks info system:logs:unit --json   # usage_spec.cmd.args
```

Mise enforces required arguments before the task body runs, so a manual
`if [[ -z "$1" ]]` check is no longer the primary guard. Keep it in scripts
intended to also run standalone.

## Caller directory versus repository directory

A Compose helper intended to operate on the project you are currently in should use:

```toml
dir = "{{cwd}}"
```

A demo task using files inside this blueprint should run from the blueprint/config root and not set `dir`.

## Destructive actions

Always make destructive behavior obvious and use `confirm`.

Avoid hidden `-f`, `--force`, `--volumes`, recursive deletes, firewall changes or credential changes unless the task name/description clearly says what happens.

## Secrets

Never hard-code:

- GitHub PATs
- passwords
- API tokens
- SSH private keys
- age identities

GitHub PATs are created by GitHub. Prefer `gh auth login` for local CLI workflows.

## Mise-managed tools

Good:

```toml
tools = { python = "3.14" }
```

This keeps Python local to the task's declared environment.

Use system package management for system-integrated applications such as desktop applications and daemon packages when appropriate.

## Validate every change

```bash
mise run dev:blueprint:validate    # syntax, metadata schema, invariants
mise run dev:blueprint:manifest    # refresh MANIFEST.json if the task set changed
mise tasks validate
mise tasks ls
mise tasks info category:new-task
```

`mise run dev:blueprint:ci` runs the whole gate the way CI does. `MANIFEST.json`
is generated -- never hand-edit it.


## Important: `file` path resolution in included TOML

For an included task file such as:

```text
tasks/system/logs.toml
```

mise resolves a relative `file =` path from the project root (the directory containing the root `mise.toml`), **not** from the directory containing the included TOML file.

Therefore this blueprint uses:

```toml
file = "scripts/bash/logs-unit.sh"
```

not:

```toml
file = "../../scripts/bash/logs-unit.sh"
```

Included task files and tasks declared directly in the root `mise.toml` therefore use the identical path. Confirm with:

```bash
mise tasks info system:logs:unit
```

`tools/validate-blueprint.py` enforces this by resolving every `file =` against the project root.
