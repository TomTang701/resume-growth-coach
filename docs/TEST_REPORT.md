# Professional Test Report

## Scope

This report evaluates the current local-first Resume Growth Coach implementation: deterministic resume/JD analysis, Portfolio Planner behavior, document parsing, persistence, local-model fallback, privacy boundaries, and reproducible verification. It does not claim that a fit score predicts hiring outcomes.

The latest evidence in this report is tied to verified revision `d7d32ab18ed131ad39e70012ef6de6de4b365777`.

## Current Verdict

**Passed for local, reproducible portfolio use. The project is intentionally local-only and is not a deployed production service.**

The verified implementation includes FastAPI, PostgreSQL through Docker Compose, Alembic migrations, SQLite support for isolated local tests, deterministic analysis before optional Ollama output, a Chromium UI smoke flow, and an evidence gate for resume-bullet eligibility.

## Verified Evidence

- Regression suite: `70 passed` with `pytest -q`.
- API quality gate: passed, including health, analysis, recommendations, UI file upload, cleanup, malformed PDF, input limits, HTML escaping, and not-found behavior.
- Chromium browser smoke: passed for page load, text and template analysis, Portfolio Planner display, validation recovery, and file upload.
- Docker Compose/PostgreSQL smoke: passed; the published port is checked to bind only to loopback.
- Exact-head GitHub Actions CI: passed for workflow policy, tests and Alembic migration, browser smoke, and Docker smoke: https://github.com/TomTang701/resume-growth-coach/actions/runs/30188637133
- Local evidence manifest: all resume-eligibility checks are true for the verified revision, including documentation and sanitized-demo checks.
- Public demonstrations use sanitized sample resume and job-description data only.

## Covered Behaviors

- Text, `.txt`, and `.pdf` input with bounded file reads, validation errors, normalization, and legacy encoding fallback.
- Deterministic skill matching, project-evidence analysis, gap scoring, and role-template recommendations.
- Portfolio Planner input through built-in templates, manually pasted descriptions, or uploaded job descriptions; duplicate project proposals are suppressed.
- Persistence, document deletion, retention cleanup, and Alembic-managed fresh PostgreSQL and SQLite schemas.
- Optional Ollama summaries with deterministic fallback when the local model is unavailable.
- Evidence-derived resume-bullet eligibility: API callers cannot unlock a project by submitting their own verification flags.

## Intentional Boundaries and Open Work

### P0

None currently known.

### P1

- README screenshot refresh awaits manually captured, sanitized UI screenshots. Agent-generated images are not accepted as verification evidence.
- Chromium smoke is covered; Firefox and WebKit behavior have not been verified.

### P2

- High-volume load behavior and a human-labeled score-calibration dataset are not available.
- The project is not deployed and does not automate recruiting-platform activity.

## Reproduce the Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools\quality_gate.py
.\.venv\Scripts\python.exe tools\browser_smoke.py
.\scripts\run-docker-smoke.ps1
```

After the exact commit's CI is green and the tracked worktree is clean, record the eligibility evidence:

```powershell
.\scripts\record-verification-evidence.ps1
```

## Claim Guidance

Use claims supported by the verified local stack and recorded evidence: FastAPI, PostgreSQL, Alembic, Docker Compose, deterministic analysis, Ollama fallback, API/browser tests, and exact-commit CI. Do not claim production deployment, hiring prediction accuracy, recruiting-platform automation, cross-browser coverage, or load-test results that have not been verified.
