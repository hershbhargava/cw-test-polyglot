# Deployment & Infrastructure — cw-test-polyglot (as-built)

> **Reverse-engineered** from the actual manifests, config, and scripts. Documents how
> the app is really built, tested, and run today. Iteration 2.

## 1. Summary

There is **no production deployment pipeline** in this repository. The only
infrastructure that exists is a **test/QA harness** driven by CoWeave's manifest plus a
Docker Compose file that provisions two idle containers into which the test commands
are executed. No CI workflow files (`.github/`), IaC (Terraform/CloudFormation), or
Kubernetes manifests are present in the tree.

## 2. Build

### 2.1 Backend
- **No build step.** Python is interpreted. Dependencies are installed from
  `backend/requirements.txt` (`flask==3.0.0`, `pytest==8.0.0`).
- **Run (dev):** `python backend/app.py` starts Flask's built-in dev server via
  `app.run()` (`app.py`), default `127.0.0.1:5000`.

### 2.2 Frontend
- **Build:** `npm run build` → `vite build` (`frontend/package.json` scripts). Output
  would land in `dist/`, which is git-ignored (`.gitignore`). No built artifact is
  committed.
- **Dev:** `npm run dev` → `vite`.
- **No committed lockfile** (`package-lock.json` absent) — dependency resolution is
  not pinned for reproducible builds.

## 3. Test execution (the real "deployment" surface)

Defined by `.coweave/manifest.yml` (`apiVersion: coweave.ai/v2`,
`kind: TestEnvironment`) and `docker-compose.yml`.

### 3.1 Compose services (`docker-compose.yml`)

```yaml
services:
  backend:
    image: python:3.11-slim
    working_dir: /app
    volumes: [ ./backend:/app ]
    command: sleep infinity
  frontend:
    image: node:20-slim
    working_dir: /app
    volumes: [ ./frontend:/app ]
    command: sleep infinity
```

- Both containers idle (`sleep infinity`); the harness `exec`s test commands into them.
- Source is bind-mounted, not baked into an image.
- No published ports, no networks, no depends_on — the two services are independent.

### 3.2 Test commands (`.coweave/manifest.yml → spec.tests`)

| Component | Service | Working dir | Command |
|-----------|---------|-------------|---------|
| backend   | `backend`  | `backend`  | `pytest` |
| frontend  | `frontend` | `frontend` | `npm test` (`vitest run`) |

- Top-level `spec.tests.command: pytest`, `timeoutSec: 600`.
- Environment: `PYTHONDONTWRITEBYTECODE=1`, `NODE_ENV=test`.
- `spec.stack: other`; `secrets: []`; `requiredServices: []`.
- This satisfies the `README.md` requirement that a correct QA manifest **runs both**
  runners.

> Prerequisite gap: the manifest runs `pytest` / `npm test` but defines **no explicit
> dependency-install step** (`pip install -r requirements.txt`, `npm install`). The
> base images (`python:3.11-slim`, `node:20-slim`) do not ship Flask/pytest or the
> node_modules, so an install step must be supplied by the harness for tests to pass.
> Recorded in the TDD "Observations & Risks".

## 4. Configuration & environment

- **Config:** No config files, `.env`, or settings module. The app reads no
  environment variables in application code (`app.py` uses none).
- **Test env vars:** only the two non-sensitive vars above, set by the manifest.
- **Ports:** Flask dev server default `5000` (not published via compose).

## 5. Observability

- **None implemented.** No logging configuration, metrics, tracing, or health-check
  endpoint exists in the code. Flask's default request log is the only runtime output
  when the dev server runs.

## 6. Rollout & rollback

- **Rollout:** Not applicable — there is no deploy target. "Shipping" is limited to
  running tests in the compose harness and (optionally) starting the dev servers
  locally.
- **Rollback:** A git revert of the relevant commit fully undoes any change; the app
  is stateless with no migrations, so revert has no data side effects (consistent with
  `PRD_DELTA_issue-1.md §7`).

## 7. Working-tree note

At the time of this reverse-engineering run, `git status` showed `.coweave/manifest.yml`
and `docker-compose.yml` as **deleted in the working tree** though still present in git
HEAD. This document describes the committed (HEAD) content of those files. If they are
intended to remain part of the harness, their deletion should be reconciled. Recorded
in the TDD "Observations & Risks".

## Related documents
- `SYSTEM_ARCHITECTURE.md` — component/topology overview.
- `SECURITY_DESIGN.md` — secrets and transport posture.
- `../TDD.md` — master technical design document.
