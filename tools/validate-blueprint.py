#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
errors = []
task_names = set()
meta_names = set()

def load(path):
    with path.open("rb") as f:
        return tomllib.load(f)

# Root config.
try:
    root_cfg = load(ROOT / "mise.toml")
    meta_names.update(root_cfg.get("_", {}).get("tasks", {}).keys())
    task_names.update(root_cfg.get("tasks", {}).keys())
    print("OK   mise.toml")
except Exception as exc:
    errors.append(f"mise.toml: {exc}")

# Included executable task files.
for path in sorted((ROOT / "tasks").rglob("*.toml")):
    if path.name.endswith(".meta.toml"):
        continue
    try:
        doc = load(path)
        for name, cfg in doc.items():
            if name == "_":
                errors.append(f"{path.relative_to(ROOT)} contains '_' but included task TOMLs must contain tasks only")
            task_names.add(name)
            if isinstance(cfg, dict) and "file" in cfg:
                # mise resolves `file =` in included task TOMLs relative to the
                # project root (where mise.toml lives), not the included file's dir.
                target = (ROOT / cfg["file"]).resolve()
                if not target.exists():
                    errors.append(f"{name}: referenced file not found: {target}")
        print(f"OK   {path.relative_to(ROOT)}")
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")

# Sidecar arbitrary metadata.
for path in sorted((ROOT / "tasks").rglob("*.meta.toml")):
    try:
        doc = load(path)
        names = doc.get("_", {}).get("tasks", {})
        if not names:
            errors.append(f"{path.relative_to(ROOT)}: no [_.tasks.*] metadata found")
        meta_names.update(names.keys())
        print(f"META {path.relative_to(ROOT)}")
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")

missing_meta = sorted(task_names - meta_names)
orphan_meta = sorted(meta_names - task_names)

if missing_meta:
    errors.append("Tasks missing custom metadata: " + ", ".join(missing_meta))
if orphan_meta:
    errors.append("Metadata without matching tasks: " + ", ".join(orphan_meta))

for path in sorted((ROOT / "scripts" / "bash").glob("*.sh")):
    p = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
    if p.returncode:
        errors.append(f"Bash syntax {path.relative_to(ROOT)}: {p.stderr}")

for path in sorted((ROOT / "scripts" / "python").glob("*.py")):
    p = subprocess.run([sys.executable, "-m", "py_compile", str(path)], capture_output=True, text=True)
    if p.returncode:
        errors.append(f"Python syntax {path.relative_to(ROOT)}: {p.stderr}")

if errors:
    print("\nVALIDATION FAILED", file=sys.stderr)
    for e in errors:
        print(f" - {e}", file=sys.stderr)
    raise SystemExit(1)

print()
print(f"Tasks:          {len(task_names)}")
print(f"Metadata sets:  {len(meta_names)}")
print("Task/meta map:  100% matched")
print("Validation:     PASS")
print()
print("Next:")
print("  mise tasks validate")
print("  mise tasks ls")
print("  mise development:metadata:all:python")
print("  mise development:catalog:json")
