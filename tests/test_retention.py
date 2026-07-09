from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app import database, models
from app.main import app
from app.services.retention import delete_documents_older_than


def test_retention_dry_run_and_delete_remove_old_graph(tmp_path: Path):
    database.configure_database(f"sqlite:///{tmp_path / 'retention.sqlite3'}")
    database.Base.metadata.drop_all(bind=database.engine)
    database.init_db()

    with TestClient(app) as client:
        resume = client.post("/api/documents/resume", data={"text": "Built Python APIs with Git."}).json()
        job = client.post("/api/documents/job-description", data={"text": "Software Engineer requiring Python and Git."}).json()
        analysis = client.post(
            "/api/analyses",
            json={"resume_id": resume["resume_id"], "job_description_id": job["job_description_id"]},
        ).json()

    old_time = datetime.now(UTC) - timedelta(days=45)
    with database.SessionLocal() as db:
        db.query(models.Document).update({"created_at": old_time})
        db.query(models.JobDescription).update({"created_at": old_time})
        db.flush()
        preview = delete_documents_older_than(db, 30, dry_run=True)
        assert preview == {
            "dry_run": True,
            "resume_count": 1,
            "job_description_count": 1,
            "analysis_count": 1,
        }
        assert db.get(models.Analysis, analysis["analysis_id"]) is not None

        deleted = delete_documents_older_than(db, 30)
        assert deleted["dry_run"] is False
        assert db.get(models.Document, resume["resume_id"]) is None
        assert db.get(models.JobDescription, job["job_description_id"]) is None
        assert db.get(models.Analysis, analysis["analysis_id"]) is None


def test_retention_rejects_non_positive_days(tmp_path: Path):
    database.configure_database(f"sqlite:///{tmp_path / 'retention.sqlite3'}")
    database.init_db()

    with database.SessionLocal() as db:
        try:
            delete_documents_older_than(db, 0)
        except ValueError as exc:
            assert "at least 1" in str(exc)
        else:
            raise AssertionError("Expected invalid retention window to fail")
