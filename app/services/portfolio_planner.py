import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvidenceChecklist:
    tests_passed: bool = False
    docker_smoke_passed: bool = False
    ci_passed: bool = False
    documentation_complete: bool = False
    sanitized_demo_verified: bool = False

    @property
    def resume_eligible(self) -> bool:
        return all(
            (
                self.tests_passed,
                self.docker_smoke_passed,
                self.ci_passed,
                self.documentation_complete,
                self.sanitized_demo_verified,
            )
        )


EVIDENCE_FIELDS = (
    "tests_passed",
    "docker_smoke_passed",
    "ci_passed",
    "documentation_complete",
    "sanitized_demo_verified",
)
RGC_PROJECT_SLUG = "resume-growth-coach-upgrade"
TEAM_PROJECT_SLUG = "team-job-workflow"
TEAM_TEST_EVIDENCE_FIELDS = (
    "backend_tests_passed",
    "frontend_tests_and_build_passed",
    "browser_ui_smoke_passed",
)


def load_evidence(
    evidence_path: Path,
    test_evidence_fields: tuple[str, ...] = ("tests_passed",),
) -> EvidenceChecklist:
    try:
        payload = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return EvidenceChecklist()
    return EvidenceChecklist(
        tests_passed=all(payload.get(field) is True for field in test_evidence_fields),
        **{field: payload.get(field) is True for field in EVIDENCE_FIELDS if field != "tests_passed"},
    )


def load_recorded_evidence() -> EvidenceChecklist:
    default_path = Path(__file__).resolve().parents[2] / "local_data" / "verification-evidence.json"
    evidence_path = Path(os.getenv("RGC_EVIDENCE_PATH", str(default_path)))
    return load_evidence(evidence_path)


def load_project_evidence() -> dict[str, EvidenceChecklist]:
    team_evidence_path = os.getenv("TJW_EVIDENCE_PATH")
    return {
        RGC_PROJECT_SLUG: load_recorded_evidence(),
        TEAM_PROJECT_SLUG: (
            load_evidence(Path(team_evidence_path), test_evidence_fields=TEAM_TEST_EVIDENCE_FIELDS)
            if team_evidence_path
            else EvidenceChecklist()
        ),
    }


@dataclass(frozen=True)
class PortfolioProposal:
    slug: str
    name: str
    summary: str
    gap_coverage: list[str]
    differentiation_opportunities: list[str]
    estimated_completion_cost: str
    acceptance_criteria: list[str]
    resume_eligible: bool
    english_resume_bullet_draft: str | None


PROJECT_CATALOG = (
    {
        "slug": RGC_PROJECT_SLUG,
        "name": "Resume Growth Coach Upgrade",
        "existing_name": "Resume Growth Coach",
        "keywords": ("PostgreSQL", "Docker", "CI/CD", "Database Design"),
        "differentiation_signals": ("LLM", "Ollama", "Document Parsing"),
        "completion_cost": 3,
        "completion_cost_label": "medium",
        "summary": "Upgrade the local-first analysis service with reproducible database, container, and CI evidence.",
        "bullet": "Hardened a local-first FastAPI analysis service with PostgreSQL, Docker Compose, and automated CI validation.",
    },
    {
        "slug": TEAM_PROJECT_SLUG,
        "name": "Team Job Workflow",
        "existing_name": "Team Job Workflow",
        "keywords": ("PostgreSQL", "Docker", "React", "CI/CD", "REST APIs", "Testing"),
        "differentiation_signals": ("React", "JWT", "role-based access control", "activity audit"),
        "completion_cost": 5,
        "completion_cost_label": "high",
        "summary": "Build a role-aware team application workflow with a React client and FastAPI API.",
        "bullet": "Built a full-stack team job workflow with React, FastAPI, PostgreSQL, JWT role controls, Docker Compose, and automated tests.",
    },
)

ACCEPTANCE_CRITERIA = [
    "Targeted unit and API tests pass.",
    "Docker Compose smoke test passes.",
    "Continuous integration workflow passes.",
    "README documents a clean local setup.",
    "Demo data is sanitized and contains no real applicant data.",
]


def build_portfolio_plan(
    missing_skills: list[str],
    existing_project_names: list[str],
    evidence_by_project: dict[str, EvidenceChecklist],
    existing_project_evidence: list[str] | None = None,
) -> list[PortfolioProposal]:
    normalized_existing = {name.strip().casefold() for name in existing_project_names}
    missing = set(missing_skills)
    evidence_text = " ".join(existing_project_evidence or []).casefold()
    proposals: list[PortfolioProposal] = []
    for project in PROJECT_CATALOG:
        if project["existing_name"].casefold() in normalized_existing:
            continue
        coverage = [skill for skill in project["keywords"] if skill in missing]
        if not coverage:
            continue
        differentiation_opportunities = [
            signal for signal in project["differentiation_signals"] if signal.casefold() not in evidence_text
        ]
        eligible = evidence_by_project.get(project["slug"], EvidenceChecklist()).resume_eligible
        proposals.append(
            PortfolioProposal(
                slug=project["slug"],
                name=project["name"],
                summary=project["summary"],
                gap_coverage=coverage,
                differentiation_opportunities=differentiation_opportunities,
                estimated_completion_cost=project["completion_cost_label"],
                acceptance_criteria=ACCEPTANCE_CRITERIA,
                resume_eligible=eligible,
                english_resume_bullet_draft=project["bullet"] if eligible else None,
            )
        )
    completion_costs = {project["slug"]: project["completion_cost"] for project in PROJECT_CATALOG}
    return sorted(
        proposals,
        key=lambda proposal: (
            -len(proposal.gap_coverage),
            -len(proposal.differentiation_opportunities),
            completion_costs[proposal.slug],
            proposal.name,
        ),
    )
