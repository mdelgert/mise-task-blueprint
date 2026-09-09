# Global Mise Setup

The root `mise.toml` makes the catalog work when you are inside this repository:

```toml
[task_config]
includes = ["tasks"]
```

To make the same tasks available from **any directory**, add them to your user-global mise config.

Typical file:

```text
~/.config/mise/config.toml
```

Example repository location:

```text
~/Source/private/mise-task-blueprint
```

Recommended global configuration:

```toml
[task_config]
includes = [
  "{{env.HOME}}/.config/mise/tasks",
  "{{env.HOME}}/Source/private/mise-task-blueprint/tasks",
]
excludes = [
  "{{env.HOME}}/Source/private/mise-task-blueprint/tasks/**/*.meta.toml",
]
```

Important: setting `task_config.includes` replaces the default file-task directories for that config scope. The first entry above deliberately preserves the normal user-global task directory.

**`excludes` is not optional.** Metadata sidecars live beside the task files, and
mise's included-task schema treats every root key as a task. Omit the exclude and
mise fails on the first sidecar with `unknown field \`tasks\`` and loads **zero**
tasks:

```
mise ERROR Error parsing task file: .../tasks/docker/compose.meta.toml
mise ERROR TOML parse error at line 8, column 2
  | [_.tasks."docker:compose:config"]
  |  ^ unknown field `tasks`
```

Unlike the repository-local `mise.toml`, where `"tasks/**/*.meta.toml"` is
relative to the config, a global exclude must be **fully qualified against the
same root as the include**. A bare `"**/*.meta.toml"` silently matches nothing.

Now from anywhere:

```bash
mise tasks ls
mise system:info
mise network:ports
mise docker:ps
```

For scripts and automation prefer the explicit form:

```bash
mise run system:info
```

## Config fragment option

You may instead keep this in:

```text
~/.config/mise/conf.d/50-tasks.toml
```

with the same contents.

## Diagnose what mise loaded

```bash
mise config
mise cfg
mise tasks ls --global
mise tasks ls --extended
mise tasks ls --json
```

## Recommended real project location

```text
~/Source/private/
└── mise-task-blueprint/
    ├── mise.toml
    ├── tasks/
    ├── scripts/
    ├── docs/
    └── skills/
```

Then update both the include **and** the exclude path accordingly.
