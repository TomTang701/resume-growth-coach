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
