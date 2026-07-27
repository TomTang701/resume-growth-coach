# Development Log

This is the primary handoff record for Resume Growth Coach. It records changes that affect behavior, tests, startup, data contracts, or handoff work. Small spelling-only or formatting-only edits do not require a separate entry.

The Chinese counterpart is [DEVELOPMENT_LOG.zh-CN.md](DEVELOPMENT_LOG.zh-CN.md). Keep both files semantically identical; update the English file first, then update the Chinese translation in the same commit.

## Logging Rules

Every major change must add an entry containing:

- Date and commit ID
- What changed and which modules were affected
- Verification commands and results
- Remaining problems
- Future work ordered as P0, P1, and P2
- Startup, data, privacy, or handoff notes

User-facing project output must remain English-only. These internal logs are bilingual, with this English file as the default entry point.

## 2026-07-09: Ollama Startup Assurance and Adversarial Test Expansion

### Changes

- Startup scripts verify the Ollama API, verify `qwen2.5:3b`, pull it when missing, and send a real generation smoke test.
- Ollama requests use a 60-second default timeout. `RGC_OLLAMA_TIMEOUT_SECONDS` is read for each request and bounded to 1-300 seconds.
- Added regression tests for UI validation, HTML escaping, invalid uploads, empty files, oversized job descriptions, missing analysis objects, and model timeout configuration.
- Kept `tools/quality_gate.py` as a reusable quality check that does not require Ollama.

### Verification

- The local `qwen2.5:3b` model passed a real generation smoke test.
- The quality gate covered health, analysis, recommendations, malformed PDF, input limits, UI escaping, and 404 behavior.
- Final result: `36 passed, 1 warning`; pytest and all API contract checks passed.

### Remaining Problems

- The default score is heuristic and does not represent real hiring probability; skill aliases and responsibility understanding remain limited.
- Browser-level automation has not been added; UI coverage currently uses FastAPI `TestClient` HTML checks.
- Ollama depends on local installation, network access, and disk space; the app falls back when it is unavailable.
- PDF, very long text, and first-model-load performance have not received systematic benchmarks.

### Future Work

- **P0**: Maintain golden cases for role templates and skill aliases to prevent inflated scores from keyword mistakes.
- **P1**: Add a real browser smoke test covering submission, error recovery, and result rendering.
- **P1**: Add PDF fixtures, Unicode/encoding cases, and large-file performance tests.
- **P2**: Expose explainable score components and calibrate them with labeled data; do not treat one total score as a definitive conclusion.

### Handoff Notes

- Use `Start-ResumeGrowthCoach.cmd`; manual virtual-environment activation is not required.
- Run `scripts/run-quality-gate.ps1` before committing.
- Never commit real resumes, real job descriptions, `local_data/`, or `.env` files.

## 2026-07-09: P1 QA Remediation

### Changes

- Added optional resume and job-description file uploads to the web UI.
- Replaced unbounded upload reads with chunked reads capped at the configured 5 MB limit.
- Made analysis persistence one commit for the analysis, skill matches, and growth goals.
- Added document deletion endpoints that remove dependent analyses, matches, and goals in the same operation.
- Added explicit `scripts/run-ollama-smoke-test.ps1` and corrected its PowerShell success-state handling.
- Rejected CJK text in user-facing Ollama fields so fallback output remains English-only.
- Updated README and local specification wording to describe deterministic fallback rather than a second fallback model.

### Verification

- `41 passed, 1 warning`.
- API quality gate passed.
- Real `qwen2.5:3b` smoke test passed.

### Remaining Problems

- Browser-level end-to-end coverage, concurrency testing, and production data encryption are still not implemented.
- The dependency deprecation warning remains.

### Future Work

- **P0**: None currently known.
- **P1**: Add Playwright browser coverage and a local data retention/cleanup command.
- **P2**: Add SQLite migration support, concurrency tests, and score calibration data.

## 2026-07-09: Retention Cleanup Follow-up

### Changes

