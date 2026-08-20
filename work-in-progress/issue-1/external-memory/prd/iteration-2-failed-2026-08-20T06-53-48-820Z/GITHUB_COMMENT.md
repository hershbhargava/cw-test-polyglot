## 🛠️ QA Manifest Author Iteration 2 — cw-test-polyglot

**Repo**: `hershbhargava/cw-test-polyglot`
**Stack**: `other` (polyglot: python + node)
**Manifest path**: `.coweave/manifest.yml`

### What this iteration produced

Authored a polyglot coweave-infra v2 manifest using the root `docker-compose.yml` (services `backend`, `frontend`). Declared `spec.tests.components[]` so BOTH suites run in their own container: `backend` → `pytest` (workingDir `backend`), `frontend` → `npm test` (workingDir `frontend`). Primary fallback command is `pytest`.

### Manifest body (key fields)

| Field | Value |
|---|---|
| `apiVersion` | `coweave.ai/v2` |
| `stack` | `other` |
| `entrypoint` | `compose` → `./docker-compose.yml` |
| `tests.command` (fallback) | `pytest` |
| component `backend` | service `backend`, workingDir `backend`, `pytest` |
| component `frontend` | service `frontend`, workingDir `frontend`, `npm test` |
| `tests.timeoutSec` | `600` |
| `secrets` (by name) | (none) |

### Validation

- Schema validation: pending coweave-infra `/validate`
- Validation iterations: 1

### Next step

Run qa-test-execution-workflow to confirm both containers install deps and run their suites (frontend needs `npm install`; backend needs `pip install -r requirements.txt`) — the compose services currently start as `sleep infinity`, so the runner must install deps before invoking each component command.
