## 📋 PRD DIFF Iteration 1 — Add a multiply operation to backend and frontend

**Mode**: New Feature / Bug Fix
**Issue**: #1
**Branch**: `feature/issue-1`

### What this iteration covers

Specifies adding a `multiply(a, b)` function to both the Python (Flask) backend and the React/JS frontend, each with matching automated tests (pytest + Vitest), while keeping all existing `add`/`sum` tests green. Purely additive — no existing behavior changes.

### Key decisions

- Scoped IN: `multiply(a, b)` on both sides + pytest and Vitest coverage (positive, negative, zero cases).
- Scoped OUT: a new `/api/multiply` HTTP route, UI components, and other operations (subtract/divide) — the issue asks only for functions + tests.
- Modeled the new functions and tests on the existing `add`/`sum` conventions; no new dependencies.

### Open questions for the reviewer

- Q1 (HIGH): Should a `/api/multiply/<int:a>/<int:b>` route be added to mirror `/api/sum`? Currently scoped OUT.
- Q2 (MEDIUM): Should tests cover float operands, or is integer coverage sufficient to match existing scope?
- Q3 (LOW): New file (`multiply.js`) vs co-locating with `sum.js` on the frontend?

### Files in this iteration

- `docs/requirements/PRD_DELTA_issue-1.md` — full change spec (10 sections, ~13kB)
- `external-memory/prd/iteration-1/metadata.json` — machine-readable metrics
- `external-memory/prd/iteration-1/GITHUB_COMMENT.md` — this comment

### Next step

Run the prd-reviewer workflow to validate this iteration (especially resolving Q1 on the HTTP endpoint) before architect handoff.
