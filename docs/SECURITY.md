# Security

Mise config and tasks are executable configuration.

## Review flow

Before trusting a new task:

```bash
mise tasks ls
mise tasks info <task>
```

Then inspect any referenced `file = "scripts/..."`.

## Blueprint policy

- Destructive tasks require explicit names and confirmation.
- No hard-coded credentials.
- No task prints private keys or auth tokens.
- SSH and age key generators refuse to overwrite existing keys.
- SOPS demos use fake data.
- No `curl ... | sh`.
- Package installation is explicit and uses the detected OS package manager.
- GitHub auth uses `gh auth login`.
- A local random secret is never misrepresented as a GitHub PAT.
- AI-generated tasks that use `sudo`, package installation, deletion, SSH, firewall, credentials, services, or arbitrary downloads require review.

## Confirmation is not self-enforcing outside a terminal

`confirm` only protects a task when something can be asked. Without a TTY mise
refuses to run the task at all:

```
$ mise run docker:prune < /dev/null
[docker:prune] ERROR task requires confirmation but there was nobody to ask; pass --yes to accept
```

`--yes` clears that, but it clears it for the whole invocation. Automation or a
GUI that adds `--yes` blanket-style has disabled every confirmation in this
repository, including:

- `docker:prune:all`
- `docker:ubuntu:remove`
- `system:pkg:update`
- `ai:claude`, `ai:copilot`, `ai:codex` -- each runs an agent with its own
  approval/permission gate bypassed

A non-interactive caller must therefore present its own confirmation before
passing `--yes`. It can identify which tasks need one by reading
`requires_confirm` from the sidecar metadata (or `execution.needs_confirmation`
in `mise dev:catalog:json`), because mise does not report `confirm` in any
`--json` output. `tools/validate-blueprint.py` enforces that the flag matches
reality; see `docs/PLUGIN-CONTRACT.md`.

## Metadata is a safety surface

`requires_confirm`, `destructive`, `requires_sudo` and `risk` are what a UI uses
to decide how loudly to warn. A wrong value is a security defect, not a cosmetic
one, so they are validated rather than trusted:

- `destructive = true` must carry `confirm` and `risk = "high"`
- `requires_sudo = true` cannot be `risk = "low"`
- `requires_confirm` must match the task's actual `confirm`
