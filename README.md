# Mise Task Blueprint

A comprehensive, plugin-free blueprint for a discoverable command/task catalog built on **mise**.

The point of this repository is to prove the complete CLI and authoring workflow before building any UI/plugin.

## Start here

```bash
cd mise-task-blueprint

# Parse every TOML file without executing tasks
python tools/validate-blueprint.py

# Native mise validation/discovery
mise tasks validate
mise tasks ls
mise tasks ls --extended
mise tasks ls --json

# Inspect one task, including its selected source/metadata
mise tasks info docker:ps
mise tasks info docker:ps --json

# Friendly interactive shorthand
mise docker:ps

# Preferred form inside scripts/automation
mise run docker:ps
```

## Reference rules

1. **Mise owns discovery and execution.**
2. **Git owns distribution/history.**
3. **Folders organize source; explicit task names define the public CLI.**
4. **Small commands stay in TOML.**
5. **Logic goes into Bash/Python/Node scripts.**
6. **Every public task has a useful `description`.**
7. **Destructive tasks use `confirm`.**
8. **Task-specific runtimes use mise `tools`.**
9. **OS-integrated applications/services use the OS package manager where appropriate.**
10. **No plugin code lives here.**

## Layout

```text
mise-task-blueprint/
├── mise.toml
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── docs/
│   ├── GLOBAL-SETUP.md
│   ├── AUTHORING-GUIDE.md
│   ├── SECURITY.md
│   └── TASK-NAMING.md
├── tasks/
│   ├── system/
│   │   ├── info.toml
│   │   ├── packages.toml
│   │   ├── services.toml
│   │   ├── logs.toml
│   │   └── files.toml
│   ├── network/
│   │   ├── info.toml
│   │   ├── diagnostics.toml
│   │   └── http.toml
│   ├── docker/
│   │   ├── core.toml
│   │   ├── containers.toml
│   │   └── compose.toml
│   ├── dev/
│   │   ├── git.toml
│   │   ├── runtimes.toml
│   │   ├── github.toml
│   │   └── secrets.toml
│   └── omarchy/
│       ├── system.toml
│       └── desktop.toml
├── scripts/
│   ├── bash/
│   ├── python/
│   └── node/
├── examples/
│   ├── docker-compose/
│   └── global-config.toml
├── skills/
│   └── mise-task-authoring/
│       └── SKILL.md
└── tools/
    └── validate-blueprint.py
```

## Why explicit task names

Do not rely on the TOML filename or folder path to define the command namespace.

For example, `tasks/docker/core.toml` contains:

```toml
["docker:ps"]
description = "List running Docker containers"
run = "docker ps"
```

The public command is therefore always:

```bash
mise docker:ps
```

You can move `core.toml` later without changing the task's CLI API.

File tasks have their own directory-prefix behavior, but this blueprint deliberately keeps the public names explicit in TOML.

## Mise metadata pattern

Use mise-native task properties only:

```toml
["category:group:action"]
description = "Short user-facing explanation"
alias = "short-name"                 # when useful
dir = "{{cwd}}"                      # operate in caller's directory
tools = { python = "3.14" }          # task-specific mise runtime/tool
env = { MODE = "demo" }              # task-local env
depends = ["category:other"]          # dependency graph
confirm = "Continue?"                # destructive/sensitive action
hide = false
run = "command"
```

For script-backed tasks:

```toml
["system:logs:unit"]
description = "Show recent logs for a systemd unit"
file = "scripts/bash/logs-unit.sh"
```

Do not invent arbitrary mise task keys such as `risk`, `tags`, or `category` until you deliberately add a separate plugin metadata schema.

## Categories

### System

```bash
mise system:info
mise system:uptime
mise system:memory
mise system:disk
mise system:pkg:install-core
mise system:pkg:update
mise system:services:failed
mise system:logs:boot-errors
mise system:logs:unit sshd
```

### Network

```bash
mise network:ip
mise network:routes
mise network:dns
mise network:ports
mise network:ping-cloudflare
mise network:public-ip
mise network:http:headers
mise network:http:json
mise network:http:weather Phoenix
```

### Docker

Without Compose:

```bash
mise docker:ps
mise docker:images
mise docker:stats
mise docker:container:inspect my-container
mise docker:container:logs my-container
mise docker:container:shell my-container

mise docker:ubuntu:create
mise docker:ubuntu:enter
mise docker:ubuntu:stop
mise docker:ubuntu:remove

# disposable Ubuntu
mise docker:ubuntu:run
```

