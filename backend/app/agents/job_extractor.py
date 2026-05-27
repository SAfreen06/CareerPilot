"""
Job extractor — takes raw Tavily results, uses Groq (Llama)
to extract structured job card fields from each snippet.

Member 2 owns this file.
"""
import json
import re
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ── Prompt ────────────────────────────────────────────────────────────────────

EXTRACT_PROMPT = """You are extracting job listing details from a web search snippet.

Given the title and content snippet below, extract these fields as JSON:

{
  "role": "exact job title",
  "company": "company name or null",
  "location": "city/country or null",
  "salary": "salary info as string or null",
  "deadline": "application deadline or null",
  "job_type": "full-time | part-time | internship | contract | null",
  "skills": ["list", "of", "skills", "mentioned"],
  "summary": "one sentence describing the role"
}

Rules:
- If a field is not mentioned anywhere in the snippet, use null
- For skills, only include explicitly mentioned technologies/tools
- For job_type, infer from context — "intern" means "internship"
- Keep summary under 15 words
- **CRITICAL - Company Name Rules:**
  * Extract the company that is ACTUALLY HIRING, not the job board/platform
  * NEVER use these platform names as company: Job Media, bdjobs, Bdtechjobs, Facebook, LinkedIn, Upwork, Freelancer, Indeed, Glassdoor, Monster, Naukri, ZipRecruiter, Himalayas, Remotive
  * If the job is on a platform, look for the real company name in the content
  * If no real company name is found, use null
- Respond ONLY with the JSON object. No explanation. No markdown. No code fences.
"""


# ── Extractor ─────────────────────────────────────────────────────────────────

def extract_job_fields(title: str, content: str) -> dict:
    """
    Extracts structured fields from a single Tavily result.
    Returns a dict with role, company, location, salary, etc.
    """
    prompt = EXTRACT_PROMPT + f"\n\nTitle: {title[:200]}\nContent: {content[:600]}"

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw_text = response.choices[0].message.content.strip()
        raw_text = re.sub(r"```json|```", "", raw_text).strip()
        parsed = json.loads(raw_text)
        return sanitize_fields(parsed)

    except json.JSONDecodeError:
        print(f"[job_extractor] JSON parse failed for: {title}")
        return fallback_fields(title)

    except Exception as e:
        print(f"[job_extractor] Error: {e}")
        return fallback_fields(title)


def sanitize_fields(raw: dict) -> dict:
    """Enforce types and clean up LLM output."""
    
    # List of job board/platform names to filter out
    PLATFORM_NAMES = {
        "job media", "job media ltd", "bdjobs", "bdtechjobs", "chakri", 
        "facebook", "linkedin", "twitter", "instagram", "upwork", 
        "freelancer", "indeed", "glassdoor", "monster", "naukri",
        "ziprecruiter", "himalayas", "remotive", "dailyremote", "web3",
        "bebee", "expertini", "dhakacareers", "jobs.com.bd"
    }
    
    company = str(raw.get("company") or "").strip() if raw.get("company") else None
    
    # Filter out platform names
    if company:
        company_clean = company.lower()
        is_platform = any(platform in company_clean for platform in PLATFORM_NAMES)
        if is_platform:
            company = None
    
    return {
        "role": str(raw.get("role") or "").strip() or "Software Engineer",
        "company": company,
        "location": str(raw.get("location")).strip() if raw.get("location") else None,
        "salary": str(raw.get("salary")).strip() if raw.get("salary") else None,
        "deadline": str(raw.get("deadline")).strip() if raw.get("deadline") else None,
        "job_type": raw.get("job_type") if raw.get("job_type") in
                    {"full-time", "part-time", "internship", "contract"} else None,
        "skills": raw.get("skills") if isinstance(raw.get("skills"), list) else [],
        "summary": str(raw.get("summary") or "").strip(),
    }


def fallback_fields(title: str) -> dict:
    """Safe fallback when extraction completely fails."""
    return {
        "role": title,
        "company": None,
        "location": "Bangladesh",
        "salary": None,
        "deadline": None,
        "job_type": None,
        "skills": [],
        "summary": "",
    }


# ── Batch extractor ───────────────────────────────────────────────────────────

def extract_all_jobs(raw_results: list[dict]) -> list[dict]:
    """
    Runs field extraction on every Tavily result.
    Returns list of enriched job card dicts.
    """
    job_cards = []

    for result in raw_results:
        title = result.get("title", "")
        content = result.get("content", "")
        url = result.get("url", "#")
        score = result.get("score", 0.0)
        source = result.get("source", "tavily")

        fields = extract_job_fields(title, content)

        job_card = {
            **fields,
            "apply_url": url,
            "relevance_score": round(score, 3),
            "source": source,
            "fit_percent": None,
            "matched_skills": [],
            "missing_skills": [],
            "reasoning": "",
        }
        job_cards.append(job_card)

    return job_cards


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mock_results = [
        {
            "title": "ML Engineer Intern — Brain Station 23",
            "url": "https://bdjobs.com/example",
            "content": "Brain Station 23 is looking for an ML Engineer Intern in Dhaka. "
                       "Required skills: Python, TensorFlow, REST APIs. "
                       "Salary: BDT 15,000–20,000/month. Deadline: June 30, 2025. "
                       "Full-time internship position.",
            "score": 0.93,
        },
        {
            "title": "React Developer Jobs Bangladesh | LinkedIn",
            "url": "https://linkedin.com/jobs/...",
            "content": "68 React developer jobs in Bangladesh. "
                       "Junior React Developer at Chaldal — Dhaka. "
                       "Skills: React, JavaScript, Tailwind CSS. Remote friendly.",
            "score": 0.85,
        },
    ]

    print("Extracting job fields...\n")
    cards = extract_all_jobs(mock_results)

    for card in cards:
        print(json.dumps(card, indent=2))
        print("-" * 60)