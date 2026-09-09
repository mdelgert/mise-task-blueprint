---
name: mise-task-authoring
description: Create safe, discoverable mise tasks following this repository's flagship pattern.
---

# Mise Task Authoring

## Goal

Maintain a CLI-first mise task catalog that remains suitable for a future UI without depending on that UI.

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

Do not invent plugin metadata inside the mise task table.

## Safety

Never silently:
- delete user data
- prune volumes
- expose secrets
- overwrite keys
- weaken SSH/firewall settings
- download and execute untrusted content

Add `confirm` to destructive actions.

## Runtime dependencies

Use mise `tools` when a task needs a specific developer tool/runtime:

```toml
tools = { python = "3.14" }
```

## Validation

After every task change:

```bash
python tools/validate-blueprint.py
mise tasks validate
mise tasks ls
mise tasks info <task>
```

## Categories

Prefer these existing top-level categories:

- `system`
- `network`
- `docker`
- `development`
- `omarchy`

Create a new category only when none of these fits.

## Scope

Do not add plugin or GUI code. This blueprint exists to prove the mise workflow itself.


## Custom catalog metadata

Every new task in an included `*.toml` file MUST have matching arbitrary metadata in the adjacent `*.meta.toml` sidecar.

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
number = 123
tags = ["docker", "ps"]
anything_you_want = "custom metadata"
```

Custom metadata is intentionally open-ended. Add fields as the product model evolves.

Do not put arbitrary fields directly inside a mise task table.

After changes validate both the executable task files and the metadata-to-task mapping.
