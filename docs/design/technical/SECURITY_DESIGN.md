# Security Design — cw-test-polyglot (as-built)

> **Reverse-engineered** from the actual code. Documents the security posture that
> **exists** in the repository today, including the deliberate absence of controls in
> this demo/test app. Iteration 2.

## 1. Summary

`cw-test-polyglot` is a minimal, stateless demonstration app with **no authentication,
no authorization, no user data, and no persistence**. Its attack surface is limited to
a single arithmetic HTTP endpoint and the local build/test tooling. There are **no**
security controls implemented in application code beyond the implicit input coercion
performed by Flask's URL converter.

## 2. Assets & data classification

| Asset | Classification | Notes |
|-------|----------------|-------|
| Arithmetic result (`{"result": n}`) | Public / non-sensitive | Computed, not stored. |
| Source code | Public | Demo repo. |
| Secrets | None | `.coweave/manifest.yml` declares `secrets: []`. No `.env`, keys, or tokens anywhere in the tree. |

There is **no PII, credential, financial, or otherwise sensitive data** handled by the
application.

## 3. Authentication & authorization

- **None.** There is no auth middleware, session handling, token validation, RBAC, or
  permission check in `backend/app.py` or elsewhere. The single route `sum_route`
  (`app.py → sum_route`) is fully anonymous and unauthenticated.

## 4. Input handling & validation

- The only route validates input **implicitly** via the `<int:a>/<int:b>` URL
  converter in `@app.route("/api/sum/<int:a>/<int:b>")` (`app.py → sum_route`):
  - Non-integer segments → route does not match → `404`.
  - Negative values → not matched by the default `int` converter → `404`.
- There is **no** body parsing, so no injection surface from request bodies exists.
- Output is produced with `flask.jsonify`, which sets `Content-Type: application/json`
  and JSON-encodes the payload (the payload is a computed integer, not attacker
  echo-back), so there is no reflected-XSS vector in the response.

## 5. Network & transport

- **Transport:** The dev server (`app.run()` in `app.py`) serves plain HTTP with no
  TLS. Default bind is `127.0.0.1:5000` (loopback) unless overridden.
- **CORS:** Not configured. No `flask-cors` or CORS headers are set, so browsers apply
  the default same-origin policy to the endpoint.
- **Rate limiting / WAF:** None.
- **Container network:** `docker-compose.yml` defines no exposed ports or published
  services; both containers idle on `sleep infinity` and are used only for test
  execution.

## 6. Secrets management

- No secrets are used or required. `.coweave/manifest.yml` explicitly sets
  `secrets: []` and `requiredServices: []`. Environment variables set for tests are
  non-sensitive: `PYTHONDONTWRITEBYTECODE=1`, `NODE_ENV=test`.

## 7. Dependencies (supply-chain surface)

| Component | Declared dependencies | Source |
|-----------|-----------------------|--------|
| Backend   | `flask==3.0.0`, `pytest==8.0.0` (pinned) | `backend/requirements.txt` |
| Frontend  | `react ^18.2.0`, `react-dom ^18.2.0`, `vite ^5.0.0`, `vitest ^1.2.0` (caret ranges) | `frontend/package.json` |

- Backend deps are **exact-pinned**; frontend deps use caret ranges (`^`) and no
  lockfile (`package-lock.json` / `pnpm-lock.yaml`) is committed, so frontend builds
  are not fully reproducible. Noted in the TDD "Observations & Risks".

## 8. Threat model (STRIDE, as-built)

| Threat | Applicability | As-built status |
|--------|---------------|-----------------|
| **S**poofing | Low | No identities exist; nothing to spoof. |
| **T**ampering | Low | Stateless; no stored data to tamper with. |
| **R**epudiation | N/A | No auditing, no accounts — irrelevant for a stateless calculator. |
| **I**nformation disclosure | Low | Only public arithmetic results returned. No sensitive data. |
| **D**enial of service | Low–Med | No rate limiting; an operator exposing `app.run()` publicly could be flooded. Loopback default limits exposure. |
| **E**levation of privilege | N/A | No privilege model exists. |

## 9. Mitigations that ACTUALLY exist

- URL `int` converter rejects non-integer / negative path segments before the handler
  runs (`app.py → sum_route`).
- `jsonify` enforces JSON content type and safe encoding of the computed result.
- Default loopback bind of the Flask dev server (no `host="0.0.0.0"` in code).
- No secrets in the repo to leak.

## 10. Notable gaps (documented, not "fixed")

These are recorded as observations — appropriate for a demo/test app, not
recommendations for this iteration:

- No TLS on the dev server (`app.run()` HTTP only).
- No production WSGI server; Flask's dev server is not hardened for production.
- No CORS policy, rate limiting, or security headers.
- Frontend has no committed lockfile → non-reproducible dependency resolution.

## Related documents
- `API_CONTRACTS.md` — endpoint request/response and error semantics.
- `SYSTEM_ARCHITECTURE.md` — component boundaries and exposure.
- `../TDD.md` — master technical design document.
