# Agent Instructions

Before editing tasks:

1. Read `skills/mise-task-authoring/SKILL.md`.
2. Read `docs/AUTHORING-GUIDE.md`.
3. Read `docs/CUSTOM-METADATA.md`.
4. Read `docs/PLUGIN-CONTRACT.md` before changing anything a consumer reads:
   sidecar fields, `scripts/python/catalog_json.py`, or `schemas/`.

Authoring rules:

5. Preserve explicit colon-delimited task names.
6. Use TOML for short commands.
7. Use `scripts/bash`, `scripts/python`, or `scripts/node` for logic.
8. Every public task needs `description`.
9. Destructive actions need explicit naming and `confirm`.
10. Use only mise-supported task metadata properties.
11. Never hard-code or print secrets/private keys.
12. Keep personal/machine-specific tasks out of `tasks/` — use `examples/overlays/`.

Machine-readability rules (these are what make a UI possible):

13. Every task that reads arguments must declare them: `#USAGE arg ...` in a
    `file =` script, or a `usage` property for an inline `run`.
14. Never mix a `usage` spec with `$1`/`$2` in an inline `run` — mise passes
    args as `$usage_<name>` only, and positionals come through empty.
15. Every new included task needs a matching `[_.tasks."<task-name>"]` entry in
    the adjacent `*.meta.toml` sidecar, with all required fields.
16. Custom catalog fields belong under `_`; never add arbitrary keys directly to
    mise task definitions.
17. Keep the four derived sidecar fields truthful: `category`,
    `requires_confirm`, `interactive`, `cwd_scope`. They mirror the task and are
    enforced. `requires_confirm` matters most — mise never reports `confirm` in
    any JSON output, so it is a consumer's only signal.

Validate every change:

18. Run `mise run dev:blueprint:validate`.
19. When mise is present, run `mise tasks validate` and `mise tasks ls`.
20. Before finishing, `mise run dev:blueprint:ci` runs the full CI gate.

Scope:

21. Do not add plugin/UI code to this blueprint.
