# Manual Screenshots and Safe Stop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** Publish Tom's real sanitized UI evidence and add a safe Windows command that stops only this checkout's local Uvicorn server.

**Architecture:** README assets are copied verbatim from the four manually supplied PNG files and validated by a documentation test. A common PowerShell lifecycle module owns launch, health verification, ignored PID-record persistence, and strictly verified process-tree shutdown; CMD files are thin user-facing wrappers.

**Tech Stack:** Markdown, PNG assets, Windows PowerShell 5.1, CMD, Uvicorn, pytest.

## Global Constraints

- Preserve manual image pixels; do not generate, crop, or reconstruct screenshots.
- Bind verification to http://127.0.0.1:8000/health only.
- Refuse a stop operation unless the PID record, command line, checkout path, and descendant listener agree.
- Do not stage Tom's pet_run_tv_monitor/, pet_run_tv_monitor_body_only/, or task-tv-monitor-base.png files.

---

### Task 1: Replace README screenshot evidence

**Files:**

- Create: docs/images/02-analysis-results.png, docs/images/03-growth-roadmap.png, docs/images/04-matching-jobs-and-bullets.png
- Modify: docs/images/01-empty-screen.png, README.md, tests/test_documentation.py
- Delete: docs/images/02-filled-template.png, docs/images/03-analysis-results.png, docs/images/04-job-recommendations.png

**Interfaces:**

- Consumes the four supplied C:\Users\tangz\AppData\Local\Temp\codex-clipboard-*.png files.
- Produces four README image references with exact filenames and sanitized alt text.

- [ ] **Step 1: Write a failing documentation assertion**

~~~python
def test_readme_uses_manual_screenshot_assets():
    readme = Path("README.md").read_text(encoding="utf-8")
    expected = {
        "docs/images/01-empty-screen.png",
        "docs/images/02-analysis-results.png",
        "docs/images/03-growth-roadmap.png",
        "docs/images/04-matching-jobs-and-bullets.png",
    }
    assert expected <= set(re.findall(r"docs/images/[A-Za-z0-9_.-]+\.png", readme))
    assert "02-filled-template.png" not in readme
~~~

- [ ] **Step 2: Run the focused test**

Run: .\.venv\Scripts\python.exe -m pytest tests\test_documentation.py -q

Expected: failure because the README names legacy assets.

- [ ] **Step 3: Copy manual PNGs verbatim and update walkthrough text**

~~~powershell
Copy-Item -LiteralPath 'C:\Users\tangz\AppData\Local\Temp\codex-clipboard-4edd39c0-8bd3-4e55-b7e3-c737515aa32b.png' -Destination 'docs\images\01-empty-screen.png'
Copy-Item -LiteralPath 'C:\Users\tangz\AppData\Local\Temp\codex-clipboard-6a01da8a-1e0c-40f2-a448-676888e894ba.png' -Destination 'docs\images\02-analysis-results.png'
Copy-Item -LiteralPath 'C:\Users\tangz\AppData\Local\Temp\codex-clipboard-14d691cd-57d8-4448-ae4e-6c54f71e8a58.png' -Destination 'docs\images\03-growth-roadmap.png'
Copy-Item -LiteralPath 'C:\Users\tangz\AppData\Local\Temp\codex-clipboard-68655d83-e4e9-4104-9fb1-3eb8802c4b63.png' -Destination 'docs\images\04-matching-jobs-and-bullets.png'
~~~

Rename the four sections to Start Screen, Analysis Results, Growth Roadmap and Planner, and Matching Jobs and Bullet Drafts. Delete only superseded legacy assets.

- [ ] **Step 4: Run focused test and inspect the copied assets**

Run: .\.venv\Scripts\python.exe -m pytest tests\test_documentation.py -q

Expected: pass and every README path exists.

- [ ] **Step 5: Commit screenshot evidence**

~~~powershell
git add README.md docs/images tests/test_documentation.py
git commit -m "docs: refresh manual UI screenshots"
~~~

### Task 2: Implement verified local server lifecycle

**Files:**

- Create: scripts/local-server.ps1, Stop-ResumeGrowthCoach.ps1, Stop-ResumeGrowthCoach.cmd, tests/test_local_lifecycle.py
- Modify: Start-ResumeGrowthCoach.ps1, Start-ResumeGrowthCoach.cmd, .gitignore, README.md

**Interfaces:**

- scripts/local-server.ps1 -Action Start|Stop|Status [-WhatIf] owns local_data\local-server.json.
- Stop-ResumeGrowthCoach.ps1 [-WhatIf] delegates to the lifecycle module.
- Stop-ResumeGrowthCoach.cmd invokes the PowerShell wrapper with ExecutionPolicy Bypass.

- [ ] **Step 1: Write failing record-validation tests**

~~~python
def test_pid_record_rejects_wrong_checkout(tmp_path):
    payload = {"pid": 1234, "checkout": "C:\\wrong", "command_marker": "uvicorn app.main:app"}
    assert lifecycle_record_is_valid(payload, checkout=tmp_path, observed_command="cmd") is False

def test_pid_record_requires_expected_command(tmp_path):
    payload = {"pid": 1234, "checkout": str(tmp_path), "command_marker": "uvicorn app.main:app"}
    assert lifecycle_record_is_valid(payload, checkout=tmp_path, observed_command="cmd /k uvicorn app.main:app") is True
~~~

- [ ] **Step 2: Run focused tests**

Run: .\.venv\Scripts\python.exe -m pytest tests\test_local_lifecycle.py -q

Expected: import failure because the lifecycle validator does not exist.

- [ ] **Step 3: Implement lifecycle module and wrappers**

Start uses absolute Python and --app-dir arguments, waits for /health, then writes { pid, checkout, command_marker }. Stop traces recorded PID descendants via Get-CimInstance Win32_Process, requires a port-8000 listener below the verified tree, and invokes taskkill /PID <recorded-pid> /T /F only after all checks. WhatIf runs all checks but skips taskkill.

- [ ] **Step 4: Verify lifecycle behavior**

Run: powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\Start-ResumeGrowthCoach.ps1

Run: powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\Stop-ResumeGrowthCoach.ps1 -WhatIf

Run: powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\Stop-ResumeGrowthCoach.ps1

Expected: health succeeds; WhatIf names only the recorded process; port 8000 has no recorded listener after stop.

- [ ] **Step 5: Commit lifecycle support**

~~~powershell
git add .gitignore README.md Start-ResumeGrowthCoach.* Stop-ResumeGrowthCoach.* scripts/local-server.ps1 tests/test_local_lifecycle.py
git commit -m "feat: add verified local server stop command"
~~~

### Task 3: Run final Growth Coach evidence gates

**Files:**

- Modify: local_data/verification-evidence.json (ignored evidence only)

- [ ] **Step 1: Run local verification**

Run: .\.venv\Scripts\python.exe -m pytest -q

Run: foreach ($browser in @('chromium','firefox','webkit')) { $env:RGC_BROWSER=$browser; .\.venv\Scripts\python.exe tools\browser_smoke.py }

Run: powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\scripts\record-verification-evidence.ps1

- [ ] **Step 2: Inspect evidence and working tree**

Run: Get-Content -Raw local_data\verification-evidence.json

Run: git status --short

Expected: all eligibility booleans are true for HEAD; only Tom's known untracked pet assets remain.

