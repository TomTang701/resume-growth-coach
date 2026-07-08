from app.services.job_recommendations import recommend_matching_jobs


def test_recommend_matching_jobs_returns_top_three():
    resume = """
    Computer science student with Python, Java, SQL, Git, Docker, Kubernetes,
    AWS, Google Cloud, CI/CD, JavaScript, Node.js, MySQL, PostgreSQL,
    TensorFlow, and PyTorch experience.
    """

    jobs = recommend_matching_jobs(resume)

    assert len(jobs) == 3
    assert jobs[0]["fit_score"] >= jobs[1]["fit_score"] >= jobs[2]["fit_score"]
    assert all(job["title"] for job in jobs)
    assert all(job["reason"] for job in jobs)


def test_backend_resume_prefers_backend_or_software_roles():
    resume = "Built Python FastAPI REST APIs with SQL, Git, pytest, Docker, and database models."

    jobs = recommend_matching_jobs(resume)

    assert jobs[0]["title"] in {"Backend Software Engineer", "Software Engineer"}


def test_recommendations_exclude_current_target_role():
    resume = "Python Java SQL Git computer science student with machine learning and cloud skills."

    jobs = recommend_matching_jobs(resume, current_job_text="Software Engineer")

    assert all(job["title"] != "Software Engineer" for job in jobs)
    assert len(jobs) == 3
