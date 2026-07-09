import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.database import get_db, init_db
from app.schemas import AnalysisCreate, AnalysisCreateResponse, DocumentResponse
from app.services.goals import build_growth_goals
from app.services.job_recommendations import recommend_matching_jobs
from app.services.matching import analyze_resume_against_job, extract_skills, infer_role_title
from app.services.ollama import generate_llm_analysis
from app.services.parsing import detect_resume_sections, extract_input_text, preview_text


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Resume Growth Coach", version="0.1.0", lifespan=lifespan)
APP_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"result": None, "error": None, "form_values": {"resume_text": "", "job_description_text": ""}},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ui/analyze", response_class=HTMLResponse)
async def analyze_from_ui(
    request: Request,
    resume_text: str = Form(""),
    job_description_text: str = Form(""),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    form_values = {"resume_text": resume_text, "job_description_text": job_description_text}
    try:
        resume = create_resume(db, resume_text, "text", None)
        job = create_job_description(db, job_description_text, "text", None)
        analysis = run_analysis(db, resume.id, job.id, None)
        result = build_analysis_payload(db, analysis)
        return templates.TemplateResponse(request, "index.html", {"result": result, "error": None, "form_values": form_values})
    except HTTPException as exc:
        return templates.TemplateResponse(request, "index.html", {"result": None, "error": exc.detail, "form_values": form_values})


@app.post("/api/documents/resume", response_model=DocumentResponse)
async def upload_resume(
    text: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    content, source_type, filename = await extract_input_text(text, file)
    resume = create_resume(db, content, source_type, filename)
    return DocumentResponse(
        resume_id=resume.id,
        extracted_text_preview=preview_text(resume.content),
        detected_sections=json.loads(resume.detected_sections_json),
    )


@app.post("/api/documents/job-description", response_model=DocumentResponse)
async def upload_job_description(
    text: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    content, source_type, filename = await extract_input_text(text, file)
    job = create_job_description(db, content, source_type, filename)
    return DocumentResponse(
        job_description_id=job.id,
        extracted_text_preview=preview_text(job.content),
        detected_role_keywords=json.loads(job.detected_keywords_json),
    )


@app.post("/api/analyses", response_model=AnalysisCreateResponse)
def create_analysis(payload: AnalysisCreate, db: Session = Depends(get_db)) -> AnalysisCreateResponse:
    analysis = run_analysis(db, payload.resume_id, payload.job_description_id, payload.model_name)
    return AnalysisCreateResponse(
        analysis_id=analysis.id,
        deterministic_fit_score=analysis.fit_score,
        ollama_status=analysis.model_status,
        ollama_model=analysis.model_name,
    )


@app.get("/api/analyses/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)) -> dict:
    analysis = fetch_analysis(db, analysis_id)
    return build_analysis_payload(db, analysis)


@app.get("/api/goals/{analysis_id}")
def get_goals(analysis_id: int, db: Session = Depends(get_db)) -> dict:
    fetch_analysis(db, analysis_id)
    rows = db.query(models.GrowthGoal).filter(models.GrowthGoal.analysis_id == analysis_id).all()
    return {row.horizon: json.loads(row.goals_json) for row in rows}


def create_resume(db: Session, content: str, source_type: str, filename: str | None) -> models.Document:
    if not content.strip():
        raise HTTPException(status_code=400, detail="Resume content is required.")
    if len(content) > 1_000_000:
        raise HTTPException(status_code=413, detail="Resume content is too large for the local MVP.")
    resume = models.Document(
        source_type=source_type,
        filename=filename,
        content=content.strip(),
        detected_sections_json=json.dumps(detect_resume_sections(content)),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def create_job_description(db: Session, content: str, source_type: str, filename: str | None) -> models.JobDescription:
    if not content.strip():
        raise HTTPException(status_code=400, detail="Job description content is required.")
    if len(content) > 1_000_000:
        raise HTTPException(status_code=413, detail="Job description content is too large for the local MVP.")
    job = models.JobDescription(
        source_type=source_type,
        filename=filename,
        content=content.strip(),
        detected_keywords_json=json.dumps(extract_skills(content)),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_analysis(db: Session, resume_id: int, job_description_id: int, model_name: str | None) -> models.Analysis:
    resume = db.get(models.Document, resume_id)
    job = db.get(models.JobDescription, job_description_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume was not found.")
    if job is None:
        raise HTTPException(status_code=404, detail="Job description was not found.")

    deterministic = analyze_resume_against_job(resume.content, job.content)
    llm = generate_llm_analysis(deterministic, model_name)
    goals = build_growth_goals(deterministic)

    analysis = models.Analysis(
        resume_id=resume.id,
        job_description_id=job.id,
        fit_score=deterministic.fit_score,
        summary=llm["summary"],
        model_name=llm["model_name"],
        model_status=llm["model_status"],
        deterministic_result_json=json.dumps(
            {
                **deterministic.to_dict(),
                "project_suggestions": llm.get("project_suggestions", []),
                "resume_bullet_drafts": llm.get("resume_bullet_drafts", []),
            }
        ),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    for skill in deterministic.matched_skills:
        db.add(models.SkillMatch(analysis_id=analysis.id, match_type="matched", skill=skill))
    for skill in deterministic.missing_skills:
        db.add(models.SkillMatch(analysis_id=analysis.id, match_type="missing", skill=skill))
    for horizon, items in goals.items():
        db.add(models.GrowthGoal(analysis_id=analysis.id, horizon=horizon, goals_json=json.dumps(items)))
    db.commit()
    return analysis


def fetch_analysis(db: Session, analysis_id: int) -> models.Analysis:
    analysis = db.get(models.Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis was not found.")
    return analysis


def build_analysis_payload(db: Session, analysis: models.Analysis) -> dict:
    deterministic = json.loads(analysis.deterministic_result_json)
    goals = {
        row.horizon: json.loads(row.goals_json)
        for row in db.query(models.GrowthGoal).filter(models.GrowthGoal.analysis_id == analysis.id).all()
    }
    return {
        "analysis_id": analysis.id,
        "fit_summary": analysis.summary,
        "overall_fit_score": analysis.fit_score,
        "evidence_coverage": deterministic.get("evidence_coverage", 0.0),
        "ollama_status": analysis.model_status,
        "ollama_model": analysis.model_name,
        "ollama_display": build_model_display(analysis.model_status, analysis.model_name),
        "target_role_title": infer_role_title(analysis.job_description.content) or "Target Job Description",
        "matched_skills": deterministic["matched_skills"],
        "missing_skills": deterministic["missing_skills"],
        "matched_keywords": deterministic["matched_keywords"],
        "missing_keywords": deterministic["missing_keywords"],
        "evidence_found_in_resume": deterministic["matched_project_evidence"],
        "recommended_improvement_areas": deterministic["recommended_improvement_areas"],
        "growth_roadmap": goals,
        "recommended_project_additions": deterministic.get("project_suggestions", []),
        "recommended_matching_jobs": recommend_matching_jobs(analysis.resume.content, analysis.job_description.content),
        "english_resume_bullet_drafts": deterministic.get("resume_bullet_drafts", []),
        "deterministic_details": deterministic,
    }


def build_model_display(status: str, model_name: str) -> str:
    if status == "available":
        return f"Using {model_name}"
    return f"Fallback mode; configured model {model_name} was not used"
