from app.services.goals import build_growth_goals
from app.services.matching import analyze_resume_against_job, extract_skills, infer_role_title


def test_extract_skills_detects_aliases():
    skills = extract_skills("Built RESTful APIs with Python, FastAPI, SQLite, and pytest.")

    assert "Python" in skills
    assert "FastAPI" in skills
    assert "SQLite" in skills
    assert "REST APIs" in skills
    assert "pytest" in skills


def test_analysis_finds_matches_and_missing_skills():
    resume = "Built a FastAPI API with SQLite, SQLAlchemy, pytest, and Git."
    job = """
    Required qualifications:
    - Build backend services using Python, FastAPI, SQL, Docker, and Git.
    Preferred qualifications:
    - Experience with LLM tools.
    """

    result = analyze_resume_against_job(resume, job)

    assert result.fit_score > 0
    assert "FastAPI" in result.matched_skills
    assert "Docker" in result.missing_skills
    assert result.recommended_improvement_areas


def test_growth_goals_are_english_and_complete():
    result = analyze_resume_against_job("Python FastAPI project", "Required: Python FastAPI SQL Docker")
    goals = build_growth_goals(result)

    assert set(goals) == {"2-week", "1-month", "3-month"}
    assert all(goals[horizon] for horizon in goals)
    assert "Ship" in " ".join(goals["1-month"])


def test_keyword_overlap_changes_score_when_no_known_skill_matches():
    weak = analyze_resume_against_job(
        "Retail cashier with scheduling and customer service experience.",
        "Marketing coordinator role focused on campaign planning, social media, content calendars, and analytics reporting.",
    )
    stronger = analyze_resume_against_job(
        "Marketing assistant who planned social media campaigns, maintained content calendars, and reported campaign analytics.",
        "Marketing coordinator role focused on campaign planning, social media, content calendars, and analytics reporting.",
    )

    assert stronger.fit_score > weak.fit_score
    assert "campaign" in stronger.matched_keywords


def test_short_software_engineer_title_uses_role_template():
    resume = """
    Computer Science student with Python, Java, SQL, Git, Docker, Kubernetes,
    AWS, Google Cloud, CI/CD, JavaScript, Node.js, MySQL, PostgreSQL,
    TensorFlow, and PyTorch experience.
    """

    result = analyze_resume_against_job(resume, "soft engineer")

    assert result.fit_score > 50
    assert "Python" in result.matched_skills
    assert "Git" in result.matched_skills
    assert "soft" not in result.missing_skills
    assert "engineer" not in result.missing_skills


def test_explicit_job_skills_take_priority_over_role_template():
    result = analyze_resume_against_job(
        "Built a Python FastAPI backend with SQL, Git, and pytest.",
        "Software engineer role requiring Python, REST APIs, SQL, Git, and testing.",
    )

    assert "Java" not in result.job_required_skills


def test_backend_software_engineer_title_uses_backend_template():
    resume = """
    Computer Science student with C++, Python, Java, JavaScript, SQL, C#, TypeScript,
    Git, Docker, Kubernetes, Node.js, MySQL, PostgreSQL, AWS, Google Cloud, CI/CD,
    TensorFlow, and PyTorch experience.
    """

    result = analyze_resume_against_job(resume, "Backend Software Engineer")

    assert infer_role_title("Backend Software Engineer") == "Backend Software Engineer"
    assert result.fit_score > 50
    assert "Python" in result.matched_skills
    assert "Java" in result.matched_skills
    assert "SQL" in result.matched_skills
    assert "Docker" in result.matched_skills
    assert "Backend Development" not in result.missing_skills


def test_role_labels_are_not_counted_as_hard_skill_gaps_in_long_jd():
    result = analyze_resume_against_job(
        "Python FastAPI SQL Git Docker",
        "We are hiring a Backend Software Engineer. Build APIs using Python and SQL.",
    )

    assert "Backend Development" not in result.missing_skills


def test_skill_list_without_project_evidence_does_not_produce_false_perfect_fit():
    result = analyze_resume_against_job(
        "Python Machine Learning TensorFlow PyTorch SQL Git Docker AWS GCP Kubernetes CI/CD",
        "Machine Learning Engineer",
    )

    assert result.evidence_coverage == 0.0
    assert result.fit_score < 100.0
    assert result.fit_score <= 80.0


def test_project_evidence_improves_fit_score_for_same_skills():
    skills_only = analyze_resume_against_job(
        "Python Machine Learning TensorFlow PyTorch SQL Git Docker",
        "Machine Learning Engineer",
    )
    with_evidence = analyze_resume_against_job(
        "Python Machine Learning TensorFlow PyTorch SQL Git Docker. Built and deployed a PyTorch machine learning model with Docker.",
        "Machine Learning Engineer",
    )

    assert with_evidence.evidence_coverage > skills_only.evidence_coverage
    assert with_evidence.fit_score > skills_only.fit_score
