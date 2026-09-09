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
file = "../../scripts/bash/install-packages.sh"
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
development:ssh:keygen
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
```

Use only mise-supported properties. Keep future UI/plugin metadata separate.

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
python tools/validate-blueprint.py
mise tasks validate
mise tasks ls
mise tasks info category:new-task
```


## Important: `file` path resolution in included TOML

For an included task file such as:

```text
tasks/system/logs.toml
```

mise resolves a relative `file =` path from the directory containing that included TOML file.

Therefore this blueprint uses:

```toml
file = "../../scripts/bash/logs-unit.sh"
```

not:

```toml
file = "scripts/bash/logs-unit.sh"
```

This is intentionally different from a task declared directly in the root `mise.toml`, where `scripts/...` would be relative to the root config file.
