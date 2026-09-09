#!/usr/bin/env python3
"""Check the live catalog against schemas/, so the published contract cannot drift.

tools/validate-blueprint.py checks the TOML sources and needs nothing but the
standard library. This script closes the other half of the loop: it runs the
real catalog generator and asserts the output still matches
schemas/catalog.schema.json, and that every sidecar entry still matches
schemas/task-metadata.schema.json.

Requires `jsonschema`. Skips with a clear message if it is unavailable, so it
never blocks a local run that only wanted the stdlib validator.

Pass --require to turn that skip into a failure. CI uses it, because a check
that silently skips is worse than no check: note that `tools = { python =
"3.14" }` means this runs under mise's Python, not the system one, so
`pip install` must target the same interpreter.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRE = "--require" in sys.argv[1:]

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ModuleNotFoundError:
    msg = (f"jsonschema not installed for {sys.executable}\n"
           f"      install it there with: "
           f"mise exec python@3.14 -- python -m pip install jsonschema")
    if REQUIRE:
        print(f"FAIL  {msg}", file=sys.stderr)
        raise SystemExit(1)
    print(f"SKIP  {msg}")
    raise SystemExit(0)


def load(path: Path) -> dict:
    return json.loads(path.read_text())


catalog_schema = load(ROOT / "schemas" / "catalog.schema.json")
meta_schema = load(ROOT / "schemas" / "task-metadata.schema.json")

# catalog.schema.json $refs the metadata schema by relative path.
registry = Registry().with_resources([
    ("./task-metadata.schema.json", Resource.from_contents(meta_schema)),
    (meta_schema["$id"], Resource.from_contents(meta_schema)),
])

failures = 0

# --- the generated catalog -------------------------------------------------
proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "python" / "catalog_json.py")],
                      cwd=ROOT, capture_output=True, text=True)
if proc.returncode:
    print(f"FAIL  catalog_json.py exited {proc.returncode}:\n{proc.stderr.strip()}",
          file=sys.stderr)
    raise SystemExit(1)

catalog = json.loads(proc.stdout)
errors = sorted(Draft202012Validator(catalog_schema, registry=registry).iter_errors(catalog),
                key=lambda e: list(e.path))
if errors:
    failures += len(errors)
    print(f"FAIL  catalog does not match schemas/catalog.schema.json "
          f"({len(errors)} error(s))", file=sys.stderr)
    for e in errors[:20]:
        path = "/".join(str(x) for x in e.path) or "<root>"
        print(f"  - {path}: {e.message}", file=sys.stderr)
else:
    print(f"OK    catalog matches catalog.schema.json ({catalog['task_count']} tasks)")

# --- every sidecar entry ---------------------------------------------------
meta_validator = Draft202012Validator(meta_schema)
checked = 0
for path in sorted(ROOT.glob("tasks/**/*.meta.toml")):
    with path.open("rb") as f:
        doc = tomllib.load(f)
    for name, entry in doc.get("_", {}).get("tasks", {}).items():
        checked += 1
        for e in meta_validator.iter_errors(entry):
            failures += 1
            print(f"FAIL  {name}: {e.message}", file=sys.stderr)

if not failures:
    print(f"OK    {checked} sidecar entries match task-metadata.schema.json")
    print("Schema conformance: PASS")
    raise SystemExit(0)

print(f"\nSCHEMA CONFORMANCE FAILED ({failures} error(s))", file=sys.stderr)
raise SystemExit(1)
