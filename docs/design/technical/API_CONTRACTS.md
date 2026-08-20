# API Contracts — cw-test-polyglot (as-built)

> **Reverse-engineered** from the actual route definitions. Documents the real HTTP
> surface that exists in the code today. Iteration 2.

## 1. Scope

The application exposes exactly **one** HTTP endpoint, defined in `backend/app.py`.
There is no OpenAPI/Swagger spec, no GraphQL schema, and no protobuf in the repo; this
document is reconstructed directly from the Flask route decorator and handler.

The frontend (`frontend/src/`) exposes **no** HTTP API — `sum.js` is a local ES module
function with no network I/O.

## 2. Endpoint: GET `/api/sum/<int:a>/<int:b>`

Defined at `backend/app.py → sum_route`:

```python
@app.route("/api/sum/<int:a>/<int:b>")
def sum_route(a, b):
    return jsonify({"result": add(a, b)})
```

| Property | Value |
|----------|-------|
| Method   | `GET` (Flask default when `methods` is unspecified; `HEAD`/`OPTIONS` auto-provided by Flask) |
| Path     | `/api/sum/<int:a>/<int:b>` |
| Path params | `a`, `b` — both use Flask's `<int:...>` converter (non-negative integers) |
| Auth     | None |
| Query params | None |
| Request body | None |
| Content-Type (response) | `application/json` (via `flask.jsonify`) |

### 2.1 Success response — `200 OK`

Body shape:

```json
{ "result": <integer> }
```

Where `result` is `a + b` computed by `add(a, b)` (`app.py → add`).

**Example:** `GET /api/sum/2/3` → `200` → `{"result": 5}`.

### 2.2 Error responses (framework-default behavior)

These are **not** implemented by application code; they are Flask/Werkzeug defaults
that follow from the route definition. There is **no** custom error-handling
middleware, `@app.errorhandler`, or input validation beyond the URL converter.

| Condition | Status | Notes |
|-----------|--------|-------|
| Path segment not a valid integer (e.g. `/api/sum/2/abc`) | `404 Not Found` | The `<int:...>` converter fails to match, so no route matches. Not a `400`. |
| Negative operand (e.g. `/api/sum/-2/3`) | `404 Not Found` | Flask's default `int` converter does **not** accept a leading `-`, so the route does not match. Negative sums are therefore **not reachable via HTTP** even though `add()` supports them. |
| Unknown path | `404 Not Found` | Werkzeug default. |
| Wrong method (e.g. `POST /api/sum/2/3`) | `405 Method Not Allowed` | Werkzeug default. |
| Integer overflow | N/A | Python integers are arbitrary-precision; no overflow. |

### 2.3 Behavioral notes

- The route and the pure function diverge in reachable input domain: `add(-1, 1)` is
  tested and returns `0` (`test_app.py → test_add_negative`), but the equivalent HTTP
  call `/api/sum/-1/1` returns `404` because of the `int` converter. This is an
  as-built characteristic, noted in the TDD "Observations & Risks".
- No pagination, rate limiting, versioning header, ETag/caching, or CORS headers are
  configured (see `SECURITY_DESIGN.md`).

## 3. Non-HTTP "contract": frontend module export

Although not an HTTP API, the frontend exposes a stable module interface consumed by
its tests:

- `sum(a, b): number` — named ES export from `frontend/src/sum.js` (`sum.js → sum`),
  returns `a + b`. Verified by `frontend/src/sum.test.js` for `(2,3)→5` and
  `(-1,1)→0`.

## Related documents
- `SYSTEM_ARCHITECTURE.md` — where this endpoint sits in the component map.
- `SECURITY_DESIGN.md` — input handling and network exposure of this endpoint.
- `../TDD.md` — master technical design document.
