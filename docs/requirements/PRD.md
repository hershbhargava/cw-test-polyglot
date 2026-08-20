# Product Requirements Document — cw-test-polyglot

> **Mode:** Reverse-engineered (documents what the product **IS**, inferred from the actual code + reconstructed TDDs under `docs/design/`).
> **Iteration:** 2 · **Issue:** [#1](https://github.com/hershbhargava/cw-test-polyglot/issues/1) · **Branch:** `feature/issue-1` (base `main`).
>
> This is a single **combined** PRD across both tiers (Python backend + JavaScript frontend). It describes the product as it exists today. It does **not** specify the not-yet-built multiply change from issue #1 — that product intent lives in `docs/requirements/PRD_DELTA_issue-1.md`.

---

## 1. Executive Summary

`cw-test-polyglot` is a deliberately minimal **polyglot demonstration application** built to exercise CoWeave's brownfield SDLC and multi-runner QA tooling. It pairs two independent components — a Python/Flask backend and a JavaScript/React-dependency frontend — each carrying its **own** test runner, so that a correct QA pipeline must discover and run **both** test suites.

The product's entire functional surface today is a single arithmetic operation, **addition**, mirrored across both stacks:
- The backend exposes an `add(a, b)` function and one HTTP endpoint `GET /api/sum/<int:a>/<int:b>` that returns the sum as JSON (`backend/app.py → add`, `→ sum_route`).
- The frontend exposes a local `sum(a, b)` module function with no network or UI (`frontend/src/sum.js → sum`).

| Layer | Tech in use | Key file | Test runner |
|-------|-------------|----------|-------------|
| Backend | Python 3, Flask 3.0.0 | `backend/app.py` | pytest 8.0.0 (`backend/test_app.py`) |
| Frontend | JavaScript (ESM); React 18 declared but unused | `frontend/src/sum.js` | Vitest 1.2.0 (`frontend/src/sum.test.js`) |
| QA harness | Docker Compose + CoWeave v2 manifest | `docker-compose.yml`, `.coweave/manifest.yml` | runs both of the above |

The value of the product is **not** the arithmetic itself but the **test-parity convention**: a repeatable pattern of "one operation + parallel tests in two ecosystems" that a QA pipeline must correctly execute end-to-end.

---

## 2. Background & Strategic Context

**Problem the product solves (inferred from behavior + `README.md`):** Tooling that only runs one language's tests will silently pass a polyglot repository while leaving half its suites unrun. This app deliberately places two runners (pytest + Vitest) in separate directories so that a QA manifest must run **both** to be correct — surfacing that class of tooling gap.

**Origin:** `README.md` states the app is *"a deliberately polyglot app for CoWeave brownfield SDLC testing (#120 / dev-bug 093)"* and that *"Both components have their own test runner; a correct QA manifest must run both."* The reconstructed TDD (`docs/design/TDD.md §1`) confirms the app's real purpose is to exercise a multi-runner QA pipeline, with its functional surface intentionally kept to a single arithmetic operation.

**Strategic context:** This is an internal test fixture / demonstration repository, not a customer-facing product. There is no market, monetization, or external user base implied by the code. Its "customers" are the CoWeave SDLC workflows (architect, dev, QA, infra) that operate on it.

---

## 3. Goals & Success Metrics

**Inferred product goals:**
- **G1 — Prove multi-runner QA correctness:** a QA manifest must discover and run both the pytest and Vitest suites (`README.md`; `.coweave/manifest.yml → spec.tests.components[]`).
- **G2 — Maintain test parity across stacks:** each arithmetic operation is mirrored on both sides with equivalent test cases (`backend/test_app.py`, `frontend/src/sum.test.js`).
- **G3 — Keep the surface minimal and stateless:** the app stays small enough to reason about completely, with no persistence or external dependencies.

**Success metrics:** The application is **not instrumented** — there are no analytics, metrics, logging configuration, or telemetry in the code (`docs/design/technical/DEPLOYMENT_STRATEGY.md §5`). The only observable success signal is a **binary build/test outcome**: both test suites pass (backend `pytest`: `test_add`, `test_add_negative`; frontend Vitest: `'adds two numbers'`, `'handles negatives'`). No runtime KPIs, usage counts, or SLAs exist.

---

## 4. Target Users & Personas

There is **no authentication, authorization, or user model** anywhere in the code (`docs/design/technical/SECURITY_DESIGN.md §3`). The single HTTP route is fully anonymous. Personas are therefore inferred from *who interacts with the code*, not from in-app roles:

| Persona | How they interact | Evidence |
|---------|-------------------|----------|
| **CoWeave SDLC pipeline / QA harness** | Executes both test suites via the compose containers and CoWeave manifest | `.coweave/manifest.yml`, `docker-compose.yml`, `README.md` |
| **Developer / maintainer** | Runs the dev server, edits the arithmetic functions, adds mirrored tests | `backend/app.py` (`app.run()`), `frontend/package.json` scripts |
| **Anonymous HTTP caller** | Issues `GET /api/sum/<int:a>/<int:b>` and reads the JSON result | `backend/app.py → sum_route` |

No end-user personas beyond these are supported by the implementation.

---

## 5. User Scenarios & User Stories

Each story maps to a real capability in the code.

**US-1 — Compute a sum over HTTP (backend).**
As an HTTP caller, I want to request the sum of two non-negative integers so that I receive the result as JSON.
- *Grounding:* `backend/app.py → sum_route` returns `jsonify({"result": add(a, b)})`.
- *Acceptance (as-built):* `GET /api/sum/2/3` → `200 {"result": 5}`.

**US-2 — Compute a sum in-process (backend function).**
As a developer, I want a pure `add(a, b)` function so that I can compute sums without the HTTP layer.
- *Grounding:* `backend/app.py → add` returns `a + b`; verified by `backend/test_app.py → test_add`, `→ test_add_negative`.
- *Acceptance:* `add(2,3)==5`, `add(-1,1)==0`.

**US-3 — Compute a sum in the frontend (module function).**
As a frontend consumer, I want a `sum(a, b)` function so that I can compute sums locally in JavaScript.
- *Grounding:* `frontend/src/sum.js → sum` returns `a + b`; verified by `frontend/src/sum.test.js` (`'adds two numbers'`, `'handles negatives'`).
- *Acceptance:* `sum(2,3)===5`, `sum(-1,1)===0`.

**US-4 — Run both test suites through one QA harness.**
As the QA pipeline, I want both pytest and Vitest suites to run in their respective containers so that no component's tests are silently skipped.
- *Grounding:* `.coweave/manifest.yml → spec.tests.components[]` declares `backend`→`pytest` and `frontend`→`npm test`; `docker-compose.yml` provisions both containers.

**US-5 — Run the backend locally for manual checks.**
As a developer, I want to start a local server so that I can call the endpoint by hand.
- *Grounding:* `backend/app.py` `if __name__ == "__main__": app.run()` (Flask dev server, default `127.0.0.1:5000`).

---

## 6. Scope & Features

### 6.1 In scope (built and observable)

| # | Feature | Where it lives |
|---|---------|----------------|
| F1 | Addition function (backend) — `add(a, b) → a + b` | `backend/app.py → add` |
| F2 | Sum HTTP endpoint — `GET /api/sum/<int:a>/<int:b>` → `{"result": n}` | `backend/app.py → sum_route` |
| F3 | Addition function (frontend) — `sum(a, b) → a + b` (named ES export) | `frontend/src/sum.js → sum` |
| F4 | Backend test suite (pytest) — positive + negative cases | `backend/test_app.py` |
| F5 | Frontend test suite (Vitest, Node env) — positive + negative cases | `frontend/src/sum.test.js`, `frontend/vite.config.js` |
| F6 | Multi-runner QA harness — two containers, both suites run | `docker-compose.yml`, `.coweave/manifest.yml` |
| F7 | Local dev/build tooling — Flask dev server; Vite `dev`/`build` scripts | `backend/app.py`, `frontend/package.json` |

### 6.2 Out of scope (NOT implemented — stated honestly, not invented)

- **Multiplication (or any operation beyond addition).** Requested in issue #1 but **not present in the implementation**; tracked in `PRD_DELTA_issue-1.md`.
- **A rendered React UI / DOM entrypoint.** `react`/`react-dom` are declared but **unused**; there is no JSX, component, or DOM mount (`docs/design/technical/SYSTEM_ARCHITECTURE.md §2.2`).
- **Frontend↔backend wiring.** The frontend does not call the backend; `sum.js` computes locally (`SYSTEM_ARCHITECTURE.md §3`).
- **Persistence / data storage.** No database, ORM, models, or migrations exist (`docs/design/TDD.md §5`).
- **Authentication / authorization.** None (`SECURITY_DESIGN.md §3`).
- **Negative operands over HTTP.** The `<int:...>` converter rejects `-`, so `/api/sum/-1/1` returns `404` even though `add(-1,1)` is supported (`API_CONTRACTS.md §2.2`).
- **HTTP-layer tests.** Only the pure `add` function is tested, not `sum_route` (`docs/design/TDD.md §9 O2`).
- **Custom error handling / input validation** beyond the URL converter; **CORS, rate limiting, security headers, TLS, observability, CI/CD, and production deployment** — all absent (`SECURITY_DESIGN.md §10`, `DEPLOYMENT_STRATEGY.md §1, §5`).

---

## 7. Functional Requirements

Rules the code actually enforces:

| ID | Requirement | Enforced by |
|----|-------------|-------------|
| FR-1 | The backend returns the arithmetic sum of two non-negative integer path parameters as `{"result": <int>}` with HTTP `200` and `Content-Type: application/json`. | `backend/app.py → sum_route` (via `flask.jsonify`) |
| FR-2 | Path segments that are not valid non-negative integers (non-numeric or negative) do not match the route and yield HTTP `404`. | Flask `<int:a>/<int:b>` converter (`API_CONTRACTS.md §2.2`) |
| FR-3 | Only the `GET` method (plus Flask's auto `HEAD`/`OPTIONS`) is served; other methods yield HTTP `405`. | Flask default method handling (`API_CONTRACTS.md §2`) |
| FR-4 | The backend `add(a, b)` returns `a + b` for any integers, including negatives (arbitrary-precision; no overflow). | `backend/app.py → add`; `test_app.py` |
| FR-5 | The frontend `sum(a, b)` returns `a + b` and is importable as a named ES export. | `frontend/src/sum.js → sum`; `sum.test.js` |
| FR-6 | The QA harness runs the backend suite via `pytest` (workingDir `backend`) and the frontend suite via `npm test` (workingDir `frontend`), each in its own container. | `.coweave/manifest.yml → spec.tests.components[]`; `docker-compose.yml` |

---

## 8. Non-Functional Requirements (as built)

| Attribute | As-built characteristic | Source |
|-----------|-------------------------|--------|
| **Performance** | Constant-time arithmetic; stateless; every response computed on the fly. No caching, pagination, or load handling. | `docs/design/TDD.md §5`; `API_CONTRACTS.md §2.3` |
| **Security** | No auth, no secrets (`secrets: []`), no PII. Only implicit control is the `<int:...>` converter; `jsonify` sets safe JSON content type. Dev server is plain HTTP on loopback default. | `SECURITY_DESIGN.md §2–§9` |
| **Scalability** | Not addressed; single Flask dev-server process, no production WSGI server, no rate limiting. | `SECURITY_DESIGN.md §10`; `DEPLOYMENT_STRATEGY.md §2.1` |
| **Reliability / Observability** | No logging config, metrics, tracing, or health endpoint; Flask default request log only. | `DEPLOYMENT_STRATEGY.md §5` |
| **Reproducibility** | Backend deps exact-pinned (`flask==3.0.0`, `pytest==8.0.0`); frontend uses caret ranges with **no committed lockfile** → non-reproducible frontend installs. | `SECURITY_DESIGN.md §7`; `DEPLOYMENT_STRATEGY.md §2.2` |
| **Portability** | Test execution containerized via slim base images with source bind-mounted. | `docker-compose.yml` |

---

## 9. User Experience & Design

**There is no graphical user interface.** Despite `react`/`react-dom` being declared in `frontend/package.json`, the tree contains **no JSX, no React component, and no DOM entrypoint** (`docs/design/technical/SYSTEM_ARCHITECTURE.md §2.2`). Vitest runs in a **Node** environment (`frontend/vite.config.js → environment: 'node'`), not a browser DOM.

The as-built "experience" is developer- and machine-facing:
- **Backend API UX:** a single unversioned REST-style path `GET /api/sum/<int:a>/<int:b>` returning a minimal JSON body `{"result": n}`. No HTML, no docs page, no error bodies beyond framework defaults.
- **Frontend module UX:** a single importable function `sum(a, b)` consumed by tests only.
- **Accessibility / responsiveness:** Not applicable — no rendered UI exists.

---

## 10. Assumptions, Dependencies & Constraints

**Reconstruction assumptions:** See `docs/requirements/PRD_issue-1-QandA.md` for the full assumption ledger surfaced during this reverse-engineering run.

**Real dependencies (from manifests):**

| Component | Dependencies | Source |
|-----------|--------------|--------|
| Backend | `flask==3.0.0`, `pytest==8.0.0` (exact-pinned) | `backend/requirements.txt` |
| Frontend | `react ^18.2.0`, `react-dom ^18.2.0`, `vite ^5.0.0`, `vitest ^1.2.0` (caret ranges, no lockfile) | `frontend/package.json` |
| QA harness | `python:3.11-slim`, `node:20-slim` base images | `docker-compose.yml` |

**Constraints:**
- The harness runs `pytest` / `npm test` but declares **no explicit dependency-install step**; the slim base images ship neither Flask/pytest nor `node_modules`, so an install step (`pip install -r requirements.txt`, `npm install`) must be injected for tests to pass (`DEPLOYMENT_STRATEGY.md §3.2`).
- Negative sums are not reachable over HTTP due to the integer URL converter.

---

## 11. Risks & Mitigations

The out-of-scope gaps ARE the risks. These are descriptive of the as-built demo/test app, not remediation commitments.

| # | Risk (observed gap) | Impact | Mitigation that actually exists |
|---|---------------------|--------|---------------------------------|
| R1 | HTTP route can't reach negative sums (`<int>` rejects `-`) while `add()` supports them. | API/function domain mismatch. | None in code; documented in `API_CONTRACTS.md §2.2`. |
| R2 | The HTTP route `sum_route` is untested (only `add` is). | Route regressions go undetected. | Pure-function tests only (`test_app.py`). |
| R3 | No committed frontend lockfile; caret ranges. | Non-reproducible frontend installs/tests. | Backend deps are exact-pinned (partial mitigation). |
| R4 | QA manifest has no dependency-install step for slim images. | Tests may fail unless harness injects installs. | Documented as a harness prerequisite. |
| R5 | No auth, CORS, rate limiting, TLS; Flask dev server only. | Not production-hardened; DoS possible if publicly exposed. | Loopback default bind; no secrets to leak. |
| R6 | `react`/`react-dom` declared but unused. | Dead dependencies; "React" is nominal. | None; noted in `SYSTEM_ARCHITECTURE.md §2.2`. |
| R7 | `.coweave/manifest.yml` and `docker-compose.yml` present in git HEAD but shown deleted in the working tree during this run. | Harness config may be inadvertently removed; reconcile before relying on it. | Committed content documented from HEAD. |

---

## 12. Timeline & Milestones

**N/A — reconstructed from an existing implementation; no forward roadmap.** This PRD documents the product as built; it does not define a delivery schedule. The only pending change (multiplication, issue #1) is specified separately in `PRD_DELTA_issue-1.md`.

---

## 13. Open Questions & Decisions

| ID | Question | Priority | Status | Decision / Answer (as-built) |
|----|----------|----------|--------|------------------------------|
| Q1 | Is the divergence between `add(-1,1)` (tested, valid) and `/api/sum/-1/1` (`404`) intentional or a latent defect? | MEDIUM | OPEN | Documented as an as-built characteristic (`API_CONTRACTS.md §2.2`); code does not resolve it. |
| Q2 | Are `react`/`react-dom` intended for a future UI, or vestigial? | LOW | OPEN | Currently unused; treated as dead deps until a component appears. |
| Q3 | Should the QA harness own the dependency-install step, or is it assumed injected externally? | MEDIUM | OPEN | Manifest defines none; documented as a harness prerequisite. |
| Q4 | Is the working-tree deletion of the harness files intentional? | HIGH | OPEN | PRD describes committed (HEAD) content; deletion should be reconciled by an operator. |

---

## 14. Appendix

### 14.1 Data Model (product view)

**Not applicable — the product is entirely stateless.** There are no persisted entities, databases, ORMs, models, or migrations anywhere in the tree (`docs/design/TDD.md §5`; `SYSTEM_ARCHITECTURE.md §6`). The only transient "entity" is a computed arithmetic result `{"result": <integer>}`, which is never stored. No `DATABASE_SCHEMA.md` exists (intentionally omitted upstream).

### 14.2 References

- `README.md` — product purpose and the "run both runners" requirement.
- `docs/design/TDD.md` — master reverse-engineered technical design.
- `docs/design/technical/SYSTEM_ARCHITECTURE.md` — component decomposition and topology.
- `docs/design/technical/API_CONTRACTS.md` — the single HTTP endpoint and error semantics.
- `docs/design/technical/SECURITY_DESIGN.md` — security posture (largely absent by design).
- `docs/design/technical/DEPLOYMENT_STRATEGY.md` — build/test harness.
- `docs/requirements/PRD_DELTA_issue-1.md` — product intent for the not-yet-built multiply change.
- `docs/requirements/PRD_issue-1-QandA.md` — reconstruction assumption ledger.

### 14.3 Source citations (files inspected this run)

- `backend/app.py` (`add`, `sum_route`), `backend/test_app.py` (`test_add`, `test_add_negative`), `backend/requirements.txt`.
- `frontend/src/sum.js` (`sum`), `frontend/src/sum.test.js`, `frontend/package.json`, `frontend/vite.config.js`.
- `docker-compose.yml` (committed content; see R7 working-tree note), `.coweave/manifest.yml` (per TDDs).
- `README.md`; all documents under `docs/design/`.
