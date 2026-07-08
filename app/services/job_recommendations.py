from app.services.matching import analyze_resume_against_job, infer_role_title


JOB_PROFILES: tuple[dict[str, str], ...] = (
    {
        "title": "Backend Software Engineer",
        "description": (
            "Backend software engineer role requiring Python, FastAPI, Java, SQL, REST APIs, Git, "
            "testing, Docker, and database design. Responsibilities include building API "
            "services, maintaining data models, and improving backend reliability."
        ),
    },
    {
        "title": "Software Engineer",
        "description": (
            "Software engineer role requiring Python, Java, SQL, Git, testing, REST APIs, "
            "data structures, algorithms, and clear project documentation."
        ),
    },
    {
        "title": "Full Stack Developer",
        "description": (
            "Full stack developer role requiring JavaScript, React, Node.js, SQL, REST APIs, "
            "HTML, CSS, Git, and testing across frontend and backend workflows."
        ),
    },
    {
        "title": "Machine Learning Engineer",
        "description": (
            "Machine learning engineer role requiring Python, machine learning, PyTorch, "
            "TensorFlow, SQL, Git, Docker, and experience turning models into usable systems."
        ),
    },
    {
        "title": "Cloud or DevOps Engineer",
        "description": (
            "Cloud engineer role requiring AWS, Google Cloud, Docker, Kubernetes, CI/CD, "
            "Linux, Git, scripting, and service reliability practices."
        ),
    },
    {
        "title": "Data Analyst",
        "description": (
            "Data analyst role requiring SQL, Python, data analysis, Excel, dashboards, "
            "analytics reporting, and clear communication of data-driven insights."
        ),
    },
)


def recommend_matching_jobs(resume_text: str, current_job_text: str = "", limit: int = 3) -> list[dict]:
    current_title = infer_role_title(current_job_text)
    scored: list[dict] = []
    for profile in JOB_PROFILES:
        if current_title and normalize_title(profile["title"]) == normalize_title(current_title):
            continue
        result = analyze_resume_against_job(resume_text, profile["description"])
        scored.append(
            {
                "title": profile["title"],
                "fit_score": result.fit_score,
                "matched_skills": result.matched_skills[:6],
                "missing_skills": result.missing_skills[:4],
                "reason": build_reason(profile["title"], result.matched_skills, result.missing_skills),
            }
        )

    return sorted(scored, key=lambda item: item["fit_score"], reverse=True)[:limit]


def build_reason(title: str, matched_skills: list[str], missing_skills: list[str]) -> str:
    if matched_skills:
        matched = ", ".join(matched_skills[:4])
        reason = f"{title} is a strong adjacent target because the resume already shows {matched}."
    else:
        reason = f"{title} may be worth exploring, but the resume needs more direct role evidence."

    if missing_skills:
        reason += f" The main gaps to close are {', '.join(missing_skills[:3])}."
    return reason


def normalize_title(title: str) -> str:
    return "".join(char.lower() for char in title if char.isalnum())
