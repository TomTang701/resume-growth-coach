JOB_DESCRIPTION_TEMPLATES: dict[str, str] = {
    "backend_full_stack_intern": """Backend / Full-stack Internship
Required qualifications:
- Build REST APIs with Python and FastAPI.
- Design relational data models with PostgreSQL and SQL.
- Collaborate on React user interfaces and API integrations.
- Write automated tests and maintain CI/CD workflows.
- Package local services with Docker.
""",
    "ai_application_intern": """AI Application Internship
Required qualifications:
- Build reliable Python services that integrate local or hosted LLM workflows.
- Parse documents and present explainable results through REST APIs.
- Store analysis history with PostgreSQL and SQLAlchemy.
- Write automated tests and package services with Docker.
""",
}

TEMPLATE_TITLES = {
    "backend_full_stack_intern": "Backend / Full-stack Internship",
    "ai_application_intern": "AI Application Internship",
}


def list_job_templates() -> list[dict[str, str]]:
    return [{"slug": slug, "title": TEMPLATE_TITLES[slug]} for slug in JOB_DESCRIPTION_TEMPLATES]


def get_job_template(slug: str) -> str:
    return JOB_DESCRIPTION_TEMPLATES[slug]
