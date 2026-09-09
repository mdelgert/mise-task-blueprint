#!/usr/bin/env python3
"""Validate the blueprint without executing any task.

Three layers:

1. Syntax    -- every TOML parses; every referenced script exists and compiles.
2. Schema    -- every task has the required [_.tasks.*] metadata fields, with
                the right types and allowed values.
3. Invariants-- metadata must agree with the task it describes. This is the
                layer that matters for a UI: `mise tasks ls --json` does not
                expose `confirm`, so a consumer has to trust the sidecar's
                `requires_confirm`/`destructive` fields. Nothing else keeps
                them honest.

Usage:
    python tools/validate-blueprint.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TASK_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*(:[a-z0-9][a-z0-9-]*)*$")

# Shell positional parameters. Deliberately does NOT match a bare `$1`, which
# would false-positive on awk programs inside single quotes (see menu.sh).
POSITIONAL_RE = re.compile(r"\$\{[1-9]|\$#")

RISK_VALUES = {"low", "medium", "high"}
CWD_SCOPE_VALUES = {"caller", "project"}

# field -> (type, allowed values or None)
META_SCHEMA: dict[str, tuple[type | tuple[type, ...], set[str] | None]] = {
    "icon": (str, None),
    "risk": (str, RISK_VALUES),
    "enabled": (bool, None),
    "tags": (list, None),
    "category": (str, None),
    "destructive": (bool, None),
    "requires_confirm": (bool, None),
    "requires_sudo": (bool, None),
    "interactive": (bool, None),
    "cwd_scope": (str, CWD_SCOPE_VALUES),
}

errors: list[str] = []
notes: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def read(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# 1. Load tasks and metadata
# ---------------------------------------------------------------------------
tasks: dict[str, dict] = {}          # name -> task config
task_origin: dict[str, str] = {}     # name -> file it came from
meta: dict[str, dict] = {}           # name -> metadata

try:
    root_cfg = read(ROOT / "mise.toml")
    for name, cfg in root_cfg.get("tasks", {}).items():
        tasks[name] = cfg
        task_origin[name] = "mise.toml"
    meta.update(root_cfg.get("_", {}).get("tasks", {}))
    print("OK   mise.toml")
except Exception as exc:
    err(f"mise.toml: {exc}")

task_files = sorted(p for p in (ROOT / "tasks").rglob("*.toml")
                    if not p.name.endswith(".meta.toml"))

for path in task_files:
    try:
        doc = read(path)
    except Exception as exc:
        err(f"{rel(path)}: {exc}")
        continue
    for name, cfg in doc.items():
        if name == "_":
            err(f"{rel(path)}: contains '_' -- included task files may only contain tasks; "
                f"put arbitrary metadata in {path.name[:-5]}.meta.toml")
            continue
        if name in tasks:
            err(f"{rel(path)}: duplicate task '{name}' (also in {task_origin[name]})")
        tasks[name] = cfg
        task_origin[name] = rel(path)
    print(f"OK   {rel(path)}")

    # Every task file must have a sidecar, and vice versa (checked below).
    sidecar = path.with_name(path.name[:-5] + ".meta.toml")
    if not sidecar.exists():
        err(f"{rel(path)}: missing metadata sidecar {sidecar.name}")

for path in sorted((ROOT / "tasks").rglob("*.meta.toml")):
    sibling = path.with_name(path.name[:-10] + ".toml")
    if not sibling.exists():
        err(f"{rel(path)}: orphan sidecar -- no matching {sibling.name}")
    try:
        doc = read(path)
    except Exception as exc:
        err(f"{rel(path)}: {exc}")
        continue
    entries = doc.get("_", {}).get("tasks", {})
    if not entries:
        err(f"{rel(path)}: no [_.tasks.*] metadata found")
    for name, m in entries.items():
        if name in meta:
            err(f"{rel(path)}: duplicate metadata for '{name}'")
        meta[name] = m
    print(f"META {rel(path)}")

# Overlays are not part of the catalog, but they should still be valid TOML.
for path in sorted((ROOT / "examples").rglob("*.toml")):
    try:
        read(path)
        print(f"EX   {rel(path)}")
    except Exception as exc:
        err(f"{rel(path)}: {exc}")

# ---------------------------------------------------------------------------
# 2. Parity
# ---------------------------------------------------------------------------
for name in sorted(set(tasks) - set(meta)):
    err(f"{name}: task has no [_.tasks.\"{name}\"] metadata")
for name in sorted(set(meta) - set(tasks)):
    err(f"{name}: metadata has no matching task")

# ---------------------------------------------------------------------------
# 3. Per-task schema and invariants
# ---------------------------------------------------------------------------
def run_text(cfg: dict) -> str:
    run = cfg.get("run") or ""
    return "\n".join(run) if isinstance(run, list) else str(run)


for name in sorted(tasks):
    cfg = tasks[name]
    where = task_origin[name]

    if not TASK_NAME_RE.match(name):
        err(f"{name} ({where}): task name must be lowercase colon-delimited "
            f"[a-z0-9-], e.g. category:group:action")

    if not str(cfg.get("description", "")).strip():
        err(f"{name} ({where}): missing a non-empty description")

    # `file =` is resolved by mise from the project root, not from the
    # directory holding the included TOML. Enforce that here.
    script: Path | None = None
    if "file" in cfg:
        script = (ROOT / cfg["file"]).resolve()
        if not script.exists():
            err(f"{name} ({where}): referenced file not found: {cfg['file']}")
            script = None

    # `lockfile = true` only records tools from the root [tools] table, not
    # task-scoped ones, so "latest" here is genuinely unpinned and will drift.
    for tool, spec in (cfg.get("tools") or {}).items():
        if spec == "latest":
            err(f"{name} ({where}): tools.{tool} = \"latest\" is unpinned. Task-scoped "
                f"tools are not recorded in mise.lock, so pin a version, e.g. "
                f"{tool} = \"1\"")

    m = meta.get(name)
    if m is None:
        continue

    # -- schema --
    for field, (expected, allowed) in META_SCHEMA.items():
        if field not in m:
            err(f"{name}: metadata missing required field '{field}'")
            continue
        value = m[field]
        if not isinstance(value, expected) or isinstance(value, bool) is not (expected is bool):
            err(f"{name}: metadata field '{field}' must be "
                f"{getattr(expected, '__name__', expected)}, got {type(value).__name__}")
            continue
        if allowed is not None and value not in allowed:
            err(f"{name}: metadata field '{field}' must be one of "
                f"{sorted(allowed)}, got {value!r}")
    if isinstance(m.get("tags"), list) and not all(isinstance(t, str) for t in m["tags"]):
        err(f"{name}: metadata field 'tags' must contain only strings")

    # -- invariants: metadata must describe the real task --
    expected_category = name.split(":")[0] if ":" in name else "root"
    if m.get("category") != expected_category:
        err(f"{name}: category is {m.get('category')!r} but the task name implies "
            f"{expected_category!r} -- category must match the name prefix")

    has_confirm = "confirm" in cfg
    if has_confirm != bool(m.get("requires_confirm")):
        err(f"{name}: confirm={'set' if has_confirm else 'absent'} in {where} but "
            f"requires_confirm={m.get('requires_confirm')} in metadata. A UI cannot see "
            f"`confirm` via mise JSON, so this field is its only signal.")

    if m.get("destructive") and not m.get("requires_confirm"):
        err(f"{name}: destructive = true must be gated by `confirm` in {where}")

    if m.get("destructive") and m.get("risk") != "high":
        err(f"{name}: destructive = true requires risk = \"high\", got {m.get('risk')!r}")

    if m.get("requires_sudo") and m.get("risk") == "low":
        err(f"{name}: requires_sudo = true cannot be risk = \"low\"")

    task_interactive = bool(cfg.get("raw")) or bool(cfg.get("interactive"))
    if task_interactive != bool(m.get("interactive")):
        err(f"{name}: raw/interactive={task_interactive} in {where} but "
            f"interactive={m.get('interactive')} in metadata")

    expected_scope = "caller" if cfg.get("dir") == "{{cwd}}" else "project"
    if m.get("cwd_scope") != expected_scope:
        err(f"{name}: dir={cfg.get('dir')!r} implies cwd_scope={expected_scope!r}, "
            f"got {m.get('cwd_scope')!r}")

    # -- args must be declared so a UI can render inputs --
    inline = run_text(cfg)
    declares_usage = "usage" in cfg
    if script is not None:
        body = script.read_text()
        if POSITIONAL_RE.search(body) and "#USAGE" not in body and not declares_usage:
            err(f"{name}: {cfg['file']} reads positional arguments but declares no "
                f"'#USAGE arg' spec, so no UI can discover its parameters")
    if POSITIONAL_RE.search(inline) and not declares_usage:
        err(f"{name} ({where}): inline run reads positional arguments but the task "
            f"declares no `usage` spec")
    if "$usage_" in inline and not declares_usage:
        err(f"{name} ({where}): inline run reads $usage_* but the task declares no "
            f"`usage` spec")
    # A usage spec on an inline `run` makes $1/$2 empty -- args arrive only as
    # $usage_<name>. Catch the mix that silently produces empty values.
    if declares_usage and re.search(r"\$\{?[1-9]", inline):
        err(f"{name} ({where}): task declares `usage` but the inline run still reads "
            f"$1/$2. With a usage spec mise passes args as $usage_<name> only; "
            f"positionals are empty.")

# ---------------------------------------------------------------------------
# 4. Script health
# ---------------------------------------------------------------------------
bash_scripts = sorted((ROOT / "scripts" / "bash").glob("*.sh"))
for path in bash_scripts:
    p = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
    if p.returncode:
        err(f"bash -n {rel(path)}: {p.stderr.strip()}")

if shutil.which("shellcheck"):
    p = subprocess.run(["shellcheck", "--severity=warning", *map(str, bash_scripts)],
                       capture_output=True, text=True)
    if p.returncode:
        err("shellcheck:\n" + (p.stdout or p.stderr).strip())
else:
    notes.append("shellcheck not installed -- only `bash -n` syntax checks ran")

for path in sorted((ROOT / "scripts" / "python").glob("*.py")):
    p = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                       capture_output=True, text=True)
    if p.returncode:
        err(f"py_compile {rel(path)}: {p.stderr.strip()}")

if shutil.which("node"):
    for path in sorted((ROOT / "scripts" / "node").glob("*.mjs")):
        p = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
        if p.returncode:
            err(f"node --check {rel(path)}: {p.stderr.strip()}")
else:
    notes.append("node not installed -- .mjs scripts were not syntax-checked")

# ---------------------------------------------------------------------------
# 5. Reporting helpers
# ---------------------------------------------------------------------------
def declared_args(name: str) -> bool:
    cfg = tasks[name]
    if "usage" in cfg:
        return True
    if "file" in cfg:
        script = (ROOT / cfg["file"])
        return script.exists() and "#USAGE" in script.read_text()
    return False


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if errors:
    print(f"\nVALIDATION FAILED ({len(errors)} error(s))", file=sys.stderr)
    for e in errors:
        print(f" - {e}", file=sys.stderr)
    raise SystemExit(1)

print()
print(f"Tasks:            {len(tasks)}")
print(f"Metadata entries: {len(meta)}")
print(f"Declared args:    {sum(1 for n in tasks if declared_args(n))} task(s)")
print(f"Confirm-gated:    {sum(1 for m in meta.values() if m.get('requires_confirm'))} task(s)")
print("Schema:           OK")
print("Invariants:       OK")
print("Validation:       PASS")
for n in notes:
    print(f"note: {n}")
print()
print("Next:")
print("  mise tasks validate")
print("  mise tasks ls")
print("  mise dev:catalog:json")
