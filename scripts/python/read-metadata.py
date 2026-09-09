from pathlib import Path
import tomllib

root = Path(__file__).resolve().parents[1]
data = tomllib.loads((root / "mise.toml").read_text())

print("Structured metadata from [_]:")
for name, metadata in data.get("_", {}).get("task_metadata", {}).items():
    print(name, metadata)

print("\nCustom file-task comments:")
for line in (root / "mise-tasks" / "screen-timeout").read_text().splitlines():
    if line.startswith("#ACTION "):
        print(line.removeprefix("#ACTION "))