- Added `app/services/retention.py` for age-based document and dependent-record cleanup.
- Added `tools/cleanup_local_data.py`; it is dry-run by default and requires `--delete` for destructive cleanup.
- Added retention regression tests for dry-run counts, dependent analysis deletion, and invalid retention windows.
- Added README instructions and updated the test/report documentation.

### Verification

- `49 passed, no warnings` after replacing deprecated UTC time handling and updating the Starlette test-client dependency.
- API quality gate passed.
- Real Ollama smoke test remains passed with `qwen2.5:3b`.
- Playwright/Selenium browser automation was not run because neither package is installed in this environment.

### Remaining Problems

- Browser-level end-to-end coverage remains open.
- SQLite migration support, concurrency/load testing, and score calibration data remain open.
- No test warning remains in the current environment after installing `httpx2`.

### Future Work

- **P0**: None currently known.
- **P1**: Add Playwright as an optional test profile and run browser smoke tests in a configured environment.
- **P2**: Add migration tooling, concurrent SQLite tests, and labeled score-calibration fixtures.

## 2026-07-09: Baseline and Concurrency Follow-up

### Changes

- Added five deterministic score golden cases in `tests/fixtures/score_baseline.json`.
- Added a concurrent API flow test covering three simultaneous resume/JD/analysis requests.
- Updated the professional test report and both language test logs with the new evidence.

### Verification

- `49 passed, no warnings`.
- Score baseline cases passed with stable expected values.
- Concurrent SQLite API flow passed with isolated analysis IDs and retrievable results.

### Remaining Problems

- Browser automation remains blocked by the missing Playwright/Selenium environment.
- SQLite schema migration tooling and labeled score-calibration data are still not implemented.
- The previous Starlette/httpx warning is resolved by the `httpx2` dependency update.

### Future Work

- **P0**: None currently known.
- **P1**: Configure Playwright and run browser smoke tests.
- **P2**: Add migration/version management, expand concurrency load, and replace heuristic baselines with labeled calibration data.

## 2026-07-09: Test Client Dependency Cleanup

### Changes

- Replaced the deprecated Starlette `httpx` fallback with the compatible `httpx2` development dependency in `requirements.txt` and `pyproject.toml`.

### Verification

- A clean-environment dependency install is represented by the updated dependency files; the current virtual environment has `httpx2==2.5.0` installed.
- A full test run is required after this dependency change before treating the warning as closed.

### Follow-up Finding

- The first direct `cleanup_local_data.py --help` run exposed a root-path import bug; the CLI now inserts the project root before importing `app`.

## 2026-07-09: Browser and Schema Protection Follow-up

### Changes

- Added Playwright/Chromium `tools/browser_smoke.py` coverage for page load, text analysis, validation recovery, and file upload.
- Added schema version marker and required table/column validation in `app/database.py`.
- Added `tools/check_database_schema.py` for explicit local database checks.
- Expanded the concurrent API smoke test from 3 to 12 flows.
- Added Playwright to the development dependencies and documented the new commands.

### Verification

- Browser smoke test passed.
- Database schema validation passed with `version=1`.
- `49 passed`, no warnings.
- API quality gate passed.

### Remaining Problems

- The schema marker is protection, not a full historical migration system; upgrade scripts are still needed for future schema changes.
- The browser test covers Chromium only and is not yet a cross-browser or CI matrix.
- Twelve concurrent flows are a smoke test, not a high-volume load test.
- Human-labeled score calibration data is still unavailable.

### Future Work

- **P0**: None currently known.
- **P1**: Add migration scripts and run the browser smoke test in CI.
- **P2**: Add Firefox/WebKit coverage, high-volume load tests, and labeled score calibration.

## 2026-07-25: Portfolio Planning and Evidence Gate

### Changes

- Added built-in backend/full-stack and AI application job templates to the local UI and API.
- Added Portfolio Planner cards that distinguish active work from non-duplicative future project proposals.
- Added PostgreSQL/Alembic, Docker Compose, CI, and an evidence-recording script.
- Changed portfolio bullet eligibility to read a local verification manifest; API request bodies can no longer claim verification flags.

