import json
import http.client
import os
import re
import urllib.error
import urllib.request

from app.services.goals import build_fallback_summary, build_resume_bullets
from app.services.matching import SKILL_ALIASES, DeterministicResult, alias_present, normalize_for_matching


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:3b"


def get_ollama_timeout_seconds() -> float:
    try:
        configured = float(os.getenv("RGC_OLLAMA_TIMEOUT_SECONDS", "60"))
    except ValueError:
        return 60.0
    return max(1.0, min(configured, 300.0))


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
        with urllib.request.urlopen(request, timeout=get_ollama_timeout_seconds()) as response:
            body = json.loads(response.read().decode("utf-8"))
        if not isinstance(body, dict):
            raise ValueError("Ollama response body was not an object.")
        parsed = parse_json_response(body.get("response", ""))
        if not parsed["summary"]:
            raise ValueError("Ollama response did not include a summary.")
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
    if not isinstance(parsed, dict):
        raise ValueError("Ollama response JSON was not an object.")
    normalized = {
        "summary": parsed.get("summary", "").strip() if isinstance(parsed.get("summary"), str) else "",
        "project_suggestions": normalize_string_list(parsed.get("project_suggestions")),
        "resume_bullet_drafts": normalize_string_list(parsed.get("resume_bullet_drafts")),
    }
    if any(contains_cjk(value) for value in [normalized["summary"], *normalized["project_suggestions"], *normalized["resume_bullet_drafts"]]):
        raise ValueError("Ollama response contained non-English user-facing text.")
    return normalized


def contains_cjk(value: str) -> bool:
    return re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", value) is not None


def normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def safe_resume_bullets(result: DeterministicResult, bullets: list[str]) -> list[str]:
    matched_terms = {skill.lower() for skill in result.matched_skills}
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
        if any(bullet_mentions_skill(bullet, skill) for skill in result.missing_skills):
            continue
        if any(bullet_mentions_skill(bullet, skill) for skill in SKILL_ALIASES if skill not in result.resume_skills):
            continue
        if allowed_terms and not any(term and term in lower for term in allowed_terms):
            continue
        safe.append(bullet)

    return safe or build_resume_bullets(result)


def bullet_mentions_skill(bullet: str, skill: str) -> bool:
    normalized = normalize_for_matching(bullet)
    return any(alias_present(normalized, alias) for alias in SKILL_ALIASES.get(skill, (skill,)))
