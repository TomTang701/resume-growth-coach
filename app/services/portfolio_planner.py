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


def load_recorded_evidence() -> EvidenceChecklist:
    default_path = Path(__file__).resolve().parents[2] / "local_data" / "verification-evidence.json"
    evidence_path = Path(os.getenv("RGC_EVIDENCE_PATH", str(default_path)))
    try:
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return EvidenceChecklist()
    return EvidenceChecklist(**{field: payload.get(field) is True for field in EVIDENCE_FIELDS})


@dataclass(frozen=True)
class PortfolioProposal:
    slug: str
    name: str
    summary: str
    gap_coverage: list[str]
    acceptance_criteria: list[str]
    resume_eligible: bool
    english_resume_bullet_draft: str | None


PROJECT_CATALOG = (
    {
        "slug": "resume-growth-coach-upgrade",
        "name": "Resume Growth Coach Upgrade",
        "existing_name": "Resume Growth Coach",
        "keywords": ("PostgreSQL", "Docker", "CI/CD", "Database Design"),
        "summary": "Upgrade the local-first analysis service with reproducible database, container, and CI evidence.",
        "bullet": "Hardened a local-first FastAPI analysis service with PostgreSQL, Docker Compose, and automated CI validation.",
    },
    {
        "slug": "team-job-workflow",
        "name": "Team Job Workflow",
        "existing_name": "Team Job Workflow",
        "keywords": ("PostgreSQL", "Docker", "React", "CI/CD", "REST APIs", "Testing"),
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
    evidence: EvidenceChecklist,
) -> list[PortfolioProposal]:
    normalized_existing = {name.casefold() for name in existing_project_names}
    missing = set(missing_skills)
    proposals: list[PortfolioProposal] = []
    for project in PROJECT_CATALOG:
        if project["existing_name"].casefold() in normalized_existing:
            continue
        coverage = [skill for skill in project["keywords"] if skill in missing]
        if not coverage:
            continue
        eligible = evidence.resume_eligible
        proposals.append(
            PortfolioProposal(
                slug=project["slug"],
                name=project["name"],
                summary=project["summary"],
                gap_coverage=coverage,
                acceptance_criteria=ACCEPTANCE_CRITERIA,
                resume_eligible=eligible,
                english_resume_bullet_draft=project["bullet"] if eligible else None,
            )
        )
    return sorted(proposals, key=lambda proposal: (-len(proposal.gap_coverage), proposal.name))
