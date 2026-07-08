from pathlib import Path

from fastapi.testclient import TestClient

from app.database import Base, configure_database, engine, init_db
from app.main import app


def make_client(tmp_path: Path) -> TestClient:
    configure_database(f"sqlite:///{tmp_path / 'test.sqlite3'}")
    Base.metadata.drop_all(bind=engine)
    init_db()
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

    goals_response = client.get(f"/api/goals/{body['analysis_id']}")
    assert goals_response.status_code == 200
    assert "2-week" in goals_response.json()


def test_home_page_renders(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "Resume Growth Coach" in response.text


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
    assert "excluding the current target job" in response.text


def test_empty_resume_is_rejected(tmp_path):
    client = make_client(tmp_path)

    response = client.post("/api/documents/resume", data={"text": ""})

    assert response.status_code == 400
