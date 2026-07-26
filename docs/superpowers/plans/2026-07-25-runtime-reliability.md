# Runtime Reliability Hardening Plan

> **For Codex:** Execute these tasks directly in dependency order, preserving the repository's local-first and sanitized-data boundaries.

**Goal:** Replace stale Portfolio Planner eligibility text with evidence-derived status, make browser validation deterministic, and run browser smoke in CI.

**Architecture:** The analysis payload will load the existing verification evidence once and derive a presentation-only portfolio status. The HTML template consumes that status. Browser smoke receives an explicit missing evidence path so its expectations do not depend on a developer's local evidence manifest. CI adds a browser job without changing the application runtime.

**Tech Stack:** FastAPI, Jinja2, pytest, Playwright, GitHub Actions.

---

### Task 1: Make Portfolio Planner eligibility evidence-derived

**Files:**
- Modify: `app/main.py`
- Modify: `app/templates/index.html`
- Modify: `tests/test_api.py`

**Step 1: Write the failing test**

Create one analysis-page assertion using a deliberately missing `RGC_EVIDENCE_PATH`. It must prove the project status names the incomplete verification fields and must reject the old static “Implementation active” copy. Create a second assertion using a complete manifest and prove it renders eligible status.

**Step 2: Run the focused test to verify it fails**

Run: `python -m pytest tests/test_api.py -k portfolio -q`
Expected: failure because the current static project record ignores the evidence manifest.

**Step 3: Write minimal implementation**

Add a small helper in `app/main.py` that maps `EvidenceChecklist` to `eligible`, `status`, and `remaining_evidence`. Load evidence once in `build_analysis_payload`, pass it both to `build_portfolio_plan` and this helper, and remove the cross-repository static project record. Render the project status and a dynamic explanatory note in the template.

**Step 4: Run focused tests**

Run: `python -m pytest tests/test_api.py -k portfolio -q`
Expected: pass.

**Step 5: Commit**

```powershell
git add app/main.py app/templates/index.html tests/test_api.py
git commit -m "feat: derive portfolio eligibility from evidence"
```

### Task 2: Make browser and CI validation exercise the evidence gate

**Files:**
- Modify: `tools/browser_smoke.py`
- Modify: `.github/workflows/ci.yml`

**Step 1: Write the failing browser expectation**

Set `RGC_EVIDENCE_PATH` in the spawned server environment to a missing file beneath the temporary smoke directory. Assert the rendered page contains the incomplete-evidence message and does not contain the retired static copy.

**Step 2: Run browser smoke to verify it fails**

Run: `python tools/browser_smoke.py`
Expected: failure until the dynamic status implementation is in place.

**Step 3: Implement CI execution**

Keep the existing test and Alembic migration steps. Add a separate browser-smoke job that installs requirements, installs Chromium through Playwright, and invokes `python tools/browser_smoke.py`.

**Step 4: Run the local browser gate**

Run: `python tools/browser_smoke.py`
Expected: browser flow passes with deterministic incomplete evidence.

**Step 5: Commit**

```powershell
git add tools/browser_smoke.py .github/workflows/ci.yml
git commit -m "ci: run deterministic browser smoke"
```

### Task 3: Record verification accurately

**Files:**
- Modify: `docs/DEVELOPMENT_LOG.zh-CN.md`
- Modify: `docs/DEVELOPMENT_LOG.md`
- Modify: `docs/TEST_LOG.md`

**Step 1: Append a dated entry**

Record the changed behavior, all local commands, and the exact CI run URL after the new head passes. Preserve historical entries rather than rewriting prior environmental observations.

**Step 2: Run full regression and artifact gates**

Run: `.\.venv\Scripts\python.exe -m pytest -q`
Run: `.\.venv\Scripts\python.exe tools/quality_gate.py`
Run: `.\.venv\Scripts\python.exe tools/browser_smoke.py`
Run: `.\scripts\run-docker-smoke.ps1`
Run: `.\scripts\record-verification-evidence.ps1`

Expected: all tests and local gates pass; the recorded evidence manifest is fully eligible only after exact-head CI succeeds.

**Step 3: Review and commit**

Run: `git diff --check`
Run: `git status --short`
Commit only the three logs and generated manifest if it changed; do not stage unrelated local files.
