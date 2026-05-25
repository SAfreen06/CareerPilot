"""
Jobs router — FastAPI endpoint for job search.
POST /api/jobs/search
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.job_search import search_jobs
from app.agents.job_extractor import extract_all_jobs

router = APIRouter()


class JobSearchRequest(BaseModel):
    query: str
    user_id: str = "test_user"  # will be real user ID once auth is ready


@router.post("/search")
def search(request: JobSearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Step 1: parse query + fetch from Tavily
    raw_results = search_jobs(request.query)

    # Step 2: extract structured fields from each result
    job_cards = extract_all_jobs(raw_results)

    # Step 3: fit score (plug in M1's function here when ready)
    # from app.services.fit_score import compute_fit_score
    # for card in job_cards:
    #     fit = compute_fit_score(request.user_id, card["role"], card["summary"])
    #     card["fit_percent"] = fit["fit_percent"]
    #     card["matched_skills"] = fit["matched_skills"]
    #     card["missing_skills"] = fit["missing_skills"]
    #     card["reasoning"] = fit["reasoning"]

    # Step 4: sort by relevance score
    job_cards.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    return {"results": job_cards, "total": len(job_cards)}