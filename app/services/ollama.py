import json
import http.client
import urllib.error
import urllib.request

from app.services.goals import build_fallback_summary, build_resume_bullets
from app.services.matching import SKILL_ALIASES, DeterministicResult


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:3b"


def generate_llm_analysis(result: DeterministicResult, model_name: str | None = None) -> dict:
    model = model_name or DEFAULT_MODEL
    prompt = build_prompt(result)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }

    try:
        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            body = json.loads(response.read().decode("utf-8"))
        parsed = parse_json_response(body.get("response", ""))
        parsed["resume_bullet_drafts"] = safe_resume_bullets(result, parsed.get("resume_bullet_drafts", []))
        parsed["model_status"] = "available"
        parsed["model_name"] = model
        return parsed
    except (urllib.error.URLError, TimeoutError, http.client.HTTPException, OSError, json.JSONDecodeError, ValueError):
        return {
            "model_status": "offline_fallback",
            "model_name": model,
            "summary": build_fallback_summary(result),
            "project_suggestions": result.recommended_improvement_areas,
            "resume_bullet_drafts": build_resume_bullets(result),
        }


def build_prompt(result: DeterministicResult) -> str:
    return f"""
You are a resume growth coach. Return only valid JSON.

Rules:
- Write every user-facing value in English.
- Do not invent completed work.
- Separate verified resume evidence from future suggestions.
- Keep suggestions practical for a student or early-career software engineer.

Deterministic analysis:
{json.dumps(result.to_dict(), indent=2)}

Return this JSON shape:
{{
  "summary": "short fit summary",
  "project_suggestions": ["suggestion 1", "suggestion 2"],
  "resume_bullet_drafts": ["truthful draft bullet 1", "truthful draft bullet 2"]
}}
""".strip()


def parse_json_response(raw: str) -> dict:
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Ollama response did not include JSON.")
    parsed = json.loads(raw[start : end + 1])
    return {
        "summary": str(parsed.get("summary", "")).strip(),
        "project_suggestions": [str(item).strip() for item in parsed.get("project_suggestions", []) if str(item).strip()],
        "resume_bullet_drafts": [str(item).strip() for item in parsed.get("resume_bullet_drafts", []) if str(item).strip()],
    }


def safe_resume_bullets(result: DeterministicResult, bullets: list[str]) -> list[str]:
    matched_terms = {skill.lower() for skill in result.matched_skills}
    missing_terms = {skill.lower() for skill in result.missing_skills}
    unsupported_skill_terms = {skill.lower() for skill in SKILL_ALIASES if skill not in result.resume_skills}
    evidence_terms = {
        token.lower()
        for evidence in result.matched_project_evidence
        for token in evidence.replace(",", " ").replace(".", " ").split()
        if len(token) > 2
    }
    allowed_terms = matched_terms.union(evidence_terms)

    safe: list[str] = []
    for bullet in bullets:
        lower = bullet.lower()
        if any(term and term in lower for term in missing_terms):
            continue
        if any(term and term in lower for term in unsupported_skill_terms):
            continue
        if allowed_terms and not any(term and term in lower for term in allowed_terms):
            continue
        safe.append(bullet)

    return safe or build_resume_bullets(result)
