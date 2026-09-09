# Custom Metadata with `[_.tasks.*]`

This is the extension point the project is intentionally built around.

## Exact syntax in a normal `mise.toml`

Mise's normal config schema reserves top-level `_` as an object with arbitrary properties.

```toml
[tasks.hello]
description = "Say hello"
run = "echo hello"

[_.tasks.hello]
icon = "hand"
risk = "low"
anything_you_want = "test"
enabled = true
number = 123
tags = ["example", "test"]
```

The values under `_` are **your data**, not native mise task properties. Mise
does not validate them, so `number = 123` and `anything_you_want = "test"` above
are legal purely to demonstrate that arbitrary typed values survive the round
trip. They are not part of this project's schema -- see
[Required metadata schema](#required-metadata-schema) below.

That means you can evolve metadata independently:

```toml
[_.tasks.hello]
# the project's required schema
icon = "hand"
risk = "low"
enabled = true
tags = ["example"]
category = "root"
destructive = false
requires_confirm = false
requires_sudo = false
interactive = false
cwd_scope = "project"

# anything else the product model needs
documentation_url = "..."
platforms = ["linux"]
requires_network = false
```

## Critical difference: included task TOMLs

Files loaded through:

```toml
[task_config]
includes = ["tasks"]
```

use mise's **included task-file schema**. Every root key is interpreted as a task.

Therefore putting this directly into an included task file:

```toml
[_.tasks.hello]
```

would make `_` appear to be a task name and does not match the included-task schema.

The blueprint therefore keeps adjacent pairs:

```text
tasks/docker/
├── core.toml
└── core.meta.toml
```

`core.toml` is mise-native:

```toml
["docker:ps"]
description = "List running Docker containers"
run = "docker ps"
```

`core.meta.toml` is catalog metadata:

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

Root `mise.toml` excludes all metadata sidecars:

```toml
[task_config]
includes = ["tasks"]
excludes = ["tasks/**/*.meta.toml"]
```

So:

```bash
mise tasks ls
```

continues to see only real executable tasks.

## Read all metadata

Bash wrapper:

```bash
mise dev:metadata:all:bash
```

Direct Python:

```bash
mise dev:metadata:all:python
```

Both return a JSON object keyed by task name.

## Build future plugin-style catalog JSON

```bash
mise dev:catalog:json
```

This performs:

```text
mise tasks ls --json          native task fields
        +
mise tasks info <t> --json    typed arguments (usage_spec)
        +
all [_.tasks.*] sidecars      catalog metadata
        ↓
versioned JSON catalog        schemas/catalog.schema.json
```

The output is an envelope, not a bare array, so the shape can grow without
breaking readers. Native mise fields stay separate from custom ones:

```json
{
  "schema_version": 1,
  "task_count": 120,
  "tasks": [
    {
      "name": "docker:ps",
      "description": "List running Docker containers",
      "category": "docker",
      "args": [],
      "execution": { "command": ["mise", "run", "docker:ps"], "...": "..." },
      "meta": { "icon": "container", "risk": "low", "...": "..." },
      "mise": { "...raw native task object..." }
    }
  ]
}
```

The `execution` block exists because mise alone cannot tell a consumer whether a
task needs a TTY, needs confirmation, or acts on the caller's directory. See
`docs/PLUGIN-CONTRACT.md`.

That is the intended boundary:

- mise owns execution metadata
- `_` owns arbitrary product/catalog metadata
- the catalog reader joins them by task name

## Why this is preferable to stuffing custom fields into a task

Do not do this:

```toml
["docker:ps"]
description = "..."
run = "docker ps"
risk = "low"
icon = "container"
```

Those are not native mise task properties and can fail mise's task schema.

Keep arbitrary fields under `_`.


## Required metadata schema

Ten fields are required on every task. `tools/validate-blueprint.py` fails the
build if any is missing, mistyped, or holds a disallowed value, and
`schemas/task-metadata.schema.json` is the machine-readable version.

```toml
[_.tasks."category:group:action"]
icon = "terminal"           # string  -- icon hint for a UI
risk = "low"                # enum    -- low | medium | high
enabled = true              # bool    -- false hides it from the catalog
tags = ["category", "group"] # [string] -- search/filter keywords
category = "category"       # string  -- must equal the name prefix
destructive = false         # bool    -- can irreversibly destroy state
requires_confirm = false    # bool    -- mirrors the task's `confirm`
requires_sudo = false       # bool    -- escalates privileges
interactive = false         # bool    -- mirrors the task's `raw`/`interactive`
cwd_scope = "project"       # enum    -- caller | project
```

### Four fields are derived, not chosen

These mirror the task definition and must agree with it:

| Field              | Must equal                                    |
| ------------------ | --------------------------------------------- |
| `category`         | the task name's prefix, or `root`             |
| `requires_confirm` | whether the task has `confirm`                |
| `interactive`      | whether the task has `raw` or `interactive`   |
| `cwd_scope`        | `caller` if `dir = "{{cwd}}"`, else `project` |

`requires_confirm` is the important one. Mise does not report `confirm` in *any*
`--json` output, so this field is the only machine-readable signal that a task
is gated. Nothing but the validator keeps it honest.

### Consistency rules

- `destructive = true` requires `requires_confirm = true` and `risk = "high"`.
- `requires_sudo = true` cannot be `risk = "low"`.

### Risk semantics

- `low`: read-only or easily reversible
- `medium`: changes local state, installs software, creates credentials/files,
  or talks to external systems
- `high`: destructive, privilege-heavy, broad system modification, or difficult
  to reverse

## Adding fields

The schema is deliberately extensible; `additionalProperties` is allowed. To add
a field:

1. Add it to the sidecars that need it.
2. Document it here.
3. Add it to `schemas/task-metadata.schema.json`.
4. If consumers should rely on it, add a rule to `tools/validate-blueprint.py`
   so it cannot silently rot.

Candidates the blueprint does not yet define:

```toml
platforms = ["linux"]
requires_network = true
docs = "https://..."
```

Do not add a field with no consumer and no meaning. Two such fields (`number`
and `anything_you_want`) were carried on all 120 tasks before being removed --
they cost real maintenance and told a reader nothing.
