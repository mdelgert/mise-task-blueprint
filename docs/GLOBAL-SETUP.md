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
```

Important: setting `task_config.includes` replaces the default file-task directories for that config scope. The first entry above deliberately preserves the normal user-global task directory.

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
└── omarchy-tasks/
    ├── mise.toml
    ├── tasks/
    ├── scripts/
    ├── docs/
    └── skills/
```

Then update the global include path accordingly.
