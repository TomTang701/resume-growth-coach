import re
from dataclasses import dataclass


SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "Python": ("python",),
    "Java": ("java",),
    "C++": ("c++", "cpp"),
    "C#": ("c#", "c sharp"),
    "Go": ("golang", "go language"),
    "FastAPI": ("fastapi",),
    "Flask": ("flask",),
    "Django": ("django",),
    "Spring Boot": ("spring boot", "springboot"),
    "SQL": ("sql", "sqlite", "postgres", "mysql"),
    "SQLite": ("sqlite",),
    "PostgreSQL": ("postgresql", "postgres"),
    "MySQL": ("mysql",),
    "SQLAlchemy": ("sqlalchemy",),
    "MongoDB": ("mongodb", "mongo"),
    "Redis": ("redis",),
    "REST APIs": ("rest api", "restful", "api endpoint", "apis"),
    "pytest": ("pytest", "unit test", "testclient"),
    "Git": ("git", "github"),
    "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s"),
    "Linux": ("linux", "ubuntu", "shell scripting"),
    "CI/CD": ("ci/cd", "github actions", "continuous integration"),
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure",),
    "GCP": ("gcp", "google cloud"),
    "React": ("react", "redux"),
    "Vue": ("vue", "vue.js"),
    "Angular": ("angular",),
    "JavaScript": ("javascript", "typescript", "node.js", "nodejs"),
    "Node.js": ("node.js", "nodejs", "express"),
    "HTML/CSS": ("html", "css", "tailwind"),
    "Machine Learning": ("machine learning", "ml", "scikit", "pytorch", "tensorflow"),
    "LLM": ("llm", "large language model", "ollama", "openai", "prompt"),
    "Document Parsing": ("pdf", "parsing", "pdfplumber", "document extraction"),
    "Data Analysis": ("pandas", "numpy", "analytics", "dashboard"),
    "Excel": ("excel", "spreadsheet", "vlookup", "pivot table"),
    "Power BI": ("power bi",),
    "Tableau": ("tableau",),
    "Agile": ("agile", "scrum"),
    "Backend Development": ("backend", "back end", "server-side", "后端"),
    "Frontend Development": ("frontend", "front end", "前端"),
    "Database Design": ("database", "data model", "数据库"),
    "Testing": ("testing", "test automation", "pytest", "unit test", "junit", "测试"),
    "Data Analysis": ("pandas", "numpy", "analytics", "dashboard", "数据分析"),
    "Machine Learning": ("machine learning", "ml", "scikit", "pytorch", "tensorflow", "机器学习"),
}

ROLE_SKILL_TEMPLATES: dict[str, tuple[str, ...]] = {
    "software_engineer": ("Python", "Java", "SQL", "Git", "Testing", "REST APIs"),
    "backend_engineer": ("Python", "Java", "SQL", "Git", "Testing", "REST APIs", "Docker"),
    "frontend_engineer": ("JavaScript", "React", "HTML/CSS", "Git", "Testing"),
    "full_stack_engineer": ("Python", "JavaScript", "SQL", "REST APIs", "React", "Git", "Testing"),
    "data_analyst": ("SQL", "Python", "Data Analysis", "Excel", "Power BI", "Tableau"),
    "machine_learning_engineer": ("Python", "Machine Learning", "SQL", "Git", "Docker"),
    "cloud_devops_engineer": ("AWS", "GCP", "Docker", "Kubernetes", "CI/CD", "Linux", "Git"),
}

REQUIRED_MARKERS = ("required", "must have", "minimum qualifications", "basic qualifications")
PREFERRED_MARKERS = ("preferred", "nice to have", "bonus", "plus")
ROLE_LABEL_SKILLS = {"Backend Development", "Frontend Development"}
STOPWORDS = {
    "and",
    "are",
    "can",
    "for",
    "from",
    "have",
    "into",
    "our",
    "that",
    "the",
    "this",
    "with",
    "you",
    "your",
    "will",
    "work",
    "working",
    "team",
    "role",
    "job",
    "soft",
    "software",
    "engineer",
    "developer",
    "description",
    "required",
    "preferred",
    "qualifications",
    "responsibilities",
    "experience",
    "skills",
    "using",
    "ability",
    "strong",
    "knowledge",
    "including",
    "such",
    "within",
    "across",
    "plus",
    "nice",
    "must",
    "build",
    "develop",
    "design",
    "implement",
}


@dataclass
class DeterministicResult:
    fit_score: float
    evidence_coverage: float
    resume_skills: list[str]
    job_required_skills: list[str]
    job_preferred_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    matched_project_evidence: list[str]
    education_signals: list[str]
    job_responsibilities: list[str]
    recommended_improvement_areas: list[str]

    def to_dict(self) -> dict:
        return {
            "fit_score": self.fit_score,
            "evidence_coverage": self.evidence_coverage,
            "resume_skills": self.resume_skills,
            "job_required_skills": self.job_required_skills,
            "job_preferred_skills": self.job_preferred_skills,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "matched_project_evidence": self.matched_project_evidence,
            "education_signals": self.education_signals,
            "job_responsibilities": self.job_responsibilities,
            "recommended_improvement_areas": self.recommended_improvement_areas,
        }


