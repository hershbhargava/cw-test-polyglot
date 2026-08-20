# Technical Design Document — cw-test-polyglot

> **Mode:** Reverse-engineered (documents what **IS**, from the code).
> **Iteration:** 2 · **Issue:** [#1](https://github.com/hershbhargava/cw-test-polyglot/issues/1)
> **Branch:** `feature/issue-1` (base `main`).
>
> This is the master document; it summarizes the as-built architecture and references
> the technical sub-documents under `technical/`.

## 1. Purpose & context

`cw-test-polyglot` is a deliberately minimal **polyglot** application for CoWeave
brownfield SDLC testing (`README.md`, referencing #120 / dev-bug 093). It pairs a
Python/Flask backend with a JavaScript/React frontend, each carrying its **own** test
runner, so that a correct QA manifest must run **both**. The app's real purpose is to
exercise a multi-runner QA pipeline; its functional surface is a single arithmetic
operation (addition) mirrored across both stacks.

Open issue #1 ("Add a multiply operation to backend and frontend") requests a second
operation; the reconstructed product intent for that change lives in
`docs/requirements/PRD_DELTA_issue-1.md`. **This TDD documents the code as it exists
today and does not implement or design #1.**

## 2. System overview

| Layer | Tech | Entry / key file | Tests |
|-------|------|------------------|-------|
| Backend | Python 3, Flask 3.0.0 | `backend/app.py` | pytest 8.0.0 — `backend/test_app.py` |
| Frontend | JavaScript (ESM), React 18 deps | `frontend/src/sum.js` | Vitest 1.2.0 — `frontend/src/sum.test.js` |
| QA harness | Docker Compose + CoWeave manifest | `docker-compose.yml`, `.coweave/manifest.yml` | runs both of the above |

```
┌──────────────────────┐        ┌──────────────────────────┐
│  Backend (Flask)     │        │  Frontend (ES module)    │
│  backend/app.py      │        │  frontend/src/sum.js     │
│   add(a,b)           │        │   sum(a,b)               │
│   GET /api/sum/a/b   │        │   (no network, no UI)    │
│   → {"result": a+b}  │        │                          │
│  tests: test_app.py  │        │  tests: sum.test.js      │
└──────────┬───────────┘        └───────────┬──────────────┘
           │                                │
           └───────── independent; not wired together ───────┘
                         │
              QA harness runs BOTH runners
        (.coweave/manifest.yml + docker-compose.yml)
```

Full detail: `technical/SYSTEM_ARCHITECTURE.md`.

## 3. Backend design (as-built)

- `backend/app.py`:
  - `app = Flask(__name__)`.
  - `add(a, b)` → `a + b` (`app.py → add`), a pure function.
  - `@app.route("/api/sum/<int:a>/<int:b>")` handler `sum_route` returns
    `jsonify({"result": add(a, b)})` (`app.py → sum_route`).
  - `app.run()` under `__main__` — Flask dev server, default `127.0.0.1:5000`.
- `backend/test_app.py`: `test_add` (`add(2,3)==5`) and `test_add_negative`
  (`add(-1,1)==0`). Tests target the pure function, not the HTTP layer.
- `backend/requirements.txt`: `flask==3.0.0`, `pytest==8.0.0` (exact-pinned).

## 4. Frontend design (as-built)

- `frontend/src/sum.js`: named export `sum(a, b)` → `a + b` (`sum.js → sum`). No JSX,
  no React component, no DOM entrypoint despite `react`/`react-dom` being declared.
- `frontend/src/sum.test.js`: Vitest `describe('sum', …)` asserting `(2,3)→5` and
  `(-1,1)→0`.
- `frontend/vite.config.js`: `defineConfig({ test: { environment: 'node' } })` — Vitest
  runs in Node, not a browser DOM.
- `frontend/package.json`: scripts `dev`/`build`/`test`; deps `react`, `react-dom`;
  devDeps `vite`, `vitest` (caret ranges; no committed lockfile).

## 5. Data & persistence

**Not applicable — this codebase has no persistence layer.** There are no databases,
ORMs, models, migrations, schema/DDL files, or seed scripts anywhere in the tree. The
application is entirely stateless; every response is computed on the fly. A dedicated
`DATABASE_SCHEMA.md` is intentionally **not** produced (write-if-substantive), since it
would contain no real content.

## 6. API surface

One endpoint: `GET /api/sum/<int:a>/<int:b>` → `200 {"result": <int>}`. Errors are
Flask/Werkzeug defaults (`404` for non-matching path incl. non-integer or negative
segments; `405` for wrong method); there is no custom error handler or validation
layer. The frontend exposes no HTTP API. Full request/response and status semantics:
`technical/API_CONTRACTS.md`.

## 7. Security posture

No authentication, authorization, secrets, or persisted data. The only implicit control
is the `<int:...>` URL converter that rejects non-integer/negative path segments; output
is JSON-encoded via `jsonify`. Dev server is plain HTTP on loopback by default; no CORS,
rate limiting, or security headers. `.coweave/manifest.yml` declares `secrets: []`. Full
threat model: `technical/SECURITY_DESIGN.md`.

## 8. Deployment & QA

No production pipeline, CI workflow, IaC, or k8s manifests exist. The real infra is a
test harness: `docker-compose.yml` provisions two idle containers (`python:3.11-slim`,
`node:20-slim`) with source bind-mounted, and `.coweave/manifest.yml` runs `pytest`
(backend) and `npm test` (frontend) into them — satisfying the "run both" requirement.
Full detail: `technical/DEPLOYMENT_STRATEGY.md`.

## 9. Observations & Risks (as-built — not fixed here)

| # | Observation | Where | Impact |
|---|-------------|-------|--------|
| O1 | HTTP route can't reach negative sums: the default `int` converter rejects `-`, so `/api/sum/-1/1` returns `404` even though `add(-1,1)` is a supported, tested case. | `app.py → sum_route`; `test_app.py → test_add_negative` | API/behavior mismatch between pure function and HTTP surface. |
| O2 | Backend HTTP route is untested — tests only cover the pure `add`, not `sum_route`. | `test_app.py` | Route regressions would go undetected by the suite. |
| O3 | Frontend `sum.js` is not wired to the backend; `react`/`react-dom` are declared but unused (no component/DOM). | `frontend/src/`, `package.json` | Dead dependencies; "React" is nominal only. |
| O4 | No committed frontend lockfile (`package-lock.json` absent); deps use caret ranges. | `package.json`, `.gitignore` | Non-reproducible frontend builds/tests. |
| O5 | QA manifest defines no dependency-install step; slim base images lack Flask/pytest and node_modules. | `.coweave/manifest.yml`, `docker-compose.yml` | Tests may fail unless the harness injects `pip install` / `npm install`. |
| O6 | `.coweave/manifest.yml` and `docker-compose.yml` are present in git HEAD but shown deleted in the working tree during this run. | `git status` | Harness config may be inadvertently removed; reconcile before relying on it. |
| O7 | Flask dev server (`app.run()`) is used with no production WSGI server, TLS, or hardening. | `app.py` | Fine for a demo; not production-ready. |

These are **descriptive** observations of the current implementation, appropriate to a
demo/test repository. They are recorded per the reverse-engineering ground rules (note
gaps, do not silently "fix" them in docs).

## 10. Related documents

- `technical/SYSTEM_ARCHITECTURE.md` — component boundaries & topology.
- `technical/API_CONTRACTS.md` — the single HTTP endpoint.
- `technical/SECURITY_DESIGN.md` — threat surface & controls (mostly absent by design).
- `technical/DEPLOYMENT_STRATEGY.md` — build/ship/run & the compose test harness.
- `docs/requirements/PRD_DELTA_issue-1.md` — product intent for the (not-yet-built) multiply change.
- *(DATABASE_SCHEMA.md intentionally omitted — no persistence layer.)*

## 11. Coverage

This repository is tiny (7 source/config files across 2 components plus the QA harness)
and was **fully covered in this run**. See the coverage ledger in
`work-in-progress/issue-1/external-memory/prd/iteration-2/metadata.json`.
