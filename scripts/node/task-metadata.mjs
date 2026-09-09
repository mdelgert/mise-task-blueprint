#!/usr/bin/env node
const payload = {
  implementation: "node",
  nodeVersion: process.version,
  taskName: process.env.MISE_TASK_NAME ?? null,
  taskDir: process.env.MISE_TASK_DIR ?? null,
  projectRoot: process.env.MISE_PROJECT_ROOT ?? null,
  originalCwd: process.env.MISE_ORIGINAL_CWD ?? null,
  cwd: process.cwd(),
};

console.log(JSON.stringify(payload, null, 2));
