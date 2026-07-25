# Adversarial Test Log

This is the primary test log for correctness, stability, edge cases, and practical user flow. Results describe current implementation behavior and do not claim that the score predicts hiring outcomes.

The Chinese counterpart is [TEST_LOG.zh-CN.md](TEST_LOG.zh-CN.md). Keep both files semantically identical; update the English file first, then update the Chinese translation in the same commit.

## 2026-07-09 Test Round

Automated result: `36 passed, 1 warning`; all API contract checks in `tools/quality_gate.py` passed.

### Checked

- Empty resume, empty job description, empty upload, missing file, and unsupported extensions.
- Resume and job description inputs over 1,000,000 characters.
- Whether malicious HTML is escaped in the rendered UI.
- Whether missing document and analysis IDs return stable 404 responses.
- Whether malformed PDFs return 400 instead of a traceback.
- Ollama availability, missing model, malformed model JSON, and timeout configuration.
- Whether direct and recommended scores match for the same canonical role and whether the current role is excluded.
- Very short text, skill-free job descriptions, and skill-only resumes without project evidence.

### Suspicious Findings and Handling

| Suspicion | Result | Handling |
|---|---|---|
| Every resume produced the same fallback result | Fixed | Deterministic analysis runs first; LLM failure only affects explanation, not structured matching or score |
| Recommended jobs repeated the current role | Fixed | Recommendations use canonical role titles and exclude the current role |
| Recommended scores differed from direct searches | Fixed | Recommendations use the same canonical title scoring path as direct analysis |
| A skills-only resume could score close to perfect | Fixed/limited | Evidence coverage lowers the score; a no-evidence case cannot reach 100 |
| User HTML could be injected into the page | Passed | Jinja autoescape is active and covered by a regression test |
| Submitted input disappeared after a validation error | Passed | UI preserves submitted input and has a regression test |
| Ollama was installed but its API was not listening | Passed | Startup scripts start the service and run a real generation smoke test |

### Not Checked or Requiring Specialized Tests

- No real browser click-level test has been run, so cross-browser form behavior, scrolling, and network-error rendering remain unverified.
- PDFs containing tables, images, scans, or complex multi-page layouts have not received full extraction-accuracy testing.
- Concurrency, process-crash recovery, and SQLite write-load testing have not been run.
- All branches for first-time model download, insufficient GPU memory, and port conflicts have not been verified.
- No human-labeled dataset exists, so score correlation with real hiring outcomes is unverified.

### User Experience Notes

- The normal text-to-analysis flow is coherent; invalid input remains visible, and results distinguish direct score, evidence coverage, and model status.
- The launcher is more reliable than manual environment activation, although first model load can take time.
- Fallback remains usable, but users must understand that it is not local-model-generated output.

### Edge-Case Conclusion

- Covered extreme inputs do not produce unhandled exceptions; they return 400/404/413 or a safely escaped 200 HTML page.
- The real Ollama smoke test passed. Deterministic fallback should still work when Ollama is unavailable, but a separate test with the service deliberately stopped remains recommended.

## Reusable Commands

```powershell
./scripts/run-quality-gate.ps1
```

or:

```powershell
.\.venv\Scripts\python.exe tools\quality_gate.py
```

## 2026-07-09 P1 Remediation Verification

- Verified UI file-only submission for both resume and job description.
- Verified oversized uploads are rejected after bounded chunked reading.
- Verified deleting a resume removes its related analysis records.
- Verified non-English Ollama user-facing output falls back safely.
- Verified the real `qwen2.5:3b` smoke test passes.
- Final automated result: `41 passed, 1 warning`.

## 2026-07-09 Retention and Stability Follow-up

### Checked

- Dry-run retention cleanup reports old resumes, job descriptions, and dependent analyses without deleting them.
- Explicit cleanup removes old documents and their analyses, skill matches, and growth goals.
- Invalid retention windows are rejected.
- The full regression suite and API quality gate remain green after the cleanup feature.
- Browser tooling availability was checked; Playwright and Selenium are not installed.

### Results

- Retention cleanup: passed.
- Dependent-record cleanup: passed.
- Destructive action requires explicit `--delete`: passed by command design and unit coverage.
- Final automated result: `43 passed, 1 warning`.

### Remaining Coverage

- No browser click-level test was executed because the browser automation dependencies are unavailable.
- No concurrent SQLite load test or migration rehearsal was executed.
- Score calibration against human-labeled hiring outcomes remains unavailable.

### Reproduction Commands

```powershell
.\.venv\Scripts\python.exe tools\cleanup_local_data.py --older-than-days 30
.\.venv\Scripts\python.exe tools\cleanup_local_data.py --older-than-days 30 --delete
```

## 2026-07-09 Baseline and Concurrency Verification

### Checked

- Five fixed score golden cases covering minimal input, skills-only input, project evidence, backend matching, and non-engineering keyword overlap.
- Three concurrent API flows using a file-backed SQLite database.
- Analysis IDs and result retrieval remained isolated across concurrent requests.
- Browser executable and Python browser automation availability.

### Results

- Score golden baseline: passed.
- Concurrent analysis flow: passed.
- Browser automation: blocked; Playwright, Selenium, and common browser commands are unavailable.
- Final automated result: `49 passed, no warnings`.

### Remaining Coverage

- SQLite migration/version upgrade rehearsal is still not available.
- Human-labeled score calibration is still unavailable.
- The previous Starlette/httpx warning is resolved by the compatible test-client dependency path.

## 2026-07-09 Browser and Schema Verification

### Checked

- Real headless Chromium page load and title.
- Text-only analysis through the actual form.
- Validation error recovery with preserved page state.
- File-only resume and job-description submission through the actual browser controls.
- Local schema version marker and required table/column validation.
- Twelve concurrent file-backed SQLite API flows.

### Results

- Chromium browser smoke: passed.
- Schema validation: passed, version `1`.
- Twelve-flow concurrency smoke: passed.
- Full regression: `49 passed`, no warnings.

### Remaining Coverage

- Firefox/WebKit and cross-browser behavior are not tested.
- The browser smoke is not yet running in CI.
- Schema version protection exists, but historical migration scripts do not.
- High-volume load and human-labeled score calibration remain open.

## 2026-07-09 CLI and Dependency Recheck

- `httpx2==2.5.0` installed and dependency files updated.
- Full regression and quality gate: `49 passed`, no warning.
- Direct `cleanup_local_data.py --help`: initially failed because of a root-path import issue; fixed and retested successfully.

## 2026-07-25 Portfolio and Evidence-Gate Verification

### Checked

- Built-in job template selection through the rendered form and API.
- Planner display for active work and non-duplicative proposals.
- Rejection of client-claimed verification flags without a local evidence manifest.
- Eligibility release only when a fully positive local manifest is present.
- Evidence script execution in local-only mode.

### Results

- Full regression: `57 passed`.
- Chromium smoke test: passed with template and planner coverage.
- Local evidence correctly records Docker and CI as incomplete and exits with code `1`.

### Remaining Coverage

- Docker Compose smoke and exact-head GitHub Actions remain unavailable in the current environment.
- Cross-browser coverage and score calibration remain open.
