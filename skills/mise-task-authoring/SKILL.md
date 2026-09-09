---
name: mise-task-authoring
description: Create safe, discoverable mise tasks following this repository's flagship pattern.
---

# Mise Task Authoring

## Goal

Maintain a CLI-first mise task catalog that remains suitable for a future UI without depending on that UI.

Every task must be describable to a machine, not just runnable by a human. See `docs/PLUGIN-CONTRACT.md`.

## Required task shape

```toml
["category:group:action"]
description = "Clear user-facing description"
run = "command"
```

Keep the public task name explicit even when the TOML file is inside a category folder.

## TOML or script?

Use TOML for a short command.

Use `file = "scripts/..."` for:
- arguments
- branches
- loops
- OS detection
- structured output
- more than a few shell statements

## Supported metadata

Use mise-native properties only, including when appropriate:

- `description`
- `alias`
- `depends`
- `depends_post`
- `wait_for`
- `env`
- `vars`
- `tools`
- `dir`
- `hide`
- `confirm`
- `raw`
- `raw_args`
- `interactive`
- `sources`
- `outputs`
- `timeout`
- `quiet`
- `silent`
- `run`
- `file`
- `usage`

Do not invent plugin metadata inside the mise task table.

## Arguments must be declared

A task that reads arguments MUST declare them, or no UI can render inputs for it
and `mise <task> --help` documents nothing. The validator enforces this.

For a `file =` script, add `#USAGE` comment lines:

```bash
#!/usr/bin/env bash
set -euo pipefail

#USAGE arg "<container>" help="Container name or ID"
#USAGE arg "[lines]" help="Number of log lines to show" default="200"

container="${1:-}"
lines="${2:-200}"
```

Scripts still receive positional `$1`, `$2`, and additionally get `$usage_container`,
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

**Critical difference:** with a `usage` spec on an inline `run`, mise passes
arguments as `$usage_<name>` **only** — `$1` and `$2` are empty. Reading `$1`
there silently yields an empty string. The validator rejects that combination.

Declared required args are enforced by mise before the task body runs, so a
manual `if [[ -z "$1" ]]` guard is no longer the primary check. Keep such guards
in scripts that are also meant to run standalone.

## Safety

Never silently:
- delete user data
- prune volumes
- expose secrets
- overwrite keys
- weaken SSH/firewall settings
- download and execute untrusted content

Add `confirm` to destructive actions.

`confirm` is invisible to every `mise --json` output, so a task carrying it MUST
also set `requires_confirm = true` in its sidecar. That flag is the only thing a
UI can see. The validator enforces both directions.

## Runtime dependencies

Use mise `tools` when a task needs a specific developer tool/runtime:

```toml
tools = { python = "3.14" }
```

Note that this means the task runs under mise's interpreter, not the system one.
Packages must be installed into that same interpreter.

Pin the version. `"latest"` is rejected by the validator: `lockfile = true`
records only the root `[tools]` table, so a task-scoped `"latest"` is genuinely
unpinned and will drift between machines.

```toml
tools = { jq = "1" }        # good
tools = { jq = "latest" }   # rejected
```

Only declare tools mise can actually provide. `curl` is not in mise's registry,
so declaring it emits a warning on every run and silently falls back to the
system binary. Ubiquitous system utilities belong to the OS package manager.

## Validation

After every task change:

```bash
mise run dev:blueprint:validate    # syntax, metadata schema, invariants
mise run dev:blueprint:manifest    # refresh MANIFEST.json if counts changed
mise tasks validate
mise tasks ls
mise tasks info <task>
```

`mise run dev:blueprint:ci` runs the whole gate the way CI does.

## Categories

Prefer these existing top-level categories:

- `system`
- `network`
- `docker`
- `dev`
- `omarchy`
- `ai`

Create a new category only when none of these fits. The sidecar's `category`
field must equal the task name's prefix; the validator checks this.

Personal or machine-specific shortcuts do not belong in `tasks/`. Put them in
`examples/overlays/` for users to copy into their own config.

## Scope

Do not add plugin or GUI code. This blueprint exists to prove the mise workflow
itself and to publish a stable contract a plugin can consume.

## Custom catalog metadata

Every new task in an included `*.toml` file MUST have a matching entry in the
adjacent `*.meta.toml` sidecar, with every required field present.

Example task:

```toml
["docker:ps"]
description = "List running Docker containers"
run = "docker ps"
```

Matching sidecar:

```toml
[_.tasks."docker:ps"]
icon = "container"
risk = "low"
enabled = true
tags = ["docker", "ps"]
category = "docker"
destructive = false
requires_confirm = false
requires_sudo = false
interactive = false
cwd_scope = "project"
```

All ten fields are required. Four of them are **derived from the task** and must
agree with it — the validator fails the build otherwise:

| Field              | Must equal                                      |
| ------------------ | ----------------------------------------------- |
| `category`         | the task name's prefix, or `root`               |
| `requires_confirm` | whether the task has `confirm`                  |
| `interactive`      | whether the task has `raw` or `interactive`     |
| `cwd_scope`        | `caller` if `dir = "{{cwd}}"`, else `project`   |

Plus: `destructive = true` requires `requires_confirm = true` and `risk = "high"`;
`requires_sudo = true` cannot be `risk = "low"`.

Metadata remains open-ended — additional fields are allowed and expected as the
product model evolves. Document new fields in `docs/CUSTOM-METADATA.md` before
they become widespread.

Do not put arbitrary fields directly inside a mise task table.

After changes validate both the executable task files and the metadata mapping.
