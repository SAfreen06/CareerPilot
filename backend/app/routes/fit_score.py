"""
Fit score route — POST /api/fit-score
M2 owns this.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.fit_score import compute_fit_score

router = APIRouter()


class FitScoreRequest(BaseModel):
    file_id: str
    job_title: str
    job_description: str


class FitScoreResponse(BaseModel):
    fit_percent: int
    matched_skills: list[str]
    missing_skills: list[str]
    reasoning: str


@router.post("/fit-score", response_model=FitScoreResponse)
def fit_score(req: FitScoreRequest):
    if not req.file_id.strip():
        raise HTTPException(status_code=400, detail="file_id is required")
    if not req.job_description.strip():
        raise HTTPException(status_code=400, detail="job_description is required")

    result = compute_fit_score(
        file_id=req.file_id,
        job_title=req.job_title,
        job_description=req.job_description,
    )
    return FitScoreResponse(**result)