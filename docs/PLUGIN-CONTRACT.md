# Plugin Contract

What a UI (an Omarchy plugin, a TUI, anything) may rely on, and the four things
mise will not tell you that this blueprint has to.

The blueprint contains no plugin code. It publishes a contract.

## The one command

```bash
mise dev:catalog:json
```

Returns a versioned envelope described by `schemas/catalog.schema.json`:

```json
{
  "schema_version": 1,
  "project": "mise-task-blueprint",
  "task_count": 120,
  "tasks": [
    {
      "name": "docker:container:logs",
      "description": "Show recent container logs; pass container name/ID and optional line count",
      "category": "docker",
      "aliases": [],
      "args": [
        { "name": "container", "help": "Container name or ID", "required": true,  "default": null,  "variadic": false },
        { "name": "lines",     "help": "Number of log lines to show", "required": false, "default": "200", "variadic": false }
      ],
      "execution": {
        "command": ["mise", "run", "docker:container:logs"],
        "needs_tty": false,
        "needs_confirmation": false,
        "confirm_bypass_flag": null,
        "cwd_scope": "project",
        "requires_sudo": false
      },
      "meta":  { "icon": "container", "risk": "low", "...": "..." },
      "mise":  { "...raw `mise tasks ls --json` object..." }
    }
  ]
}
```

Takes ~0.5s for ~120 tasks. Cache it; regenerate when any config file changes.

`schema_version` is bumped only for breaking changes. New fields may appear
without a bump, so ignore unknown keys rather than rejecting them.

## Why not just call mise directly?

Four things a consumer needs are not available from any single mise command.
This is the entire reason the blueprint exists in this shape.

### 1. `confirm` is in no JSON output at all

```bash
mise tasks info docker:prune --json | grep confirm   # no match
```

A task's `confirm` string is invisible to `tasks ls --json` and
`tasks info --json` alike. Read `execution.needs_confirmation` instead, which is
mirrored from the sidecar's `requires_confirm` and kept truthful by
`tools/validate-blueprint.py`.

### 2. Arguments are only in `tasks info`, not `tasks ls`

`mise tasks ls --json` reports `args: []` for every task. The typed parameter
list lives in `mise tasks info <task> --json` under `usage_spec`, one task at a
time. `catalog_json.py` fans those calls out and flattens them into `args`.

Only tasks that declare a spec have arguments to report — a `#USAGE arg` line in
their script or a `usage` property on an inline `run`. The validator rejects any
task that reads arguments without declaring them, so `args` can be trusted to be
complete.

### 3. There is no TTY, and `confirm` requires one

```
$ mise run docker:prune < /dev/null
[docker:prune] ERROR task requires confirmation but there was nobody to ask; pass --yes to accept
```

A panel launched from a bar widget has no controlling terminal, so every
`confirm` task fails. `--yes` fixes that but disables confirmation for
everything in the invocation — including `ai:codex`, which runs an agent with
its approval gate bypassed.

**So the UI must own the confirmation step:**

1. Read `execution.needs_confirmation`.
2. If true, show your own dialog. Use `meta.risk` and `meta.destructive` to
   decide how loud it should be.
3. Only after the user consents, append `execution.confirm_bypass_flag`.

Never pass `--yes` without having asked.

### 4. `dir = "{{cwd}}"` has no meaning without a caller

19 tasks act on the invoking directory (`dev:git:*`, `docker:compose:*`,
`system:files:cwd-size`). In `mise tasks ls --json` their `dir` is already
resolved to the config root, so that field cannot tell you they are
caller-relative.

Read `execution.cwd_scope`:

- `"caller"` — ask the user for a directory and set the child process's cwd to
  it. Running these from a panel's default cwd operates on the blueprint repo,
  silently and wrongly.
- `"project"` — run from the config root.

## Launching a task

```
argv  = execution.command
argv += [positional values for execution's args, in order]
argv += [execution.confirm_bypass_flag] if the user has just consented

cwd   = user-chosen directory   if execution.cwd_scope == "caller"
        config root             otherwise

if execution.needs_tty:   launch in a terminal emulator; do not capture stdout
else:                     capture stdout/stderr normally
```

`needs_tty` is true for 14 tasks that hand the terminal to a child process
(`raw = true`): agent TUIs, `docker exec -it`, `journalctl -f`, `gh auth login`.
Capturing their output instead of giving them a terminal will hang or misbehave.

## Metadata fields

`meta` is the task's sidecar entry verbatim, described by
`schemas/task-metadata.schema.json`. Presentation-relevant fields:

| Field         | Use                                                              |
| ------------- | ---------------------------------------------------------------- |
| `icon`        | Icon hint; map to your own icon set                              |
| `risk`        | `low` / `medium` / `high` — badge severity                       |
| `destructive` | Show the loudest warning; implies `risk = "high"` and confirm     |
| `enabled`     | `false` means hide from the catalog without removing from mise    |
| `tags`        | Search and filtering                                             |
| `category`    | Grouping; always equals the task name prefix                     |

The set is intentionally extensible: additional fields are expected as the
product model grows. Add them to the sidecars, document them in
`docs/CUSTOM-METADATA.md`, and extend `schemas/task-metadata.schema.json`.

## What keeps this honest

`mise tasks validate` checks the mise-native side.
`mise run dev:blueprint:validate` checks the contract side:

- every task has a sidecar entry with all required fields, correct types and
  allowed values;
- the four derived fields (`category`, `requires_confirm`, `interactive`,
  `cwd_scope`) match the task they describe;
- `destructive` implies `confirm` and `risk = "high"`;
- no task reads arguments without declaring them;
- no inline `run` mixes a `usage` spec with `$1`.

`mise run dev:blueprint:schema` additionally validates the generated catalog
against `schemas/`, so the published shape cannot drift from its own schema.

Without those checks the sidecar is just a comment. `requires_confirm` in
particular has no other enforcement, and it is the field that decides whether a
UI warns before running `docker system prune -a`.

## Stability

Stable, safe to depend on:

- task names (`docs/TASK-NAMING.md` — moving a file must not rename a task)
- the `schema_version: 1` envelope
- `execution` and `args` field names and semantics
- required `meta` fields

Not stable:

- the `mise` passthrough object — it is whatever the installed mise emits
- optional `meta` fields beyond the required set
- task descriptions
