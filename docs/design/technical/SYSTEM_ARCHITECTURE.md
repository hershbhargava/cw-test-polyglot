# System Architecture — cw-test-polyglot (as-built)

> **Reverse-engineered** from the actual code in this repository. Documents what
> **IS**, not what should be. Iteration 2.

## 1. Overview

`cw-test-polyglot` is a deliberately minimal **polyglot** demonstration application
used for CoWeave brownfield SDLC testing (per `README.md`, referencing #120 / dev-bug
093). It consists of two independent, unconnected components, each written in a
different language ecosystem and each carrying its own test runner:

| Component | Language / Runtime | Framework | Test runner | Source dir |
|-----------|--------------------|-----------|-------------|------------|
| Backend   | Python 3           | Flask 3.0.0 | pytest 8.0.0 | `backend/` |
| Frontend  | JavaScript (ESM)   | React 18 (deps only) | Vitest 1.2.0 | `frontend/` |

The stated purpose in `README.md`: *"Both components have their own test runner; a
correct QA manifest must run **both**."* The architecture therefore exists primarily
to exercise a multi-runner QA pipeline, not to serve production traffic.

## 2. Component decomposition

### 2.1 Backend (`backend/`)

- **Entrypoint / app module:** `backend/app.py`.
  - Constructs a Flask application: `app = Flask(__name__)` (`app.py`).
  - Defines a pure arithmetic helper `add(a, b)` returning `a + b` (`app.py → add`).
  - Exposes one HTTP route, `sum_route`, decorated with
    `@app.route("/api/sum/<int:a>/<int:b>")`, returning
    `jsonify({"result": add(a, b)})` (`app.py → sum_route`).
  - Runs a development server under `if __name__ == "__main__": app.run()`
    (`app.py`) — i.e. Flask's built-in server on its default host/port (`127.0.0.1:5000`).
- **Tests:** `backend/test_app.py` imports `add` directly and asserts
  `add(2, 3) == 5` (`test_app.py → test_add`) and `add(-1, 1) == 0`
  (`test_app.py → test_add_negative`). Tests exercise the pure function, **not** the
  HTTP route.
- **Dependencies:** `backend/requirements.txt` pins `flask==3.0.0` and `pytest==8.0.0`.

### 2.2 Frontend (`frontend/`)

- **Module:** `frontend/src/sum.js` exports a single named function
  `sum(a, b)` returning `a + b` (`sum.js → sum`). This is a plain ES module; there is
  **no rendered React component, JSX, or DOM entrypoint** in the tree despite `react`
  / `react-dom` being declared as dependencies in `package.json`.
- **Tests:** `frontend/src/sum.test.js` (Vitest) imports `sum` and asserts
  `sum(2, 3)` is `5` and `sum(-1, 1)` is `0` inside a `describe('sum', …)` block.
- **Build/test config:** `frontend/vite.config.js` calls
  `defineConfig({ test: { environment: 'node' } })` — Vitest runs in a **Node**
  environment (no jsdom/browser DOM).
- **Scripts** (`frontend/package.json`): `dev` → `vite`, `build` → `vite build`,
  `test` → `vitest run`.
- **Dependencies:** runtime `react ^18.2.0`, `react-dom ^18.2.0`; dev `vite ^5.0.0`,
  `vitest ^1.2.0`.

## 3. Wiring & data flow

There is **no** inter-component wiring. The frontend does **not** call the backend
route; `sum.js` computes locally. The two components share only a naming convention
(an arithmetic operation + parallel tests) and a common QA harness. The only runtime
data flow that exists at all is the backend HTTP path:

```
HTTP GET /api/sum/<int:a>/<int:b>
        │
        ▼
  Flask route sum_route(a, b)   (backend/app.py)
        │  a, b coerced to int by the <int:...> URL converter
        ▼
  add(a, b) → a + b
        │
        ▼
  jsonify({"result": <int>})  → 200 application/json
```

## 4. QA / test harness topology

The QA harness is described by `.coweave/manifest.yml` (`apiVersion:
coweave.ai/v2`, `kind: TestEnvironment`) and `docker-compose.yml`:

- **`docker-compose.yml`** defines two idle service containers:
  - `backend`: image `python:3.11-slim`, `working_dir: /app`, bind-mounts
    `./backend:/app`, `command: sleep infinity`.
  - `frontend`: image `node:20-slim`, `working_dir: /app`, bind-mounts
    `./frontend:/app`, `command: sleep infinity`.
  - Both idle (`sleep infinity`); tests are executed *into* the containers by the
    harness rather than as the container command.
- **`.coweave/manifest.yml`** (`spec.tests`) declares two components:
  - `backend` → service `backend`, `workingDir: backend`, `command: pytest`.
  - `frontend` → service `frontend`, `workingDir: frontend`, `command: npm test`.
  - Environment: `PYTHONDONTWRITEBYTECODE=1`, `NODE_ENV=test`.
  - `secrets: []`, `requiredServices: []` — no secrets or external services.

> Note: at the time of this run both `.coweave/manifest.yml` and
> `docker-compose.yml` were tracked in git HEAD but showed as deleted in the working
> tree (`git status`). This doc describes their committed content. See TDD
> "Observations & Risks".

## 5. Deployment topology

There is no production deployment target defined in the repo. Runtime surfaces are:

- **Backend dev server** via `python app.py` (`app.run()` default `127.0.0.1:5000`).
- **Frontend dev/build** via `vite` / `vite build` (scripts in `package.json`); no
  built artifact or server is committed, and `dist/` is git-ignored (`.gitignore`).
- **Containerized test execution** via the compose file above (test-only, not a
  serving topology).

## 6. Key architectural characteristics (as-built)

- **Stateless.** No database, cache, session store, or persistence layer anywhere in
  the tree (confirmed: no models, migrations, ORM, or DB drivers). See
  `DATABASE_SCHEMA` note in the TDD — *not applicable*.
- **No auth.** No authentication, authorization, or user model exists.
- **Two independent runtimes.** Python and Node are decoupled; the "polyglot" nature
  is the point of the repo, not an accident.
- **Test-parity convention.** Each operation is mirrored across both stacks with its
  own runner, and the QA manifest must run both (`README.md`).

## Related documents
- `API_CONTRACTS.md` — the single HTTP endpoint.
- `SECURITY_DESIGN.md` — threat surface and (absence of) controls.
- `DEPLOYMENT_STRATEGY.md` — build/ship/run and the compose test harness.
- `../TDD.md` — master technical design document.
