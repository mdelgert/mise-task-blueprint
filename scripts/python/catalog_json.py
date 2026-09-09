#!/usr/bin/env python3
"""Emit the versioned task catalog: the contract a UI/plugin consumes.

Joins three sources that no single mise command exposes together:

  mise tasks ls --json      native task fields (name, description, tools, ...)
  mise tasks info <t> --json per-task `usage_spec`, i.e. typed arguments
  tasks/**/*.meta.toml      arbitrary [_.tasks.*] catalog metadata

Two things a consumer cannot get from mise alone and must read from here:

  * arguments -- `tasks ls --json` omits `usage_spec`; only `tasks info` has it.
  * confirmation -- mise never reports `confirm` in any JSON output, so the
    `requires_confirm` flag from the sidecar is the only machine-readable
    signal that a task is gated. tools/validate-blueprint.py enforces that it
    matches reality.

Output is a versioned envelope (see schemas/catalog.schema.json), not a bare
array, so the shape can grow without breaking existing readers.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(os.environ.get("MISE_PROJECT_ROOT") or Path(__file__).resolve().parents[2])
sys.path.insert(0, str(ROOT / "scripts" / "python"))
from catalog_metadata import collect  # noqa: E402

SCHEMA_VERSION = 1


def mise_json(*argv: str) -> object:
    p = subprocess.run(["mise", *argv], cwd=ROOT, text=True,
                       capture_output=True, check=True)
    return json.loads(p.stdout)


def task_list() -> list[dict]:
    data = mise_json("tasks", "ls", "--json")
    # Current mise emits a list; tolerate a dict shape defensively.
    if isinstance(data, dict):
        inner = data.get("tasks")
        return inner if isinstance(inner, list) else list(data.values())
    return data


def normalize_args(usage_spec: dict) -> list[dict]:
    """Flatten mise's usage_spec into a UI-renderable parameter list."""
    out = []
    for a in (usage_spec.get("cmd") or {}).get("args") or []:
        default = a.get("default")
        if isinstance(default, list):
            default = default[0] if default else None
        out.append({
            "name": a.get("name"),
            "help": a.get("help") or "",
            "required": bool(a.get("required")),
            "default": default,
            "variadic": bool(a.get("var")),
        })
    return out


def usage_for(name: str) -> tuple[str, list[dict]]:
    try:
        info = mise_json("tasks", "info", name, "--json")
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return name, []
    return name, normalize_args(info.get("usage_spec") or {})


def main() -> int:
    tasks = [t for t in task_list() if isinstance(t, dict)]
    meta = collect()

    # ~20ms per call, so fan out rather than paying 115x sequentially.
    with ThreadPoolExecutor(max_workers=16) as ex:
        arg_map = dict(ex.map(usage_for, [t["name"] for t in tasks]))

    entries = []
    for task in sorted(tasks, key=lambda t: t["name"]):
        name = task["name"]
        m = meta.get(name, {})
        args = arg_map.get(name, [])
        entries.append({
            "name": name,
            "description": task.get("description") or "",
            "category": name.split(":")[0] if ":" in name else "root",
            "aliases": task.get("aliases") or [],
            "args": args,
            # Everything a launcher needs to run this safely.
            "execution": {
                "command": ["mise", "run", name],
                # `raw`/`interactive` tasks hand the TTY to a child process, so
                # a GUI must open a terminal instead of capturing stdout.
                "needs_tty": bool(m.get("interactive")),
                # mise aborts a `confirm` task when there is no TTY to ask on
                # ("nobody to ask; pass --yes"). A UI must therefore present its
                # own confirmation and then pass --yes.
                "needs_confirmation": bool(m.get("requires_confirm")),
                "confirm_bypass_flag": "--yes" if m.get("requires_confirm") else None,
                # "caller" means the task acts on the invoking directory
                # (dir = "{{cwd}}"), so a UI must supply one explicitly.
                "cwd_scope": m.get("cwd_scope", "project"),
                "requires_sudo": bool(m.get("requires_sudo")),
            },
            "meta": m,
            "mise": task,
        })

    print(json.dumps({
        "schema_version": SCHEMA_VERSION,
        "project": "mise-task-blueprint",
        "task_count": len(entries),
        "tasks": entries,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
