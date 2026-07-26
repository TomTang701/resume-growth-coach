import codecs
import json

from app.services.portfolio_planner import EvidenceChecklist, build_portfolio_plan, load_recorded_evidence


def test_recorded_evidence_accepts_windows_powershell_utf8_bom(tmp_path, monkeypatch):
    evidence_path = tmp_path / "verification-evidence.json"
    evidence_path.write_bytes(
        codecs.BOM_UTF8
        + json.dumps(
            {
                "tests_passed": True,
                "docker_smoke_passed": True,
                "ci_passed": True,
                "documentation_complete": True,
                "sanitized_demo_verified": True,
            }
        ).encode("utf-8")
    )
    monkeypatch.setenv("RGC_EVIDENCE_PATH", str(evidence_path))

    assert load_recorded_evidence().resume_eligible is True


def test_planner_ranks_team_workflow_for_uncovered_full_stack_gaps():
    plan = build_portfolio_plan(
        missing_skills=["PostgreSQL", "Docker", "React", "CI/CD"],
        existing_project_names=["Resume Growth Coach", "Amazon Clone"],
        evidence_by_project={},
    )

    assert plan[0].slug == "team-job-workflow"
    assert "PostgreSQL" in plan[0].gap_coverage
    assert plan[0].resume_eligible is False
    assert plan[0].english_resume_bullet_draft is None


def test_planner_excludes_existing_project_and_releases_bullet_only_after_evidence():
    plan = build_portfolio_plan(
        missing_skills=["Docker", "PostgreSQL", "CI/CD"],
        existing_project_names=["Resume Growth Coach"],
        evidence_by_project={
            "team-job-workflow": EvidenceChecklist(
                tests_passed=True,
                docker_smoke_passed=True,
                ci_passed=True,
                documentation_complete=True,
                sanitized_demo_verified=True,
            )
        },
    )

    assert all(item.slug != "resume-growth-coach-upgrade" for item in plan)
    assert plan[0].resume_eligible is True
    assert plan[0].english_resume_bullet_draft
