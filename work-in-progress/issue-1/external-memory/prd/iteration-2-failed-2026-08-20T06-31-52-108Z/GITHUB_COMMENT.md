## 🛠️ QA Manifest Author Iteration 2 — cw-test-polyglot

**Repo**: `hershbhargava/cw-test-polyglot`
**Stack**: `unknown` (polyglot: python + node)
**Manifest path**: `.coweave/manifest.yml` (NOT written — skipped)

### What this iteration produced

No manifest was authored. The coweave-infra v2 schema requires `spec.entrypoint` to be exactly `compose` or `helm`, but this repository contains **no docker-compose file and no Helm chart** (verified: repo root has only `backend/`, `frontend/`, `docs/`, README, .gitignore — no compose/chart, no `.coweave/`). With no test-environment source, a schema-valid manifest cannot be produced.

### Blocking gap

| Requirement | State |
|---|---|
| `spec.entrypoint.compose.file` | ❌ no compose file in repo |
| `spec.entrypoint.helm.chart` | ❌ no Helm chart in repo |
| Test commands (per component) | ✅ known: `backend` → `pytest`, `frontend` → `npm test` |

### Validation

- Schema validation: ⏭️ not attempted — `# SKIPPED: no-test-env-source`
- Validation iterations: 0

### Next step

An operator (or an infra-provisioning workflow) must add a `docker-compose.yml` defining `backend` (python/pytest) and `frontend` (node/npm test) services. Once a compose file exists, re-run this workflow to author a polyglot manifest with `spec.tests.components[]` for both containers.
