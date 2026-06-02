"""
Fit score service — M2 owns this.
Uses M1's embeddings.py and vector_store.py directly.
"""
import json
import re
import os
from groq import Groq
from dotenv import load_dotenv
from app.services.embeddings import embed_texts
from app.services.vector_store import query_embeddings

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT = """You are a career advisor. Your task is strictly defined:

STEP 1: Extract the required skills from the JOB DESCRIPTION only.
STEP 2: For each required skill, check if it appears in the CV EXCERPTS.
STEP 3: Return the results.

Rules:
- matched_skills: required job skills that ARE in the CV
- missing_skills: required job skills that are NOT in the CV
- Do NOT include any skill that is not required by the job
- Do NOT list CV skills that the job doesn't ask for
- fit_percent: be realistic and never give 100% — there are always unknown gaps. Max score is 95.
  * 85-95: almost all job skills matched
  * 65-84: most core skills matched, some gaps
  * 40-64: some skills matched, significant gaps
  * 0-39: poor match
- reasoning: one sentence

Respond ONLY with raw JSON. No markdown.

Job title: JOB_TITLE
Job description: JOB_DESC
CV excerpts: CV_CHUNKS"""


def compute_fit_score(file_id: str, job_title: str, job_description: str) -> dict:
    """
    1. Embed the job description
    2. Query CV vectors for top matching chunks
    3. Use LLM to compute fit score, matched/missing skills and reasoning
    """
    # Step 1 — embed job description
    jd_embeddings = embed_texts([job_description[:1000]])
    if not jd_embeddings:
        return _fallback()

    jd_embedding = jd_embeddings[0]

    # Step 2 — retrieve top CV chunks relevant to this job
    result = query_embeddings(
        query_embedding=jd_embedding,
        n_results=6,
        source=file_id,
    )
    cv_chunks = result.get("documents", [])

    if not cv_chunks:
        return _fallback()

    # Step 3 — LLM computes score and explains it
    prompt = (PROMPT
        .replace("JOB_TITLE", job_title[:200])
        .replace("JOB_DESC", job_description[:600])
        .replace("CV_CHUNKS", "\n".join(cv_chunks[:4]))
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        parsed = json.loads(raw)

        return {
            "fit_percent": int(parsed.get("fit_percent", 50)),
            "matched_skills": parsed.get("matched_skills", []),
            "missing_skills": parsed.get("missing_skills", []),
            "reasoning": parsed.get("reasoning", ""),
        }

    except json.JSONDecodeError:
        print(f"[fit_score] JSON parse failed")
        return _fallback()

    except Exception as e:
        print(f"[fit_score] Error: {e}")
        return _fallback()


def _fallback() -> dict:
    return {
        "fit_percent": 0,
        "matched_skills": [],
        "missing_skills": [],
        "reasoning": "No CV data found. Please upload your CV first.",
    }