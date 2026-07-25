import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from app import database
from app.main import app


def make_client(tmp_path: Path) -> TestClient:
    database.configure_database(f"sqlite:///{tmp_path / 'test.sqlite3'}")
    database.Base.metadata.drop_all(bind=database.engine)
    database.init_db()
    return TestClient(app)


def test_document_analysis_and_goals_flow(tmp_path):
    client = make_client(tmp_path)

    resume_response = client.post(
        "/api/documents/resume",
        data={"text": "Built a FastAPI REST API with SQLite, SQLAlchemy, pytest, and Git."},
    )
    assert resume_response.status_code == 200
    resume_id = resume_response.json()["resume_id"]

    job_response = client.post(
        "/api/documents/job-description",
        data={
            "text": """
            Required qualifications:
            - Build backend services using Python, FastAPI, SQL, Docker, and Git.
            - Write unit tests for API workflows.
            """
        },
    )
    assert job_response.status_code == 200
    job_id = job_response.json()["job_description_id"]

    analysis_response = client.post(
        "/api/analyses",
        json={"resume_id": resume_id, "job_description_id": job_id},
    )
    assert analysis_response.status_code == 200
    body = analysis_response.json()
    assert body["analysis_id"] > 0
    assert body["ollama_status"] in {"available", "offline_fallback"}
    assert body["ollama_model"]

    detail_response = client.get(f"/api/analyses/{body['analysis_id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert "FastAPI" in detail["matched_skills"]
    assert "Docker" in detail["missing_skills"]
    assert detail["english_resume_bullet_drafts"]
    assert len(detail["recommended_matching_jobs"]) == 3
    assert detail["recommended_matching_jobs"][0]["title"]
    assert detail["ollama_model"]
    assert detail["ollama_display"]
    assert "evidence_coverage" in detail

    goals_response = client.get(f"/api/goals/{body['analysis_id']}")
    assert goals_response.status_code == 200
    assert "2-week" in goals_response.json()


def test_ui_accepts_file_only_resume_and_job_inputs(tmp_path):
    client = make_client(tmp_path)

    response = client.post(
        "/ui/analyze",
        files={
            "resume_file": ("resume.txt", b"Built Python APIs with Git.", "text/plain"),
            "job_description_file": ("job.txt", b"Software Engineer requiring Python and Git.", "text/plain"),
        },
    )

    assert response.status_code == 200
    assert "Target JD fit score" in response.text
    assert "Python" in response.text


def test_home_page_renders(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "Resume Growth Coach" in response.text


def test_health_endpoint_is_fast_and_stable(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ui_preserves_submitted_text_and_varies_score(tmp_path):
    client = make_client(tmp_path)
    resume = "Marketing assistant who planned social media campaigns and reported campaign analytics."
    job = "Marketing coordinator role focused on campaign planning, social media, content calendars, and analytics reporting."

    response = client.post("/ui/analyze", data={"resume_text": resume, "job_description_text": job})

    assert response.status_code == 200
    assert resume in response.text
    assert job in response.text
    assert "20.0" not in response.text
    assert "Alternative Matching Jobs" in response.text
    assert "same canonical role templates" in response.text


def test_empty_resume_is_rejected(tmp_path):
    client = make_client(tmp_path)

    response = client.post("/api/documents/resume", data={"text": ""})

    assert response.status_code == 400


def test_malformed_pdf_returns_client_error_not_server_traceback(tmp_path):
    client = make_client(tmp_path)

    response = client.post(
        "/api/documents/resume",
        files={"file": ("resume.pdf", b"not a PDF", "application/pdf")},
    )

    assert response.status_code == 400
    assert "could not be parsed" in response.json()["detail"]


def test_oversized_pasted_document_is_rejected(tmp_path):
    client = make_client(tmp_path)

    response = client.post("/api/documents/resume", data={"text": "x" * 1_000_001})

    assert response.status_code == 413


def test_unknown_analysis_returns_not_found(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/api/analyses/999999")

    assert response.status_code == 404


def test_ui_validation_error_preserves_inputs_and_escapes_html(tmp_path):
    client = make_client(tmp_path)
    response = client.post(
        "/ui/analyze",
        data={"resume_text": "Candidate <script>alert('x')</script>", "job_description_text": ""},
    )

    assert response.status_code == 200
    assert "Job description content is required." in response.text
    assert "&lt;script&gt;alert(&#39;x&#39;)&lt;/script&gt;" in response.text
    assert "<script>alert('x')</script>" not in response.text


def test_unsupported_upload_and_empty_file_are_rejected(tmp_path):
    client = make_client(tmp_path)
    unsupported = client.post(
        "/api/documents/resume",
        files={"file": ("resume.docx", b"content", "application/octet-stream")},
    )
    empty = client.post(
        "/api/documents/resume",
        files={"file": ("resume.txt", b"", "text/plain")},
    )

    assert unsupported.status_code == 400
    assert "Only .txt and .pdf" in unsupported.json()["detail"]
    assert empty.status_code == 400
    assert "empty" in empty.json()["detail"]


def test_oversized_job_description_is_rejected(tmp_path):
    client = make_client(tmp_path)

    response = client.post("/api/documents/job-description", data={"text": "x" * 1_000_001})

    assert response.status_code == 413


def test_analysis_with_missing_document_returns_not_found(tmp_path):
    client = make_client(tmp_path)

    response = client.post("/api/analyses", json={"resume_id": 999, "job_description_id": 999})

    assert response.status_code == 404


def test_concurrent_analysis_requests_are_isolated(tmp_path):
    client = make_client(tmp_path)

    def run_flow(index: int) -> int:
        resume = client.post(
            "/api/documents/resume",
            data={"text": f"Built Python API project {index} with Git."},
        )
        job = client.post(
            "/api/documents/job-description",
            data={"text": "Software Engineer requiring Python and Git."},
        )
        assert resume.status_code == 200
        assert job.status_code == 200
        analysis = client.post(
            "/api/analyses",
            json={"resume_id": resume.json()["resume_id"], "job_description_id": job.json()["job_description_id"]},
        )
        assert analysis.status_code == 200
        return analysis.json()["analysis_id"]

    with ThreadPoolExecutor(max_workers=6) as executor:
        analysis_ids = list(executor.map(run_flow, range(12)))

    assert len(set(analysis_ids)) == 12
    assert all(client.get(f"/api/analyses/{analysis_id}").status_code == 200 for analysis_id in analysis_ids)


def test_deleting_resume_removes_related_analysis_data(tmp_path):
    client = make_client(tmp_path)
    resume = client.post("/api/documents/resume", data={"text": "Built Python APIs with Git."}).json()
    job = client.post("/api/documents/job-description", data={"text": "Software Engineer requiring Python and Git."}).json()
    analysis = client.post(
        "/api/analyses",
        json={"resume_id": resume["resume_id"], "job_description_id": job["job_description_id"]},
    ).json()

    deleted = client.delete(f"/api/documents/resume/{resume['resume_id']}")

    assert deleted.status_code == 200
    assert deleted.json()["deleted_analysis_count"] == 1
    assert client.get(f"/api/analyses/{analysis['analysis_id']}").status_code == 404
    assert client.delete(f"/api/documents/resume/{resume['resume_id']}").status_code == 404


def test_upload_size_limit_is_enforced_before_full_file_processing(tmp_path):
    client = make_client(tmp_path)
    oversized = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/api/documents/resume",
        files={"file": ("resume.txt", oversized, "text/plain")},
    )

    assert response.status_code == 400
    assert "too large" in response.json()["detail"]


def test_portfolio_plan_ignores_client_claimed_evidence_without_local_manifest(tmp_path, monkeypatch):
    monkeypatch.setenv("RGC_EVIDENCE_PATH", str(tmp_path / "missing-verification-evidence.json"))
    client = make_client(tmp_path)
    resume = client.post("/api/documents/resume", data={"text": "Built FastAPI with Python."}).json()
    job = client.post("/api/documents/job-description", data={"text": "Backend role requiring PostgreSQL, Docker, React, and CI/CD."}).json()
    analysis = client.post("/api/analyses", json={"resume_id": resume["resume_id"], "job_description_id": job["job_description_id"]}).json()

    response = client.post(
        "/api/portfolio-plans",
        json={
            "analysis_id": analysis["analysis_id"],
            "existing_project_names": ["Resume Growth Coach"],
            "evidence": {"tests_passed": True, "docker_smoke_passed": True, "ci_passed": True, "documentation_complete": True, "sanitized_demo_verified": True},
        },
    )

    proposal = response.json()["proposals"][0]
    assert proposal["resume_eligible"] is False
    assert proposal["english_resume_bullet_draft"] is None


def test_portfolio_plan_unlocks_only_from_verified_local_manifest(tmp_path, monkeypatch):
    evidence_path = tmp_path / "verification-evidence.json"
    evidence_path.write_text(
        json.dumps({"tests_passed": True, "docker_smoke_passed": True, "ci_passed": True, "documentation_complete": True, "sanitized_demo_verified": True}),
        encoding="utf-8",
    )
    monkeypatch.setenv("RGC_EVIDENCE_PATH", str(evidence_path))
    client = make_client(tmp_path)
    resume = client.post("/api/documents/resume", data={"text": "Built FastAPI with Python."}).json()
    job = client.post("/api/documents/job-description", data={"text": "Backend role requiring PostgreSQL, Docker, React, and CI/CD."}).json()
    analysis = client.post("/api/analyses", json={"resume_id": resume["resume_id"], "job_description_id": job["job_description_id"]}).json()

    response = client.post(
        "/api/portfolio-plans",
        json={"analysis_id": analysis["analysis_id"], "existing_project_names": ["Resume Growth Coach"]},
    )

    proposal = response.json()["proposals"][0]
    assert proposal["resume_eligible"] is True
    assert proposal["english_resume_bullet_draft"]


def test_home_and_api_expose_builtin_job_templates(tmp_path):
    client = make_client(tmp_path)

    home = client.get("/")
    templates = client.get("/api/job-templates")

    assert home.status_code == 200
    assert "Backend / Full-stack Internship" in home.text
    assert templates.status_code == 200
    assert any(item["slug"] == "backend_full_stack_intern" for item in templates.json()["templates"])


def test_ui_template_analysis_shows_portfolio_planner_with_evidence_gate(tmp_path):
    client = make_client(tmp_path)

    response = client.post(
        "/ui/analyze",
        data={
            "resume_text": "Built a FastAPI service with Python, SQLite, SQLAlchemy, and pytest.",
            "job_template": "backend_full_stack_intern",
        },
    )

    assert response.status_code == 200
    assert "Portfolio Planner" in response.text
    assert "Team Job Workflow" in response.text
    assert "Implementation active; evidence gate pending." in response.text
    assert "Not resume-eligible until all verification evidence is recorded." in response.text
