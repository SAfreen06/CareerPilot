"""
Job search — takes parsed Tavily params, calls Tavily API,
returns raw results list. Now with Remotive integration.
"""
import os
import requests
from dotenv import load_dotenv
from app.agents.query_parser import parse_query
from app.agents.remotive_search import search_remotive_from_parsed_params, convert_remotive_to_job_card

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_URL = "https://api.tavily.com/search"


# ── Seed jobs (demo safety net) ───────────────────────────────────────────────

SEED_JOBS = [
    {
        "title": "Backend Engineer Intern",
        "url": "#",
        "content": "Looking for Python and FastAPI developers with REST API experience. "
                   "Basic knowledge of PostgreSQL required. Remote-friendly team.",
        "score": 0.75,
        "source": "curated",
    },
    {
        "title": "ML Engineer Intern",
        "url": "#",
        "content": "Seeking candidates with Python and machine learning basics. "
                   "TensorFlow or scikit-learn experience preferred. Dhaka office.",
        "score": 0.74,
        "source": "curated",
    },
    {
        "title": "Frontend Developer Intern",
        "url": "#",
        "content": "React and Tailwind CSS experience required. "
                   "Will work on real product features from day one. Dhaka based.",
        "score": 0.73,
        "source": "curated",
    },
]


# ── Tavily search ─────────────────────────────────────────────────────────────

def search_jobs(user_query: str, use_remotive: bool = True) -> list[dict]:
    # Step 1: parse query (for Tavily)
    params = parse_query(user_query)
    print(f"[job_search] Parsed params: {params}")

    results = []
    
    # Step 2: call Tavily (uses parsed query with location)
    tavily_results = _call_tavily(params)
    tavily_results = [r for r in tavily_results if r.get("score", 0) >= 0.4]
    print(f"[job_search] Tavily returned {len(tavily_results)} results after filtering")
    results.extend(tavily_results)
    
    # Step 3: call Remotive with ORIGINAL query
    if use_remotive:
        # Create a new params dict with the ORIGINAL query
        remotive_params = {
            "query": user_query,  # Use original user query
            "filters": params.get("filters", {}),  # Keep filters
            "max_results": params.get("max_results", 10)
        }
        
        remotive_jobs = search_remotive_from_parsed_params(remotive_params)
        print(f"[job_search] Remotive returned {len(remotive_jobs)} results")
        results.extend(remotive_jobs)
    
    
    # Step 4: deduplicate by URL
    seen_urls = set()
    unique_results = []
    for r in results:
        url = r.get("url", "")
        if url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(r)
    
    # Step 5: append seed jobs if still sparse
    if len(unique_results) < 3:
        print("[job_search] Sparse results — appending seed jobs")
        unique_results = unique_results + SEED_JOBS
    
    print(f"[job_search] Total {len(unique_results)} unique results (Tavily: {len(tavily_results)}, Remotive: {len(remotive_jobs) if use_remotive else 0})")
    
    return unique_results


def _call_tavily(params: dict) -> list[dict]:
    query = params["query"]

    # For BD searches, add site hints to the query string instead
    if params.get("country") == "bangladesh":
        if "bangladesh" not in query.lower() and "dhaka" not in query.lower():
            query = query + " Dhaka Bangladesh"

    payload = {
        "query": query,
        "max_results": params["max_results"],
        "search_depth": "basic",
    }

    if params.get("time_range"):
        payload["time_range"] = params["time_range"]

    if params.get("country"):
        payload["country"] = params["country"]

    try:
        response = requests.post(
            TAVILY_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TAVILY_API_KEY}",
            },
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])

    except requests.exceptions.Timeout:
        print("[job_search] Tavily request timed out")
        return []

    except requests.exceptions.RequestException as e:
        print(f"[job_search] Tavily request failed: {e}")
        return []


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    query = "software engineer intern remote"
    print(f"Searching for: {query}\n")
    results = search_jobs(query)

    for i, r in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Title   : {r.get('title')}")
        print(f"  URL     : {r.get('url')}")
        print(f"  Source  : {r.get('source')}")
        print(f"  Score   : {r.get('score')}")
        print(f"  Content : {r.get('content', '')[:120]}...")
        print()