With a Compose file in your current project:

```bash
mise docker:compose:config
mise docker:compose:up
mise docker:compose:up-detached
mise docker:compose:ps
mise docker:compose:logs
mise docker:compose:pull
mise docker:compose:build
mise docker:compose:restart
mise docker:compose:down
```

Included Compose demo:

```bash
mise docker:compose:demo:up
mise docker:compose:demo:ps
mise docker:compose:demo:logs
mise docker:compose:demo:down
```

### Development

```bash
mise dev:git:status
mise dev:git:log

mise dev:python:version
mise dev:python:hello
mise dev:node:version
mise dev:node:hello

mise dev:metadata:bash
mise dev:metadata:python

mise dev:github:auth
mise dev:github:auth-status
mise dev:github:user
mise dev:github:pat:help

mise dev:ssh:keygen
mise dev:age:keygen
mise dev:age:encrypt
mise dev:age:decrypt
mise dev:sops:demo
```

### Omarchy

```bash
mise omarchy:commands
mise omarchy:commands:json
mise omarchy:debug
mise omarchy:update
mise omarchy:theme:list
mise omarchy:font:list
mise omarchy:hypr:monitors
mise omarchy:hypr:clients
mise omarchy:hypr:binds
mise omarchy:hypr:devices
mise omarchy:hypr:reload
```

## Package installation example

`system:pkg:install-core` demonstrates one task calling a real Bash implementation that detects:

- Arch / Omarchy (`pacman`)
- Debian / Ubuntu (`apt-get`)
- Fedora / RHEL-family (`dnf`)

The baseline includes examples for:

- ansible
- nano
- remmina
- age
- sops
- curl
- jq
- git
- OpenSSH
- Docker
- Docker Compose

The script contains an obvious placeholder section for future packages.

## Runtime examples

These demonstrate the important mise pattern:

```toml
["dev:python:hello"]
tools = { python = "3.14" }
file = "scripts/python/task_metadata.py"

["dev:node:hello"]
tools = { node = "24" }
file = "scripts/node/hello.mjs"
```

The host doesn't need those particular Python/Node versions installed through its OS package manager first; mise resolves/activates the requested runtime for the task.

## Metadata-returning examples

Bash:

```bash
mise dev:metadata:bash
```

Python:

```bash
mise dev:metadata:python
```

Both output JSON containing useful execution context such as the task name, task directory, project root and original working directory.

## GitHub PAT note

A GitHub PAT is issued by GitHub. This blueprint intentionally does **not** fabricate a locally generated random string and call it a GitHub PAT.

Instead:

```bash
mise dev:github:auth
mise dev:github:pat:help
```

demonstrate the correct workflow using GitHub CLI and least-privilege guidance.

## Global catalog

See `docs/GLOBAL-SETUP.md`.

The recommended model is:

```text
~/.config/mise/config.toml
        │
        └── includes
             ~/Source/private/mise-task-blueprint/tasks
```

Then tasks are available from any directory.

## AI authoring

Point an agent to:

```text
skills/mise-task-authoring/SKILL.md
```

Also included:

```text
AGENTS.md
CLAUDE.md
```

A useful kickoff instruction is:

```text
Read AGENTS.md and skills/mise-task-authoring/SKILL.md before adding or changing mise tasks.
Follow the existing category, naming, metadata, safety and validation patterns.
```

## Security

Treat mise task configuration as executable code.

Before running an unfamiliar recipe:

```bash
mise tasks info <task>
```

Read `docs/SECURITY.md` for the blueprint rules.


## Custom metadata: the important `_` namespace

The blueprint now explicitly demonstrates the arbitrary metadata pattern:

```toml
[tasks.hello]
description = "Simple task"
run = "echo hello"

[_.tasks.hello]
icon = "hand"
risk = "low"
anything_you_want = "test"
enabled = true
number = 123
tags = ["example", "test"]
```

For included task TOMLs, metadata is stored in adjacent `*.meta.toml` sidecars because mise's included-task schema treats every root key as a task.

Example:

```text
tasks/docker/
├── core.toml
└── core.meta.toml
```

`mise.toml` excludes `*.meta.toml` files from task discovery.

Useful commands:

```bash
mise tasks ls
mise dev:metadata:all:bash
mise dev:metadata:all:python
mise dev:catalog:json
```

See `docs/CUSTOM-METADATA.md`.


For the design rationale and conventions, read `docs/BEST-PRACTICES.md`.
