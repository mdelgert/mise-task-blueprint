# Task Naming

Use a stable colon-delimited command API:

```text
<category>:<group>:<action>
```

Examples:

```text
system:info
system:logs:boot-errors
system:pkg:install-core
network:http:weather
docker:container:shell
docker:compose:up
dev:metadata:python
dev:ssh:keygen
omarchy:hypr:monitors
```

Folders organize source. Task names define the CLI.

Moving a TOML file should not silently rename the public task.
