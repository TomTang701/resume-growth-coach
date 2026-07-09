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
