from app.services.matching import analyze_resume_against_job
from app.services.ollama import safe_resume_bullets


def test_safe_resume_bullets_reject_missing_skill_claims():
    result = analyze_resume_against_job(
        "Built a Python FastAPI backend with SQL and Git.",
        "Software engineer role requiring Python, REST APIs, SQL, Git, and testing.",
    )
    bullets = [
        "Conducted comprehensive unit tests for a Java-based application using JUnit and Mockito.",
        "Built a Python FastAPI backend with SQL and Git.",
    ]

    safe = safe_resume_bullets(result, bullets)

    assert "Java" not in " ".join(safe)
    assert any("Python" in bullet for bullet in safe)
