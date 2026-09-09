# Mise Task Blueprint

A comprehensive, plugin-free blueprint for a discoverable command/task catalog built on **mise**.

The point of this repository is to prove the complete CLI and authoring workflow before building any UI/plugin.

## Start here

```bash
cd mise-task-blueprint

# Validate syntax, metadata schema and task/metadata invariants
mise run dev:blueprint:validate

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
10. **Tasks that take arguments declare them**, so a UI can render inputs.
11. **No plugin code lives here** — the blueprint publishes a contract instead.

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
│   ├── BEST-PRACTICES.md
│   ├── CUSTOM-METADATA.md
│   ├── PLUGIN-CONTRACT.md
│   ├── SECURITY.md
│   └── TASK-NAMING.md
├── tasks/
│   ├── ai/
│   │   └── agents.toml
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
│   │   ├── blueprint.toml
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
│   ├── overlays/            # personal shortcuts to copy into your own config
│   └── global-config.toml
├── schemas/                 # the machine-readable plugin contract
│   ├── catalog.schema.json
│   └── task-metadata.schema.json
├── skills/
│   └── mise-task-authoring/
│       └── SKILL.md
├── tools/
│   ├── validate-blueprint.py
│   └── check-catalog-schema.py
├── MANIFEST.json            # generated -- do not hand-edit
└── .github/workflows/
    └── validate.yml
```

Each `tasks/**/x.toml` has an adjacent `x.meta.toml` sidecar holding its
catalog metadata.

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

Do not invent arbitrary mise task keys such as `risk`, `tags`, or `category`
inside the task table -- those live in the `*.meta.toml` sidecar under `_`. See
`docs/CUSTOM-METADATA.md`.

Tasks that read arguments declare them, so `mise <task> --help` works and a UI
can discover parameters:

```toml
["network:trace"]
description = "Trace route to a host"
usage = '''
arg "<host>" help="Host name or IP address to trace a route to"
'''
run = 'traceroute "$usage_host"'
```

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
mise dev:catalog:json

mise dev:blueprint:validate
mise dev:blueprint:manifest
mise dev:blueprint:schema
mise dev:blueprint:ci

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

### AI agents

Each hands the terminal to a full-screen agent TUI and runs it with its own
approval gate disabled, so each carries an explicit `confirm`:

```bash
mise ai:claude
mise ai:copilot
mise ai:codex
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
file = "scripts/python/hello-python.py"

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

Mise reserves top-level `_` for arbitrary data, which this blueprint uses to
carry catalog metadata alongside strictly-validated mise tasks:

```toml
[tasks.hello]
description = "Simple task"
run = "echo hello"

[_.tasks.hello]
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
```

For included task TOMLs, metadata is stored in adjacent `*.meta.toml` sidecars
because mise's included-task schema treats every root key as a task.

```text
tasks/docker/
├── core.toml
└── core.meta.toml
```

`mise.toml` excludes `*.meta.toml` files from task discovery.

Ten fields are required and validated. Four of them mirror the task definition
(`category`, `requires_confirm`, `interactive`, `cwd_scope`) and the validator
fails if they disagree with it.

```bash
mise tasks ls
mise dev:metadata:all:bash
mise dev:metadata:all:python
mise dev:catalog:json
```

See `docs/CUSTOM-METADATA.md`.

## Building a UI on top of this

The blueprint contains no plugin code. It publishes a versioned contract:

```bash
mise dev:catalog:json     # schemas/catalog.schema.json
```

Each task in that output carries its typed `args` and an `execution` block
telling a launcher what it needs: a TTY, a confirmation dialog, a working
directory, or elevated privileges.

That block exists because four things a consumer needs cannot be obtained from
mise alone:

| Need              | Why mise is not enough                                   |
| ----------------- | -------------------------------------------------------- |
| arguments         | `tasks ls --json` omits them; only `tasks info` has them |
| confirmation      | `confirm` appears in **no** `--json` output              |
| terminal handling | `raw` tasks must get a TTY, not a captured pipe          |
| working directory | `dir = "{{cwd}}"` is already resolved away in the JSON   |

Read `docs/PLUGIN-CONTRACT.md` before writing a consumer.

## Validation and CI

```bash
mise run dev:blueprint:ci        # the gate CI runs
```

- `mise tasks validate` — mise's own task checks
- `mise run dev:blueprint:validate` — metadata schema and task/metadata invariants
- `mise run dev:blueprint:schema` — the generated catalog against `schemas/`
- `mise run dev:blueprint:manifest` — regenerate `MANIFEST.json`

`.github/workflows/validate.yml` runs the same gate on push and pull request,
with `shellcheck` installed so that layer runs too.

For the design rationale and conventions, read `docs/BEST-PRACTICES.md`.
