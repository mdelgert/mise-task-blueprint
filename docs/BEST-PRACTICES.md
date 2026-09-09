# Mise Task Blueprint Best Practices

This repository is intended as a reusable pattern for mise-based automation projects.

## 1. Use `tasks/` as the public source tree

Prefer:

```text
tasks/
├── system/
├── network/
├── docker/
├── dev/
└── omarchy/
```

`tasks/` communicates exactly what the directory contains and does not tie the blueprint to a specific product concept.

## 2. Keep task names explicit and stable

Folders organize source. Public task names are an API.

```toml
["docker:compose:up"]
description = "Start Compose services in the current directory"
dir = "{{cwd}}"
run = "docker compose up"
```

Do not rely on the filename to create the namespace.

## 3. Keep native mise configuration separate from arbitrary metadata

Executable task:

```toml
["docker:ps"]
description = "List running Docker containers"
run = "docker ps"
```

Adjacent custom metadata:

```toml
[_.tasks."docker:ps"]
icon = "container"
risk = "low"
enabled = true
number = 100
tags = ["docker", "containers"]
```

This preserves strict mise task validation while allowing the project to add any catalog fields it needs.

## 4. Use sidecar metadata for included task TOMLs

Recommended pair:

```text
tasks/docker/
├── core.toml
└── core.meta.toml
```

Root config:

```toml
[task_config]
includes = ["tasks"]
excludes = ["tasks/**/*.meta.toml"]
```

The sidecar pattern makes metadata discoverable to humans without causing mise to interpret `_` as a task in an included task file.

## 5. Prefer TOML for small tasks

Good:

```toml
["system:uptime"]
description = "Show system uptime"
run = "uptime"
```

## 6. Prefer scripts for real logic

Use Bash/Python/Node when the implementation has branches, loops, platform detection, multiple commands, argument validation, or structured output.

```toml
["system:pkg:install-core"]
description = "Install the baseline package set"
file = "scripts/bash/install-packages.sh"
```

Keep the task definition declarative and the implementation testable.

## 7. Declare task-specific runtimes with mise

```toml
["dev:metadata:python"]
description = "Return task metadata as JSON"
tools = { python = "3.14" }
file = "scripts/python/task_metadata.py"
```

Avoid requiring users to manually install a particular runtime version when mise can provision it.

## 8. Use the OS package manager for OS-integrated software

Desktop apps, system daemons, drivers, and host packages often belong in pacman/apt/dnf.

Use mise primarily for developer runtimes and CLI tools where its backend model is appropriate.

## 9. Use `dir = "{{cwd}}"` for caller-project tasks

Examples:

```toml
["dev:git:status"]
dir = "{{cwd}}"
run = "git status"
```

```toml
["docker:compose:up"]
dir = "{{cwd}}"
run = "docker compose up"
```

This lets a global task operate on the directory from which the user invoked mise.

## 10. Destructive tasks must be obvious

Use explicit names, descriptions, and `confirm`.

```toml
["docker:prune:all"]
description = "Remove all unused Docker images and other unused objects"
confirm = "Run docker system prune -a?"
run = "docker system prune -a"
```

## 11. Keep secrets out of task metadata and output

Never place secrets in:

- `mise.toml`
- task TOML
- `*.meta.toml`
- logs
- generated task-list JSON

Metadata should describe behavior, not contain credentials.

## 12. Treat metadata keys as a project schema

Arbitrary means extensible, not random.

A useful baseline:

```toml
[_.tasks."example:task"]
icon = "terminal"
risk = "low"
enabled = true
number = 100
tags = ["example"]
category = "example"
destructive = false
requires_sudo = false
interactive = false
```

Future fields can be added deliberately:

```toml
platforms = ["linux"]
requires_network = true
author = "..."
docs = "..."
```

Document new fields in `docs/CUSTOM-METADATA.md`.

## 13. Validate task ↔ metadata parity

Every public task should have matching metadata.

The included validator checks:

- TOML syntax
- duplicate/missing tasks
- task-to-metadata mapping
- referenced script existence
- Bash syntax
- Python syntax

Run:

```bash
python tools/validate-blueprint.py
```

Then:

```bash
mise tasks validate
mise tasks ls
mise tasks ls --json
```

## 14. Keep the CLI useful without a plugin

A UI should enhance the task system, not be required to use it.

A good project remains useful with:

```bash
mise tasks ls
mise tasks info docker:ps
mise docker:ps
```

## 15. Keep project-specific concepts out of the generic core

This blueprint includes an `omarchy/` category as an example because domain-specific categories are valid.

But the core structure remains generic:

```text
tasks/
scripts/
docs/
skills/
tools/
```

A future product can call tasks "recipes" in its UI while the underlying implementation remains standard mise tasks.
