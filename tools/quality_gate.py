"""Run the project's regression suite and adversarial API contract checks.

This tool is intentionally independent of a running Ollama service and the
developer's local database. It is suitable for local changes and CI jobs.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def fake_llm(result, model_name=None):
    from app.services.goals import build_fallback_summary, build_resume_bullets
    from app.services.ollama import DEFAULT_MODEL

    return {
        "model_status": "offline_fallback",
        "model_name": model_name or DEFAULT_MODEL,
        "summary": build_fallback_summary(result),
        "project_suggestions": result.recommended_improvement_areas,
        "resume_bullet_drafts": build_resume_bullets(result),
    }


def run_pytest() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        check=False,
    )
    return result.returncode


def run_api_contract_checks() -> dict[str, object]:
    from app import database
    from app import main

    original_llm = main.generate_llm_analysis
    checks: dict[str, object] = {}
    with TemporaryDirectory(prefix="resume-growth-coach-quality-") as temp_dir:
        database.configure_database(f"sqlite:///{Path(temp_dir) / 'quality.sqlite3'}")
        database.init_db()
        main.generate_llm_analysis = fake_llm
        try:
            with TestClient(main.app) as client:
                health = client.get("/health")
                assert health.status_code == 200 and health.json() == {"status": "ok"}
                checks["health"] = "passed"

                resume = client.post(
                    "/api/documents/resume",
                    data={"text": "Built Python FastAPI APIs with SQL, Git, pytest, and Docker."},
                )
                job = client.post(
                    "/api/documents/job-description",
                    data={"text": "Backend Software Engineer"},
                )
                assert resume.status_code == 200 and job.status_code == 200
                analysis = client.post(
                    "/api/analyses",
                    json={
                        "resume_id": resume.json()["resume_id"],
                        "job_description_id": job.json()["job_description_id"],
                    },
                )
                assert analysis.status_code == 200
                detail = client.get(f"/api/analyses/{analysis.json()['analysis_id']}")
                body = detail.json()
                assert detail.status_code == 200
                assert body["overall_fit_score"] > 0
                assert len(body["recommended_matching_jobs"]) == 3
                assert all(item["title"] != "Backend Software Engineer" for item in body["recommended_matching_jobs"])
                checks["analysis_and_recommendations"] = "passed"

                malformed_pdf = client.post(
                    "/api/documents/resume",
                    files={"file": ("broken.pdf", b"not a PDF", "application/pdf")},
                )
                assert malformed_pdf.status_code == 400
                checks["malformed_pdf"] = "passed"

                oversized = client.post(
                    "/api/documents/resume",
                    data={"text": "x" * 1_000_001},
                )
                assert oversized.status_code == 413
                checks["oversized_input"] = "passed"

                assert client.get("/api/analyses/999999").status_code == 404
                checks["not_found"] = "passed"
        finally:
            main.generate_llm_analysis = original_llm
            database.engine.dispose()
    return checks


def main_entry() -> int:
    pytest_code = run_pytest()
    if pytest_code != 0:
        return pytest_code
    try:
        checks = run_api_contract_checks()
    except Exception as exc:
        print(json.dumps({"api_contract_checks": "failed", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"pytest": "passed", "api_contract_checks": checks}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main_entry())
