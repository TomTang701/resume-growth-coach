from app.services.matching import analyze_resume_against_job
from app.services.ollama import generate_llm_analysis, get_ollama_timeout_seconds, parse_json_response, safe_resume_bullets


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


def test_ollama_null_fields_are_normalized_without_crashing():
    parsed = parse_json_response('{"summary": null, "project_suggestions": null, "resume_bullet_drafts": null}')

    assert parsed == {"summary": "", "project_suggestions": [], "resume_bullet_drafts": []}


def test_ollama_non_list_fields_are_ignored():
    parsed = parse_json_response('{"summary": "Ready", "project_suggestions": "bad", "resume_bullet_drafts": {}}')

    assert parsed == {"summary": "Ready", "project_suggestions": [], "resume_bullet_drafts": []}


def test_bullet_filter_does_not_confuse_javascript_with_java():
    result = analyze_resume_against_job(
        "Built JavaScript frontend features with React, HTML, CSS, and Git.",
        "Frontend developer role requiring JavaScript, React, HTML, CSS, and Git.",
    )

    safe = safe_resume_bullets(result, ["Built JavaScript frontend features with React and Git."])

    assert safe == ["Built JavaScript frontend features with React and Git."]


def test_valid_ollama_response_is_marked_available(monkeypatch):
    result = analyze_resume_against_job(
        "Built a Python FastAPI backend with SQL and Git.",
        "Software engineer role requiring Python, SQL, and Git.",
    )

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"response":"{\\"summary\\":\\"Good fit.\\",\\"project_suggestions\\":[],\\"resume_bullet_drafts\\":[\\"Built a Python FastAPI backend with SQL and Git.\\"]}"}'

    monkeypatch.setattr("app.services.ollama.urllib.request.urlopen", lambda *args, **kwargs: Response())

    output = generate_llm_analysis(result)

    assert output["model_status"] == "available"
    assert output["model_name"]


def test_malformed_ollama_response_uses_fallback(monkeypatch):
    result = analyze_resume_against_job("Python", "Software Engineer")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"response":"not json"}'

    monkeypatch.setattr("app.services.ollama.urllib.request.urlopen", lambda *args, **kwargs: Response())

    output = generate_llm_analysis(result)

    assert output["model_status"] == "offline_fallback"


def test_invalid_ollama_timeout_configuration_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("RGC_OLLAMA_TIMEOUT_SECONDS", "not-a-number")

    assert get_ollama_timeout_seconds() == 60.0


def test_ollama_timeout_configuration_is_bounded(monkeypatch):
    monkeypatch.setenv("RGC_OLLAMA_TIMEOUT_SECONDS", "9999")
    assert get_ollama_timeout_seconds() == 300.0

    monkeypatch.setenv("RGC_OLLAMA_TIMEOUT_SECONDS", "0")
    assert get_ollama_timeout_seconds() == 1.0
