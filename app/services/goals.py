from app.services.matching import DeterministicResult


def build_growth_goals(result: DeterministicResult) -> dict[str, list[str]]:
    missing = result.missing_skills[:5]
    evidence_gap = result.recommended_improvement_areas[:3]

    two_week = [
        "Select one target job description and convert its required skills into a project evidence checklist.",
        "Rewrite the strongest existing project bullets so each bullet includes an action, technical method, and measurable outcome.",
    ]
    one_month = [
        "Build or extend one backend project feature that demonstrates the highest-priority missing skill.",
        "Add tests and a short README section that proves the feature can be run from a clean checkout.",
    ]
    three_month = [
        "Complete a portfolio-ready project iteration with a documented architecture, API examples, and test coverage.",
        "Prepare interview talking points that connect project decisions to the target role requirements.",
    ]

    if missing:
        two_week.append(f"Create a focused learning plan for {', '.join(missing[:3])}.")
        one_month.append(f"Ship a small but verifiable feature using {missing[0]}.")
    if evidence_gap:
        three_month.append("Turn the most important evidence gaps into finished, resume-safe project bullets.")

    return {
        "2-week": two_week,
        "1-month": one_month,
        "3-month": three_month,
    }


def build_fallback_summary(result: DeterministicResult) -> str:
    if result.matched_skills:
        matched = ", ".join(result.matched_skills[:5])
        opening = f"The resume shows relevant evidence for {matched}."
    else:
        opening = "The resume has limited direct evidence for the target role's technical requirements."

    if result.missing_skills:
        missing = ", ".join(result.missing_skills[:5])
        return f"{opening} The highest-priority gaps are {missing}. Add credible project evidence before using these skills in resume bullets."

    return f"{opening} The next improvement should be stronger quantified impact and clearer project evidence."


def build_resume_bullets(result: DeterministicResult) -> list[str]:
    bullets = []
    if "FastAPI" in result.matched_skills or "REST APIs" in result.matched_skills:
        bullets.append("Built backend API workflows with structured request handling, persistence, and testable endpoints.")
    if "SQL" in result.matched_skills or "SQLite" in result.matched_skills:
        bullets.append("Implemented database-backed features with clear data models and repeatable local setup.")
    if "LLM" in result.matched_skills:
        bullets.append("Integrated local AI assistance while preserving deterministic fallback behavior for core analysis.")
    if not bullets:
        bullets.append("Developed project features aligned with target role requirements and documented the implementation for review.")
    return bullets

