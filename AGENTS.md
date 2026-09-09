# Agent Instructions

Before editing tasks:

1. Read `skills/mise-task-authoring/SKILL.md`.
2. Read `docs/AUTHORING-GUIDE.md`.
3. Preserve explicit colon-delimited task names.
4. Use TOML for short commands.
5. Use `scripts/bash`, `scripts/python`, or `scripts/node` for logic.
6. Every public task needs `description`.
7. Destructive actions need explicit naming and `confirm`.
8. Use only mise-supported task metadata properties.
9. Never hard-code or print secrets/private keys.
10. Run `python tools/validate-blueprint.py`.
11. When mise is present, run `mise tasks validate` and `mise tasks ls`.
12. Do not add plugin/UI code to this blueprint.

13. Read `docs/CUSTOM-METADATA.md`.
14. Every new included task must receive a matching `[_.tasks."<task-name>"]` entry in the adjacent `*.meta.toml` sidecar.
15. Custom catalog fields belong under `_`; never add arbitrary keys directly to mise task definitions.
