# Resume Growth Coach

Resume Growth Coach is a local-first AI backend project that compares a resume with a target job description, identifies skill and evidence gaps, and produces a practical growth roadmap.

The project runs deterministic analysis before any LLM generation. Ollama is optional: when it is offline, the app still returns a fit score, matched skills, missing skills, project evidence, and fallback goals.

## Features

- FastAPI backend with JSON APIs and a local HTML UI
- SQLite persistence through SQLAlchemy
- Pasted text and `.txt` / `.pdf` document input in both the API and local UI
- Deterministic skill matching and explainable fit scoring
- Evidence-aware fit scoring that distinguishes listed skills from project evidence
- Optional Ollama summaries with offline fallback
- Growth goals for 2-week, 1-month, and 3-month horizons
- Portfolio Planner that ranks non-duplicative project proposals from verified skill gaps
- Resume-eligibility gate that withholds resume bullets until tests, Docker, CI, documentation, and sanitized-demo evidence are supplied
- pytest coverage for parsing, matching, API flow, and fallback behavior

## Quick Start

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

After setup, launch the app with the one-click helper from the project root:

```powershell
.\Start-ResumeGrowthCoach.ps1
```

You can also double-click:

```text
Start-ResumeGrowthCoach.cmd
```

Both launchers start the FastAPI server and open the local web page automatically.
They also start the Ollama API if needed and verify that `qwen2.5:3b` is installed before opening the page.

Manual run command:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Run tests:

```powershell
pytest
```

Run the reusable adversarial quality gate:

```powershell
.\scripts\run-quality-gate.ps1
```

The quality gate runs the regression suite and API contract checks using a temporary SQLite database and a fake LLM response. It does not require Ollama and does not modify the local application database.

## Reproducible PostgreSQL Run

Docker Compose starts PostgreSQL and the application, runs Alembic migrations, and exposes the local UI at `http://127.0.0.1:8000`:

```powershell
.\scripts\run-docker-smoke.ps1
```

For normal local Docker use, run `docker compose up --build`. The Compose database credentials are development-only and must not be reused outside this local stack.

Alembic manages fresh PostgreSQL and SQLite schemas. An existing SQLite database created before migrations were introduced must be baselined once without changing its tables:

```powershell
.\.venv\Scripts\python.exe -m alembic stamp head
```

## Resume Evidence Gate

Portfolio Planner reads its eligibility state from `local_data/verification-evidence.json`; the API does not accept caller-provided verification flags. Generate the local evidence after substantive changes:

```powershell
.\scripts\record-verification-evidence.ps1 -LocalOnly
```

`-LocalOnly` intentionally records Docker and CI as incomplete and exits with code `1`. After Docker smoke passes and the exact commit's GitHub Actions run is green, run without `-LocalOnly` and include `-CiPassed`. Only a fully green evidence file can release a resume bullet draft.

Run the real local-model smoke test when Ollama is installed:

```powershell
.\scripts\run-ollama-smoke-test.ps1
```

Install the Chromium browser once, then run the real UI smoke test:

```powershell
python -m playwright install chromium
.\.venv\Scripts\python.exe tools\browser_smoke.py
```

Validate the local database schema and version marker:

```powershell
.\.venv\Scripts\python.exe tools\check_database_schema.py
```

## Developer Documentation

English is the default documentation language. Each handoff and log document has a separate Chinese counterpart for reference:

- [Developer Handoff](docs/HANDOFF.md) | [中文交接](docs/HANDOFF.zh-CN.md)
- [Development Log](docs/DEVELOPMENT_LOG.md) | [中文开发日志](docs/DEVELOPMENT_LOG.zh-CN.md)
- [Adversarial Test Log](docs/TEST_LOG.md) | [中文测试日志](docs/TEST_LOG.zh-CN.md)
- [Professional Test Report](docs/TEST_REPORT.md) | [中文测试报告](docs/TEST_REPORT.zh-CN.md)

The English file is the default entry point. Update the English document first and commit the matching `.zh-CN.md` translation in the same change.

## User Interface Walkthrough

The screenshots below use sanitized template data only. They do not include a real person's name, contact information, resume, or job application details.

### Start Screen

Paste a sanitized resume and a target job description into the two input boxes.

![Empty Resume Growth Coach screen](docs/images/01-empty-screen.png)

### Template Input

The left panel keeps the submitted resume and job description visible so the user can verify what was analyzed.

![Filled sanitized template input](docs/images/02-filled-template.png)

### Analysis Results

The right panel shows the deterministic fit score, the Ollama status and model name, matched skills, missing skills, evidence, roadmap, recommended jobs, and resume bullet drafts.

![Analysis results with sanitized sample data](docs/images/03-analysis-results.png)

### Matching Job Recommendations

The app also recommends the top matching job directions for the resume, with a score and a short reason for each option.

![Recommended matching jobs section](docs/images/04-job-recommendations.png)

## Optional Ollama Setup

Install Ollama and pull the default model:

```powershell
ollama pull qwen2.5:3b
```

If Ollama is not running, the application still returns deterministic analysis.
The default local-model request timeout is 60 seconds. Override it when needed with `RGC_OLLAMA_TIMEOUT_SECONDS`.

## API Overview

- `POST /api/documents/resume`
- `POST /api/documents/job-description`
- `POST /api/analyses`
- `GET /api/analyses/{analysis_id}`
- `GET /api/goals/{analysis_id}`
- `POST /api/portfolio-plans`
- `DELETE /api/documents/resume/{resume_id}`
- `DELETE /api/documents/job-description/{job_description_id}`

## Privacy Notes

Documents are stored locally until explicitly deleted through the document deletion API. Do not commit real resumes, real job descriptions, local databases, upload folders, or `.env` files. Use only sanitized sample data in public repositories.

Inspect old local data without deleting it:

```powershell
.\.venv\Scripts\python.exe tools\cleanup_local_data.py --older-than-days 30
```

Delete the matching local data only after reviewing the dry-run result:

```powershell
.\.venv\Scripts\python.exe tools\cleanup_local_data.py --older-than-days 30 --delete
```

## Sample Resume Bullets

These bullets should only be used after the matching implementation, persistence, UI, and tests are verified:

- Built a local-first AI resume growth coach with FastAPI, SQLite, SQLAlchemy, and Ollama to compare resumes against job descriptions.
- Implemented deterministic skill matching and gap scoring before LLM generation, reducing dependence on prompt-only analysis.
- Added PDF/text parsing, persisted analysis history, and generated 2-week, 1-month, and 3-month self-improvement roadmaps.
- Tested document upload, analysis, and offline LLM fallback flows with pytest and FastAPI TestClient.
