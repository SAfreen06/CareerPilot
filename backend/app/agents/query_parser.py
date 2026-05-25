import json
import re
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a job search query parser. Extract structured parameters 
from the user's natural language job search query.

Output ONLY a valid JSON object with these exact fields:

{
  "query": "cleaned job search string for web search",
  "time_range": "day | week | month | year | null",
  "country": "bangladesh | null",
  "is_remote": true/false
  "max_results": 10,
  "filters": {
    "job_type": "full-time | part-time | internship | contract | null",
    "salary_min": null,
    "salary_max": null,
    "skills_required": [],
    "experience_level": "junior | mid | senior | null"
  }
}

Rules for "query":
  Convert to a clean web search string. Include role + location.
  "Find ML internships in Dhaka"     → "machine learning intern jobs Dhaka Bangladesh"
  "Remote React jobs"                → "React developer remote jobs"
  "Senior Python backend Bangladesh" → "senior Python backend developer jobs Bangladesh"
  Never append "jobs Bangladesh" if location or role already implies it clearly.

Rules for "time_range":
  "today"                   → "day"
  "this week" / "last 7 days" → "week"
  "this month" / "open this month" → "month"
  "this year"               → "year"
  nothing mentioned         → "month"

Rules for "country":
  Mentions Bangladesh / Dhaka / BD / any BD city → "bangladesh"
  Says "remote" with no country                  → null
  Mentions another country                       → null
  Nothing mentioned                              → "bangladesh"


Rules for "filters":
  "job_type":
    intern / internship in query → "internship"
    full time / full-time        → "full-time"
    part time / part-time        → "part-time"
    contract / freelance         → "contract"
    nothing mentioned            → null

  "salary_min" / "salary_max":
    "above 50k" / "minimum 50000"  → salary_min: 50000, salary_max: null
    "below 80k"                    → salary_min: null, salary_max: 80000
    "50k to 80k"                   → salary_min: 50000, salary_max: 80000
    nothing mentioned              → both null
    Always use integer BDT values.

  "skills_required":
    Extract any explicitly mentioned technologies or tools.
    "Python developer"      → ["Python"]
    "React and Node.js job" → ["React", "Node.js"]
    "ML internship"         → ["Machine Learning"]
    nothing specific        → []

  "experience_level":
    junior / entry level / fresher → "junior"
    senior / lead / principal      → "senior"
    mid / intermediate             → "mid"
    nothing mentioned              → null

IMPORTANT: Respond ONLY with the JSON object. No explanation. No markdown. No code fences.
"""


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_query(user_query: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\n\nUser query: \"{user_query}\""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw_text = response.choices[0].message.content.strip()
        raw_text = re.sub(r"```json|```", "", raw_text).strip()

        parsed = json.loads(raw_text)
        return validate_params(parsed, user_query)

    except json.JSONDecodeError:
        print(f"[query_parser] JSON parse failed. Raw: {raw_text}")
        return default_params(user_query)

    except Exception as e:
        print(f"[query_parser] Unexpected error: {e}")
        return default_params(user_query)


# ── Validator ─────────────────────────────────────────────────────────────────

VALID_TIME_RANGES = {"day", "week", "month", "year"}
DEFAULT_DOMAINS = [
    "bdtechjobs.com",
    "bdjobs.com",
    "jobs.com.bd",
    "chakri.com",
    "glassdoor.com",
]


def validate_params(raw: dict, original_query: str) -> dict:
    query = str(raw.get("query", "")).strip()
    if not query:
        query = original_query + " jobs Bangladesh"

    time_range = raw.get("time_range")
    if time_range not in VALID_TIME_RANGES:
        time_range = "month"

    country = raw.get("country")
    if country is not None:
        country = str(country).lower().strip()
        if country not in {"bangladesh"}:
            country = None

    domains = raw.get("include_domains", [])
    if not isinstance(domains, list) or not domains:
        domains = DEFAULT_DOMAINS

    # Validate filters block
    raw_filters = raw.get("filters", {}) or {}
    filters = {
        "job_type": raw_filters.get("job_type") if raw_filters.get("job_type") in
                    {"full-time", "part-time", "internship", "contract"} else None,
        "salary_min": int(raw_filters["salary_min"]) if raw_filters.get("salary_min") else None,
        "salary_max": int(raw_filters["salary_max"]) if raw_filters.get("salary_max") else None,
        "skills_required": raw_filters.get("skills_required") if
                           isinstance(raw_filters.get("skills_required"), list) else [],
        "experience_level": raw_filters.get("experience_level") if raw_filters.get("experience_level") in
                            {"junior", "mid", "senior"} else None,
    }

    return {
        "query": query,
        "time_range": time_range,
        "country": country,
        "include_domains": domains,
        "max_results": 10,
        "filters": filters,
    }

def default_params(original_query: str) -> dict:
    return {
        "query": original_query + " jobs Bangladesh",
        "time_range": "month",
        "country": "bangladesh",
        "include_domains": DEFAULT_DOMAINS,
        "max_results": 10,
        "filters": {
            "job_type": None,
            "salary_min": None,
            "salary_max": None,
            "skills_required": [],
            "experience_level": None,
        }
    }


# ── Quick test ────────────────────────────────────────────────────────────────

import time

if __name__ == "__main__":
    test_queries = [
        "Find ML internships in Dhaka open this month",
        "Remote React developer jobs posted this week",
        "Senior Python backend roles in Bangladesh salary above 50k",
        "Data science jobs today",
        "Flutter developer jobs",
    ]

    for q in test_queries:
        print(f"\nQuery   : {q}")
        result = parse_query(q)
        print(f"Parsed  : {json.dumps(result, indent=2)}")
        print("-" * 60)
        time.sleep(4)  # stay within free tier rate limits