# cw-test-polyglot

A deliberately **polyglot** app for CoWeave brownfield SDLC testing (#120 / dev-bug 093):

- `backend/` — Python (Flask) with pytest tests
- `frontend/` — React with Vitest tests

Both components have their own test runner; a correct QA manifest must run **both**.
