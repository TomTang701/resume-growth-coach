import codecs
import json
from pathlib import Path

from app.services import portfolio_planner
from app.services.portfolio_planner import EvidenceChecklist, build_portfolio_plan, current_git_commit, load_recorded_evidence


def current_project_commit() -> str:
    commit = current_git_commit(Path(__file__).resolve().parents[1])
    assert commit is not None
    return commit


def test_recorded_evidence_accepts_windows_powershell_utf8_bom(tmp_path, monkeypatch):
    monkeypatch.setattr(portfolio_planner, "git_worktree_is_clean", lambda _: True)
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
                "verified_commit": current_project_commit(),
            }
        ).encode("utf-8")
    )
    monkeypatch.setenv("RGC_EVIDENCE_PATH", str(evidence_path))

    assert load_recorded_evidence().resume_eligible is True


def test_recorded_evidence_rejects_an_outdated_git_commit(tmp_path, monkeypatch):
    evidence_path = tmp_path / "verification-evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "tests_passed": True,
                "docker_smoke_passed": True,
                "ci_passed": True,
                "documentation_complete": True,
                "sanitized_demo_verified": True,
                "verified_commit": "outdated-commit",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("RGC_EVIDENCE_PATH", str(evidence_path))

    assert load_recorded_evidence().resume_eligible is False


def test_recorded_evidence_rejects_a_modified_worktree(tmp_path, monkeypatch):
    evidence_path = tmp_path / "verification-evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "tests_passed": True,
                "docker_smoke_passed": True,
                "ci_passed": True,
                "documentation_complete": True,
                "sanitized_demo_verified": True,
                "verified_commit": current_project_commit(),
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("RGC_EVIDENCE_PATH", str(evidence_path))
    monkeypatch.setattr(portfolio_planner, "git_worktree_is_clean", lambda _: False, raising=False)

    assert load_recorded_evidence().resume_eligible is False


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


def test_planner_excludes_existing_project_when_name_has_surrounding_whitespace():
    plan = build_portfolio_plan(
        missing_skills=["PostgreSQL", "Docker", "React", "CI/CD"],
        existing_project_names=["  Team Job Workflow  "],
        evidence_by_project={},
    )

    assert all(item.slug != "team-job-workflow" for item in plan)
