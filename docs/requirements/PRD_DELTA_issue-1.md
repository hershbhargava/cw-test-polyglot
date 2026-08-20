# PRD DIFF — Add a Multiply Operation to Backend and Frontend

| Field | Value |
|-------|-------|
| **Iteration** | 1 |
| **Design Mode** | New Feature / Bug Fix |
| **Depth Mode** | Detailed |
| **Issue** | [#1](https://github.com/hershbhargava/cw-test-polyglot/issues/1) |
| **Feature Branch** | `feature/issue-1` |
| **Base Branch** | `main` |
| **Priority** | Medium |
| **Status** | Draft for review |

---

## 1. Change Summary

This change adds a **multiplication** capability to the `cw-test-polyglot` application, mirroring the addition capability that already exists in both halves of the polyglot stack. A `multiply(a, b)` function will be introduced to the Python (Flask) backend alongside the existing `add` function, and a `multiply(a, b)` function will be introduced to the React/JavaScript frontend alongside the existing `sum` function. Each new function is accompanied by its own automated tests (pytest for the backend, Vitest for the frontend).

**Scope at a glance:**

| Metric | Count |
|--------|-------|
| New capabilities | 1 (multiplication) |
| New backend functions | 1 (`multiply`) |
| New frontend functions | 1 (`multiply`) |
| New test suites | 2 (pytest + Vitest) |
| Modified existing features | 0 |
| Deprecated features | 0 |

**Priority & urgency:** Medium priority, low urgency. This is an additive enhancement that extends the demonstration surface of the polyglot app. There is no production incident or deadline pressure. The overriding constraint from the issue is that **all existing tests must remain green**.

---

## 2. Motivation & Background

**Why now:** The application currently demonstrates a single arithmetic operation (addition) consistently across two language ecosystems — Python and JavaScript — each with parallel test coverage. Issue #1 requests a second arithmetic operation, multiplication, be added with the same parity. This grows the app's demonstration of polyglot symmetry and gives both stacks a second worked example of the "operation + test" pattern.

**Business/user value:**
- Demonstrates that the "add an operation with matching tests on both sides" workflow is repeatable and low-friction.
- Provides a second reference implementation for contributors extending the app with further operations.
- Increases confidence that the shared testing conventions (pytest + Vitest) scale beyond a single function.

**Source:** GitHub Issue #1 — *"Add a multiply operation to backend and frontend"*

> "Add a `multiply(a, b)` to the Python backend (with a pytest test) and a `multiply(a, b)` to the React frontend (with a vitest test). Both components should keep their existing tests green."

**Requestor:** Repository owner (`hershbhargava`).

---

## 3. Current State

Today the application supports exactly one arithmetic operation, addition, expressed slightly differently on each side of the stack.

### 3.1 Backend (Python / Flask) — today

- Location: `backend/app.py`
- An `add(a, b)` function returns the sum of two numbers.
- A Flask route `/api/sum/<int:a>/<int:b>` exposes addition over HTTP and returns JSON of the shape `{"result": <number>}`.
- Tests live in `backend/test_app.py` and cover a positive case and a negative-number case for `add`.

### 3.2 Frontend (React / JavaScript) — today

- Location: `frontend/src/sum.js`
- A `sum(a, b)` function (ES6 named export) returns the sum of two numbers.
- Tests live in `frontend/src/sum.test.js` (Vitest) and cover a positive case and a negative-number case for `sum`.

### 3.3 Current limitation this change addresses

There is no way to multiply two numbers in either the backend or the frontend. Any consumer wanting a product of two values must compute it themselves. This change closes that gap symmetrically across both stacks.

---

## 4. Proposed Changes

All changes in this iteration are **New**. Nothing existing is modified, extended, or deprecated.

### 4.1 New — Backend `multiply` function (Python)

| Aspect | Before | After |
|--------|--------|-------|
| Multiplication function | Does not exist | `multiply(a, b)` returns the product of `a` and `b` |
| Addition function `add` | Exists, unchanged | Exists, unchanged |

**User story:** As a backend consumer, I want a `multiply(a, b)` function so that I can obtain the product of two numbers using the same conventions as the existing `add` function.

**Acceptance criteria:**
- A `multiply(a, b)` function exists in the backend and returns the arithmetic product of its two arguments.
- Calling it with `(2, 3)` returns `6`.
- Calling it with a negative operand behaves per standard arithmetic (e.g. `(-2, 3)` returns `-6`).
- Calling it with zero returns `0` (e.g. `(0, 5)` returns `0`).
- The existing `add` function and its behavior are unchanged.

### 4.2 New — Backend pytest coverage for `multiply`

**User story:** As a maintainer, I want automated pytest coverage for `multiply` so that its correctness is verified on every test run.

**Acceptance criteria:**
- New pytest test(s) verify `multiply` for at least a basic positive case and one edge case (negative and/or zero), consistent with the existing `add` test style.
- The full backend test suite (existing `add` tests plus new `multiply` tests) passes.

### 4.3 New — Frontend `multiply` function (JavaScript)

| Aspect | Before | After |
|--------|--------|-------|
| Multiplication function | Does not exist | `multiply(a, b)` (named export) returns the product of `a` and `b` |
| Addition function `sum` | Exists, unchanged | Exists, unchanged |

**User story:** As a frontend consumer, I want a `multiply(a, b)` function so that I can obtain the product of two numbers using the same conventions as the existing `sum` function.

**Acceptance criteria:**
- A `multiply(a, b)` named export exists in the frontend and returns the arithmetic product of its two arguments.
- Calling it with `(2, 3)` returns `6`.
- Negative and zero operands behave per standard arithmetic.
- The existing `sum` function and its behavior are unchanged.

### 4.4 New — Frontend Vitest coverage for `multiply`

**User story:** As a maintainer, I want automated Vitest coverage for `multiply` so that its correctness is verified on every test run.

**Acceptance criteria:**
- New Vitest test(s) verify `multiply` for at least a basic positive case and one edge case (negative and/or zero), consistent with the existing `sum` test style (`describe` / `it` / `expect().toBe()`).
- The full frontend test suite (existing `sum` tests plus new `multiply` tests) passes via `npm test`.

### 4.5 Scope boundaries — explicitly NOT changing

- The existing `add` (backend) and `sum` (frontend) functions and tests are **not** modified.
- The existing `/api/sum/<int:a>/<int:b>` Flask route is **not** modified.
- **A new HTTP API route for multiply is OUT OF SCOPE** for this iteration unless clarified otherwise (see Open Question Q1). The issue explicitly asks only for `multiply(a, b)` functions plus tests on each side; it does not request an endpoint.
- No user-facing UI screen, form, or React component is added (the frontend currently exposes math via a plain module function, not a rendered UI).
- No new operations beyond multiplication (no subtract/divide) are added.
- No changes to build tooling, dependencies, or configuration files are required.

---

## 5. Impact Analysis

### 5.1 User impact

- **Affected personas:** Developers/consumers of the backend function API and the frontend module API.
- **Workflow changes:** None to existing workflows. This is purely additive — a new function becomes available alongside existing ones.
- **Retraining/communication:** None required. No existing behavior changes.
- **Breaking changes to expectations:** None.

### 5.2 Data impact

- **No impact.** The application is stateless with no database, schema, or persisted data. No migration or data transformation is involved.

### 5.3 API impact

- **No impact to existing API contracts.** The existing `/api/sum/<int:a>/<int:b>` route is untouched and fully backward compatible.
- Whether a new `/api/multiply/...` route is added is deferred to Open Question Q1; if added, it would be a purely additive new route with no effect on existing consumers.

### 5.4 Integration impact

- **No impact.** There are no external systems, webhooks, notifications, events, or third-party integrations involved.

### 5.5 Performance impact

- **Negligible.** Multiplication is a constant-time arithmetic operation. No new load, scaling, or latency considerations for existing systems.

---

## 6. Requirements

### 6.1 New functional requirements

| ID | Requirement |
|----|-------------|
| FR-1 | The backend shall provide a `multiply(a, b)` function that returns the arithmetic product of two numeric inputs. |
| FR-2 | The frontend shall provide a `multiply(a, b)` function (named export) that returns the arithmetic product of two numeric inputs. |
| FR-3 | The backend shall include automated pytest coverage for `multiply` covering a positive case and at least one edge case (negative and/or zero). |
| FR-4 | The frontend shall include automated Vitest coverage for `multiply` covering a positive case and at least one edge case (negative and/or zero). |

### 6.2 Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | The `multiply` implementations shall follow the same code and test conventions already established for `add`/`sum`. |
| NFR-2 | No new runtime or dev dependencies shall be introduced. |

### 6.3 Backward compatibility requirements

| ID | Requirement |
|----|-------------|
| BC-1 | All existing backend tests (for `add`) shall continue to pass unchanged. |
| BC-2 | All existing frontend tests (for `sum`) shall continue to pass unchanged. |
| BC-3 | The existing `/api/sum/<int:a>/<int:b>` route shall remain functionally identical. |

### 6.4 Accessibility requirements

- **Not applicable.** No user-facing UI is added or changed in this iteration.

---

## 7. Migration & Rollback

### 7.1 Migration

- **No data migration required.** The application is stateless; adding functions requires no schema, data, or configuration migration.
- Deployment simply ships the added functions and tests.

### 7.2 Feature flag strategy

- **Not required.** The change is small, additive, and non-breaking. A feature flag would add unnecessary complexity.

### 7.3 Rollback plan

- Rollback is a straightforward revert of the commit(s) introducing the `multiply` functions and their tests. Because the change is purely additive and touches no existing behavior, reverting has no side effects on existing functionality.

### 7.4 Communication plan

- **None required** — no existing user workflow changes.

---

## 8. Testing Strategy

### 8.1 What specifically needs testing (new)

- **Backend `multiply`:** basic positive case (e.g. `2 × 3 = 6`), a negative-operand case (e.g. `-2 × 3 = -6`), and a zero case (e.g. `0 × 5 = 0`).
- **Frontend `multiply`:** the same set of cases expressed in Vitest style.

### 8.2 Regression test areas (existing features that could break)

- Existing backend `add` tests (`test_add`, `test_add_negative`) must remain green.
- Existing frontend `sum` tests ("adds two numbers", "handles negatives") must remain green.
- The `/api/sum` route behavior must remain unchanged.

### 8.3 Edge cases specific to the change

- Multiplication by zero returns zero.
- Multiplication with negative operands yields the correct sign.
- Commutativity is inherently satisfied by arithmetic; a single ordering per case is sufficient.

### 8.4 Performance benchmarks

- **Not applicable.** Constant-time arithmetic; no before/after performance benchmark is meaningful.

### 8.5 Exit criteria

- The full backend pytest suite passes.
- The full frontend Vitest suite passes (`npm test`).
- No existing test is modified or skipped to achieve green.

---

## 9. Open Questions & Decisions

| ID | Question | Priority | Status | Answer |
|----|----------|----------|--------|--------|
| Q1 | Should a new HTTP API route (e.g. `/api/multiply/<int:a>/<int:b>`) be added to expose multiply over HTTP, mirroring the existing `/api/sum` route? The issue text requests only the `multiply(a, b)` functions plus tests, so this PRD scopes the endpoint OUT by default. | HIGH | OPEN | |
| Q2 | Should the `multiply` tests also cover non-integer (float) operands, or is integer coverage sufficient to match the existing `add`/`sum` test scope? | MEDIUM | OPEN | |
| Q3 | Should the frontend function live in a new file (e.g. `multiply.js`) or be co-located with the existing `sum.js`? (Naming/organization decision; does not affect behavior.) | LOW | OPEN | |

**Decisions made in this iteration (documented assumptions):**
- **D1:** Scoped the HTTP endpoint OUT by default, following the literal issue text which asks only for functions + tests. Revisit if Q1 is answered "yes."
- **D2:** Assumed edge-case coverage should mirror the existing `add`/`sum` tests (positive + negative), with zero added as a low-cost multiplication-specific case.

---

## 10. Appendix

### 10.1 Related tickets/issues

- GitHub Issue #1 — "Add a multiply operation to backend and frontend" (primary source).

### 10.2 Existing artifacts affected / referenced

| Area | Existing artifact | Relationship to this change |
|------|-------------------|-----------------------------|
| Backend function module | `backend/app.py` (contains `add`) | New `multiply` sits alongside `add`; `add` unchanged |
| Backend tests | `backend/test_app.py` (tests `add`) | New `multiply` tests added; existing tests unchanged |
| Frontend function module | `frontend/src/sum.js` (contains `sum`) | New `multiply` follows the same export convention; `sum` unchanged |
| Frontend tests | `frontend/src/sum.test.js` (tests `sum`) | New `multiply` tests follow the same Vitest convention; existing tests unchanged |

### 10.3 Supporting context

- Backend testing framework: pytest 8.0.0. Frontend testing framework: Vitest 1.2.0 (Node environment).
- The application is a minimal, stateless polyglot demonstration app with no database, authentication, or external integrations, which keeps the impact surface of this change extremely small.