def analyze_resume_against_job(resume_text: str, job_text: str) -> DeterministicResult:
    resume_skills = extract_skills(resume_text)
    role_skills = infer_role_skills(job_text)
    explicit_job_skills = [skill for skill in extract_skills(job_text) if skill not in ROLE_LABEL_SKILLS]
    use_role_template = should_use_role_template(job_text, role_skills)
    job_skills = role_skills if use_role_template else explicit_job_skills or role_skills
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_text)
    contextual_required = extract_contextual_skills(job_text, REQUIRED_MARKERS)
    if contextual_required:
        required_skills = contextual_required
    elif use_role_template:
        required_skills = role_skills
    else:
        required_skills = explicit_job_skills or role_skills or fallback_required_keywords(job_keywords)
    preferred_skills = [skill for skill in extract_contextual_skills(job_text, PREFERRED_MARKERS) if skill not in required_skills]
    matched = sorted(set(resume_skills).intersection(job_skills))
    missing = sorted(set(required_skills).difference(resume_skills))
    matched_keywords = sorted(set(job_keywords).intersection(resume_keywords).union(matched))
    missing_keywords = sorted(set(job_keywords).difference(resume_keywords).difference(matched))
    evidence = extract_project_evidence(resume_text, matched)
    responsibilities = extract_responsibilities(job_text)
    education = extract_education_signals(resume_text)
    evidence_coverage = calculate_evidence_coverage(matched, evidence)
    score = calculate_fit_score(
        matched,
        missing,
        preferred_skills,
        resume_text,
        evidence,
        matched_keywords,
        job_keywords,
        evidence_coverage,
    )
    improvements = build_improvement_areas(missing, responsibilities)

    return DeterministicResult(
        fit_score=score,
        evidence_coverage=evidence_coverage,
        resume_skills=resume_skills,
        job_required_skills=required_skills,
        job_preferred_skills=preferred_skills,
        matched_skills=matched,
        missing_skills=missing,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        matched_project_evidence=evidence,
        education_signals=education,
        job_responsibilities=responsibilities,
        recommended_improvement_areas=improvements,
    )


def extract_skills(text: str) -> list[str]:
    lower = normalize_for_matching(text)
    found = []
    for skill, aliases in SKILL_ALIASES.items():
        if any(alias_present(lower, alias) for alias in aliases):
            found.append(skill)
    return sorted(found)


def infer_role_skills(job_text: str) -> list[str]:
    role = infer_role_key(job_text)
    if role:
        return sorted(ROLE_SKILL_TEMPLATES[role])
    return []


def infer_role_title(job_text: str) -> str:
    role = infer_role_key(job_text)
    role_titles = {
        "machine_learning_engineer": "Machine Learning Engineer",
        "cloud_devops_engineer": "Cloud or DevOps Engineer",
        "backend_engineer": "Backend Software Engineer",
        "frontend_engineer": "Frontend Developer",
        "full_stack_engineer": "Full Stack Developer",
        "data_analyst": "Data Analyst",
        "software_engineer": "Software Engineer",
    }
    return role_titles.get(role, "")


def infer_role_key(job_text: str) -> str:
    normalized = normalize_for_matching(job_text)
    role_patterns: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("machine_learning_engineer", ("machine learning engineer", "ml engineer", "ai engineer")),
        ("cloud_devops_engineer", ("cloud or devops engineer", "cloud engineer", "devops engineer")),
        ("backend_engineer", ("backend software engineer", "backend engineer", "back end engineer", "backend developer")),
        ("frontend_engineer", ("frontend engineer", "front end engineer", "frontend developer")),
        ("full_stack_engineer", ("full stack engineer", "fullstack engineer", "full stack developer")),
        ("data_analyst", ("data analyst", "business analyst", "analytics analyst")),
        ("software_engineer", ("software engineer", "soft engineer", "swe", "software developer")),
    )
    for role, patterns in role_patterns:
        if any(pattern in normalized for pattern in patterns):
            return role
    return ""


def should_use_role_template(job_text: str, role_skills: list[str]) -> bool:
    if not role_skills:
        return False
    words = re.findall(r"[a-zA-Z+#.]+", job_text)
    has_requirement_markers = any(marker in job_text.lower() for marker in REQUIRED_MARKERS + PREFERRED_MARKERS)
    return len(words) <= 6 and not has_requirement_markers


def alias_present(normalized_text: str, alias: str) -> bool:
    normalized_alias = normalize_for_matching(alias)
    if contains_cjk(normalized_alias):
        return normalized_alias in normalized_text
    if re.fullmatch(r"[a-z0-9]+", normalized_alias):
        return re.search(rf"(?<![a-z0-9]){re.escape(normalized_alias)}(?![a-z0-9])", normalized_text) is not None
    return normalized_alias in normalized_text


