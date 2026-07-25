from pydantic import BaseModel, Field


class AnalysisCreate(BaseModel):
    resume_id: int
    job_description_id: int
    model_name: str | None = Field(default=None, max_length=128)


class DocumentResponse(BaseModel):
    resume_id: int | None = None
    job_description_id: int | None = None
    extracted_text_preview: str
    detected_sections: list[str] = []
    detected_role_keywords: list[str] = []


class AnalysisCreateResponse(BaseModel):
    analysis_id: int
    deterministic_fit_score: float
    ollama_status: str
    ollama_model: str


class PortfolioPlanCreate(BaseModel):
    analysis_id: int
    existing_project_names: list[str] = []
