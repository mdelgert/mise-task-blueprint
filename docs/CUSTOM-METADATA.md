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

The values under `_` are **your data**, not native mise task properties.

That means you can evolve metadata independently:

```toml
[_.tasks.hello]
icon = "hand"
risk = "low"
enabled = true
number = 123
tags = ["example", "test"]

category = "example"
destructive = false
requires_sudo = false
interactive = false

author = "Matthew"
documentation_url = "..."
platforms = ["linux"]
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
number = 1
tags = ["docker", "ps"]
category = "docker"
destructive = false
requires_sudo = false
interactive = false
anything_you_want = "custom metadata for docker:ps"
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
mise tasks ls --json
        +
all [_.tasks.*] sidecars
        ↓
merged JSON catalog
```

The output keeps native mise fields separate from custom fields:

```json
[
  {
    "name": "docker:ps",
    "description": "List running Docker containers",
    "...native mise fields...": "...",
    "meta": {
      "icon": "container",
      "risk": "low",
      "enabled": true,
      "tags": ["docker", "ps"]
    }
  }
]
```

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


## Recommended baseline metadata schema

For this blueprint, use these fields consistently unless a task has a strong reason not to:

```toml
[_.tasks."category:group:action"]
icon = "terminal"
risk = "low"
enabled = true
number = 100
tags = ["category", "group"]
category = "category"
destructive = false
requires_sudo = false
interactive = false
```

The schema is intentionally extensible, but new keys should be documented before becoming widespread.

Suggested risk values:

```text
low
medium
high
```

Suggested semantics:

- `low`: read-only or easily reversible
- `medium`: changes local state, installs software, creates credentials/files, or talks to external systems
- `high`: destructive, privilege-heavy, broad system modification, or difficult to reverse

`number` is an arbitrary numeric example field retained to prove typed metadata handling. It should not be treated as a ranking unless the project later defines that meaning.
