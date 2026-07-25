# Runtime Reliability Hardening Design

## Goal

Make the local UI, evidence state, and CI describe the same verified behavior. This work targets runtime accuracy rather than new product features.

## Current Gap

`app/main.py` presents a hard-coded portfolio status that says implementation is active and the evidence gate is pending. That statement can remain false after the local verification manifest turns fully green. The Chromium browser smoke is useful locally but is not executed by GitHub Actions.

## Design

1. Replace the hard-coded active-project status with a function that derives the Resume Growth Coach status from `load_recorded_evidence()` on each request.
2. The UI must state either that all evidence checks are complete or list only the currently incomplete checks. It must not infer evidence from browser input or a caller-supplied API body.
3. Add regression coverage for both a missing/partial manifest and a fully verified manifest. The browser smoke must assert the evidence-derived wording instead of the obsolete static wording.
4. Add a separate GitHub Actions browser job. It installs Chromium with Playwright and runs `tools/browser_smoke.py` against its disposable SQLite database.
5. Append a dated verification entry to the English and Chinese project logs; do not rewrite historical test results.

## Acceptance Evidence

- Unit/API tests prove missing and complete evidence states render correctly.
- Chromium smoke passes locally and in the browser CI job.
- Existing test and Alembic CI jobs remain green.
- No real resume, job description, token, or local evidence manifest is committed.

## Non-Goals

- Do not add hosted deployment, external recruiting-platform automation, or cross-repository filesystem dependencies.
- Do not make the planner trust client-provided evidence flags.