def extract_contextual_skills(text: str, markers: tuple[str, ...]) -> list[str]:
    lower_lines = text.lower().splitlines()
    selected: list[str] = []
    for index, line in enumerate(lower_lines):
        if any(marker in line for marker in markers):
            window_lines = [line]
            for next_line in lower_lines[index + 1 : index + 8]:
                if any(marker in next_line for marker in REQUIRED_MARKERS + PREFERRED_MARKERS):
                    break
                window_lines.append(next_line)
            window = "\n".join(window_lines)
            selected.extend(extract_skills(window))
    return sorted(set(selected))


def extract_project_evidence(resume_text: str, matched_skills: list[str]) -> list[str]:
    evidence: list[str] = []
    lines = [line.strip(" -\t") for line in resume_text.splitlines() if line.strip()]
    for line in lines:
        normalized = normalize_for_matching(line)
        if any(any(alias_present(normalized, alias) for alias in SKILL_ALIASES[skill]) for skill in matched_skills):
            if has_project_signal(line):
                evidence.append(line)
        if len(evidence) >= 8:
            break
    return evidence


def has_project_signal(line: str) -> bool:
    lower = line.lower()
    return any(token in lower for token in ("built", "implemented", "developed", "created", "project", "api", "database"))


def extract_education_signals(text: str) -> list[str]:
    signals = []
    lower = text.lower()
    patterns = {
        "Computer Science": ("computer science", "cs ", "software engineering"),
        "Graduate Coursework": ("omscs", "master", "graduate"),
        "Data Coursework": ("data structures", "algorithms", "database", "machine learning"),
    }
    for label, aliases in patterns.items():
        if any(alias in lower for alias in aliases):
            signals.append(label)
    return signals


def extract_responsibilities(job_text: str) -> list[str]:
    responsibilities = []
    for raw_line in job_text.splitlines():
        line = raw_line.strip(" -\t")
        if len(line) < 20:
            continue
        lower = line.lower()
        if any(token in lower for token in ("build", "develop", "design", "implement", "test", "collaborate", "maintain")):
            responsibilities.append(line)
        if len(responsibilities) >= 8:
            break
    return responsibilities


def calculate_fit_score(
    matched: list[str],
    missing_required: list[str],
    preferred: list[str],
    resume_text: str,
    evidence: list[str],
    matched_keywords: list[str],
    job_keywords: list[str],
    evidence_coverage: float,
) -> float:
    total_required = len(matched) + len(missing_required)
    if total_required == 0:
        skill_score = 0.0
    else:
        skill_score = 100.0 * len(matched) / total_required
    keyword_denominator = max(1, min(20, len(job_keywords)))
    keyword_score = 100.0 * min(len(matched_keywords), keyword_denominator) / keyword_denominator
    if total_required == 0:
        base = keyword_score
    else:
        base = (skill_score * 0.75) + (keyword_score * 0.25)
    preferred_bonus = min(10.0, 2.0 * len(set(matched).intersection(preferred)))
    evidence_bonus = min(10.0, 2.5 * len(evidence))
    length_penalty = -2.0 if len(resume_text.split()) < 25 else 0.0
    evidence_factor = 0.75 + (0.25 * (evidence_coverage / 100.0)) if matched else 1.0
    adjusted_base = base * evidence_factor
    return round(max(0.0, min(100.0, adjusted_base + preferred_bonus + evidence_bonus + length_penalty)), 1)


def calculate_evidence_coverage(matched: list[str], evidence: list[str]) -> float:
    if not matched:
        return 0.0
    evidence_lines = min(len(evidence), len(matched))
    return round(100.0 * evidence_lines / len(matched), 1)


def build_improvement_areas(missing: list[str], responsibilities: list[str]) -> list[str]:
    areas = [f"Add credible project evidence for {skill}." for skill in missing[:6]]
    if responsibilities:
        areas.append("Map resume bullets to the job's core implementation and collaboration responsibilities.")
    if not areas:
        areas.append("Strengthen quantified impact and make the strongest project evidence easier to scan.")
    return areas


def normalize_for_matching(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9+#./\s\u4e00-\u9fff-]", " ", lowered)
    return re.sub(r"\s+", " ", lowered)


def extract_keywords(text: str, limit: int = 30) -> list[str]:
    normalized = normalize_for_matching(text)
    tokens = re.findall(r"[a-z][a-z0-9+#./-]{2,}|[\u4e00-\u9fff]{2,}", normalized)
    keywords: list[str] = []
    for token in tokens:
        clean = token.strip("-/.")
        if not clean or clean in STOPWORDS or clean.isdigit():
            continue
        if clean not in keywords:
            keywords.append(clean)
        if len(keywords) >= limit:
            break
    return keywords


def fallback_required_keywords(job_keywords: list[str]) -> list[str]:
    if len(job_keywords) < 3:
        return []
    return job_keywords[:10]


def contains_cjk(text: str) -> bool:
    return re.search(r"[\u4e00-\u9fff]", text) is not None
