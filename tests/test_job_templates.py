from app.services.job_templates import JOB_DESCRIPTION_TEMPLATES, list_job_templates


def test_builtin_backend_template_contains_required_engineering_signals():
    template = JOB_DESCRIPTION_TEMPLATES["backend_full_stack_intern"]

    assert "PostgreSQL" in template
    assert "Docker" in template
    assert "React" in template


def test_template_list_exposes_stable_slug_and_title():
    templates = list_job_templates()

    assert {item["slug"] for item in templates} >= {"backend_full_stack_intern", "ai_application_intern"}
    assert all(item["title"] for item in templates)