### Verification

- Full regression: `57 passed`.
- API quality gate and Chromium smoke test passed, including the template and planner path.
- A local-only evidence run recorded Docker and CI as incomplete, keeping resume eligibility false.

### Remaining Problems

- Docker Desktop is unavailable on this machine, so Compose smoke evidence is not yet recorded.
- GitHub CI cannot be evidenced until the implementation is committed and pushed.

### Future Work

- **P0**: None currently known.
- **P1**: Run Docker smoke and exact-head GitHub Actions after publication.
- **P2**: Add browser coverage to CI and a score-calibration dataset.

## 2026-07-25 Runtime Evidence Closure

### Changes

- Replaced the stale static Portfolio Planner card with status derived from the recorded verification checklist.
- Added deterministic incomplete-evidence coverage to the Chromium smoke test.
- Added the Chromium smoke test as a dedicated GitHub Actions job.

### Verification

- Full regression and quality/API gate: 59 passed.
- Chromium browser smoke and Docker Compose/PostgreSQL smoke passed locally.
- Exact-head CI passed, including the browser job: https://github.com/TomTang701/resume-growth-coach/actions/runs/30180380459
- The local evidence manifest now records every resume-eligibility requirement as true.

### Remaining Problems

- Firefox/WebKit coverage, high-volume load testing, and human-labeled score calibration remain future work.

## 2026-07-25: Current Evidence and Documentation Reconciliation (`d7d32ab`)

### Changes

- Added direct regression coverage for pasted text, UTF-8 BOM text uploads, bounded reads, legacy encoding fallback, and invalid document input in `tests/test_parsing.py`.
- Reconciled the current README and professional test report with the implemented PostgreSQL/Alembic/Docker Compose stack and the evidence-gated Portfolio Planner.
- Kept prior development-log entries as historical records instead of rewriting their contemporaneous SQLite/MVP results.

### Verification

- Full local regression: `70 passed`.
- Quality gate, Chromium browser smoke, and Docker Compose/PostgreSQL smoke passed.
- Exact-head CI passed for workflow policy, tests and Alembic migration, browser smoke, and Docker smoke: https://github.com/TomTang701/resume-growth-coach/actions/runs/30188637133
- `local_data/verification-evidence.json` records every eligibility check as true for `d7d32ab18ed131ad39e70012ef6de6de4b365777`.

### Remaining Problems

- Chromium is the only browser smoke target; high-volume load behavior and score calibration remain unverified.
- README screenshot refresh requires manually captured, sanitized UI images; generated images are not accepted as evidence.

### Future Work

- **P0**: None currently known.
- **P1**: Refresh README screenshots after manual sanitized captures are provided; verify Firefox and WebKit behavior if cross-browser support becomes a requirement.
- **P2**: Add load characterization and a human-labeled score-calibration dataset without changing the local-first privacy boundary.

## 2026-07-26: Current Documentation Reconciliation (`443c5fc`)

### Changes

- Recorded the four manually captured, sanitized README screenshots and the guarded local stop command in the current-status documentation.
- Reconciled the professional test report with the implemented Chromium, Firefox, and WebKit CI smoke matrix.
- Preserved earlier development-log entries as historical records instead of changing their contemporaneous test counts or implementation limits.

### Verification

- Full local regression: `79 passed`.
- The README screenshot-documentation test confirms all four current manual assets are referenced.
- Exact-head CI passed for workflow policy, tests and Alembic migration, Chromium/Firefox/WebKit browser smoke, and Docker smoke: https://github.com/TomTang701/resume-growth-coach/actions/runs/30195978576

### Remaining Problems

- High-volume load behavior and human-labeled score calibration remain unverified.
- The project remains local-first and does not deploy or automate recruiting-platform activity.

### Future Work

- **P0**: None currently known.
- **P1**: None currently known.
- **P2**: Add load characterization and a human-labeled score-calibration dataset without changing the local-first privacy boundary.
