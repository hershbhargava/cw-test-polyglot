# PRD Reconstruction — Assumption & Question Ledger (issue #1)

> Companion to `docs/requirements/PRD.md`. This ledger records every ambiguity encountered while **reverse-engineering** the PRD from the code + reconstructed TDDs, the assumption taken to proceed, the PRD section that would change if the assumption is wrong, and where in the inputs the question arose.
>
> Downstream workflows (architect, dev, qa) should read this to distinguish PRD claims grounded in observable code from those resting on inference.
>
> **Iteration:** 2 · **Branch:** `feature/issue-1`

---

## A. Assumptions taken during reconstruction

| # | Question / Ambiguity | Assumption taken | Impact if wrong | Source |
|---|----------------------|------------------|-----------------|--------|
| A1 | The GitHub issue #1 asks to "add a multiply operation." Is multiplication part of the *current* product? | It is **not** implemented today; the PRD documents only addition (as-built) and lists multiply as Out of Scope, deferring it to `PRD_DELTA_issue-1.md`. | §1, §6 (Scope), §7 (FRs) — if multiply were already present, features/FRs would expand. | Issue body (`issues/issue-1.json → issue.body`); code (`backend/app.py`, `frontend/src/sum.js`) shows no multiply. |
| A2 | Who are the "users" of an app with no auth/roles? | Personas inferred from code interaction surfaces (QA pipeline, developer, anonymous HTTP caller), not from an in-app role model. | §4 (Personas), §5 (User Stories) — a real auth/role model would replace these inferred personas. | `SECURITY_DESIGN.md §3` (no auth); `backend/app.py → sum_route`. |
| A3 | Is the product's purpose really "exercise a multi-runner QA pipeline" rather than "provide a calculator"? | Yes — purpose is the polyglot/test-parity demonstration, per README + TDD; arithmetic is incidental. | §1, §2, §3 (Goals) — a genuine calculator product would reframe goals and metrics. | `README.md`; `docs/design/TDD.md §1`. |
| A4 | Are `react`/`react-dom` intended for a future UI or vestigial? | Treated as **currently unused dead dependencies**; no UX section content is inferred from them. | §6.2, §9 (UX), §11 R6 — a planned UI would add real UX requirements. | `frontend/package.json`; `SYSTEM_ARCHITECTURE.md §2.2`. |
| A5 | Should the negative-operand HTTP `404` be treated as a bug or intended behavior? | Documented as an **as-built characteristic** (open question), not asserted as intended or defective. | §6.2, §7 FR-2, §13 Q1 — a "bug" framing would change requirements/risks. | `API_CONTRACTS.md §2.2`; `test_app.py → test_add_negative`. |
| A6 | Does the QA harness own dependency installation? | Assumed **externally injected**; PRD notes the manifest defines no install step as a constraint/risk. | §10 (Constraints), §11 R4 — if the harness must own installs, that becomes a functional requirement of the harness. | `DEPLOYMENT_STRATEGY.md §3.2`; `.coweave/manifest.yml`. |
| A7 | The harness files show as deleted in the working tree but exist in git HEAD. Which state is authoritative? | The **committed (HEAD)** content is authoritative for the PRD; deletion is flagged as an open item to reconcile. | §6.1 F6, §11 R7, §13 Q4 — if deletion is intentional, feature F6 (QA harness) may not exist in the working tree. | `git status`; `docs/design/*` working-tree notes. |
| A8 | Are there success metrics/KPIs for this product? | Assumed **none** beyond binary test pass/fail; app is uninstrumented. | §3 (Goals & Success Metrics) — real telemetry would add measurable KPIs. | `DEPLOYMENT_STRATEGY.md §5` (no observability). |
| A9 | Is there any data model / persisted entity? | Assumed **none** — fully stateless; no `DATABASE_SCHEMA.md`. | §14.1 (Data Model) — any persistence would introduce entities and data requirements. | `docs/design/TDD.md §5`; `SYSTEM_ARCHITECTURE.md §6`. |

---

## B. Open questions carried into the PRD

These mirror `PRD.md §13` and remain genuinely unresolved by the code:

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q1 | Is the `add(-1,1)` vs `/api/sum/-1/1` (`404`) divergence intentional or a latent defect? | MEDIUM | OPEN |
| Q2 | Are `react`/`react-dom` intended for a future UI, or vestigial? | LOW | OPEN |
| Q3 | Should the QA harness own the dependency-install step, or is it injected externally? | MEDIUM | OPEN |
| Q4 | Is the working-tree deletion of `.coweave/manifest.yml` / `docker-compose.yml` intentional? | HIGH | OPEN |

---

## C. Notes on issue #1 (scope guidance only)

Per the reverse-engineering ground rules, issue #1's request to add multiplication was treated as **scope guidance (which area to cover)**, NOT as a requirements source. The multiply capability is **not** in the current code and is therefore documented as Out of Scope in `PRD.md §6.2`, with forward intent captured in `PRD_DELTA_issue-1.md`. No aspirational/planned requirement from the issue was written into the PRD as if implemented.
