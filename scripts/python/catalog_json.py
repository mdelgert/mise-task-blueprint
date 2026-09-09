#!/usr/bin/env python3
"""Merge `mise tasks ls --json` with custom [_.tasks.*] metadata."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("MISE_PROJECT_ROOT") or Path(__file__).resolve().parents[2])
sys.path.insert(0, str(ROOT / "scripts" / "python"))
from catalog_metadata import collect

def mise_tasks():
    p = subprocess.run(
        ["mise", "tasks", "ls", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    data = json.loads(p.stdout)
    # Current mise output is normally a list; support a dict defensively.
    if isinstance(data, dict):
        if "tasks" in data and isinstance(data["tasks"], list):
            return data["tasks"]
        return list(data.values())
    return data

meta = collect()
out = []

for task in mise_tasks():
    if not isinstance(task, dict):
        continue
    name = task.get("name")
    merged = dict(task)
    merged["meta"] = meta.get(name, {})
    out.append(merged)

print(json.dumps(out, indent=2, sort_keys=True))
