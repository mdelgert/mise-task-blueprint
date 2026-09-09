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
