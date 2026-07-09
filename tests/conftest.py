import pytest


@pytest.fixture(autouse=True)
def isolate_external_llm(monkeypatch):
    """Keep API tests deterministic and independent of a locally running Ollama."""
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

    monkeypatch.setattr("app.main.generate_llm_analysis", fake_llm)
