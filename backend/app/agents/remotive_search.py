"""
Remotive job search — fetches remote jobs from Remotive's public API.
No API key required.
"""
import requests
import re
from typing import List, Dict, Optional

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"


def search_remotive_from_parsed_params(parsed_params: Dict) -> List[Dict]:
    """
    Convert our existing parsed query parameters to Remotive API calls.
    """
    query = parsed_params.get("query", "")
    filters = parsed_params.get("filters", {})
    
    # Extract search term from query
    search_term = _extract_search_term(query)
    print(f"[remotive_search] Extracted search term: '{search_term}'")
    
    # Map skills to category if possible
    skills = filters.get("skills_required", [])
    category = _infer_category_from_skills(skills) or _infer_category_from_query(query)
    
    jobs = _fetch_remotive_jobs(
        search_term=search_term,
        category=category,
        limit=parsed_params.get("max_results", 20)
    )
    
    print(f"[remotive_search] After fetch, got {len(jobs)} jobs")
    
    # SKIP job_type filtering for Remotive - Remotive's job_type field is unreliable
    # Many good jobs have null job_type, so we don't want to filter them out
    
    # Convert to job cards with the query for scoring
    converted_jobs = []
    for job in jobs:
        converted = convert_remotive_to_job_card(job, query)
        converted_jobs.append(converted)
    
    print(f"[remotive_search] Returning {len(converted_jobs)} jobs")
    
    # Print first job title for debugging
    if converted_jobs:
        print(f"[remotive_search] First job: {converted_jobs[0].get('title')} - Score: {converted_jobs[0].get('score')}")
    
    return converted_jobs


def convert_remotive_to_job_card(remotive_job: Dict, search_query: str = "") -> Dict:
    """
    Convert a Remotive API job to our internal job card format.
    """
    # Determine location type
    job_location = remotive_job.get("candidate_required_location", "")
    if "bangladesh" in job_location.lower() or "dhaka" in job_location.lower():
        location_type = "on-site"
    elif job_location and job_location.lower() not in ["worldwide", "anywhere"]:
        location_type = f"remote - {job_location}"
    else:
        location_type = "remote - global"
    
    return {
        "title": remotive_job.get("title", ""),
        "url": remotive_job.get("url", "#"),
        "content": _clean_description(remotive_job.get("description", "")),
        "score": _calculate_relevance_score(remotive_job, search_query),
        "source": "remotive",
        "location_type": location_type,
        "_remotive_id": remotive_job.get("id"),
        "_company_name": remotive_job.get("company_name"),
        "_location": job_location,
        "_salary": remotive_job.get("salary"),
        "_job_type": remotive_job.get("job_type"),
        "_publication_date": remotive_job.get("publication_date"),
    }
    
    
def _calculate_relevance_score(job: Dict, query: str) -> float:
    """Calculate relevance score based on query matching."""
    if not query:
        return 0.70
    
    score = 0.50
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    title = job.get("title", "").lower()
    description = job.get("description", "")[:500].lower()
    
    # Remove common stop words
    stop_words = {"jobs", "job", "in", "at", "for", "with", "remote", "bangladesh", "dhaka", "a", "an", "the"}
    important_query_words = [w for w in query_words if w not in stop_words]
    
    # Bonus for title match
    title_matches = 0
    for word in important_query_words:
        if word in title:
            title_matches += 1
    
    if title_matches > 0:
        score += min(0.35, title_matches * 0.12)
    
    # Skill-specific bonuses
    if "python" in query_lower and "python" in title:
        score += 0.10
    if "react" in query_lower and "react" in title:
        score += 0.10
    if "javascript" in query_lower and ("javascript" in title or "js" in title):
        score += 0.10
    
    # Description matches
    desc_matches = 0
    for word in important_query_words:
        if word in description and len(word) > 2:
            desc_matches += 1
    score += min(0.15, desc_matches * 0.03)
    
    # Penalty for no matches
    if title_matches == 0 and desc_matches == 0:
        score -= 0.15
    
    return round(min(0.95, max(0.35, score)), 3)


def _fetch_remotive_jobs(search_term: str = None, category: str = None, limit: int = 20) -> List[Dict]:
    """Fetch jobs from Remotive API with client-side filtering."""
    params = {}
    if search_term:
        params["search"] = search_term
    if category:
        params["category"] = category
    if limit:
        params["limit"] = limit * 2  # Fetch more to allow for filtering
    
    try:
        response = requests.get(REMOTIVE_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        jobs = data.get("jobs", [])
        
        # Client-side filtering for better results
        if search_term and search_term.strip():
            search_terms = search_term.lower().split()
            filtered_jobs = []
            for job in jobs:
                title = job.get("title", "").lower()
                description = job.get("description", "")[:500].lower()
                
                # Job must match at least one search term
                if any(term in title or term in description for term in search_terms):
                    filtered_jobs.append(job)
            
            print(f"[remotive_search] API returned {len(jobs)} jobs, filtered to {len(filtered_jobs)} matching '{search_term}'")
            
            if filtered_jobs:
                print(f"[remotive_search] Example match: {filtered_jobs[0].get('title')}")
            
            return filtered_jobs[:limit]
        
        print(f"[remotive_search] Found {len(jobs)} jobs from Remotive")
        return jobs[:limit]
        
    except requests.exceptions.RequestException as e:
        print(f"[remotive_search] API request failed: {e}")
        return []


def _extract_search_term(query: str) -> str:
    """Extract key terms from natural language query."""
    stop_words = {"jobs", "job", "in", "at", "for", "with", "remote", "bangladesh", "dhaka", "a", "an", "the", "to", "of", "and", "i", "am", "looking", "for", "find", "me", "a"}
    words = query.lower().split()
    
    # Keep important words (skills, roles)
    important_words = []
    for word in words:
        if word not in stop_words and len(word) > 1:
            important_words.append(word)
    
    # Return the most relevant terms
    result = " ".join(important_words[:3]) if important_words else ""
    return result


def _infer_category_from_skills(skills: List[str]) -> Optional[str]:
    """Infer Remotive category from skills list."""
    if not skills:
        return None
    
    all_skills = " ".join(s.lower() for s in skills)
    
    if any(tech in all_skills for tech in ["python", "tensorflow", "pytorch", "ml", "ai"]):
        return "software-dev"
    if any(tech in all_skills for tech in ["sql", "tableau", "power bi", "analytics"]):
        return "data-science"
    if any(tech in all_skills for tech in ["react", "angular", "vue", "frontend"]):
        return "software-dev"
    
    return None


def _infer_category_from_query(query: str) -> Optional[str]:
    """Infer Remotive category from the search query."""
    query_lower = query.lower()
    
    if "data" in query_lower:
        return "data-science"
    if any(x in query_lower for x in ["dev", "software", "developer", "engineer", "python", "react"]):
        return "software-dev"
    
    return "software-dev"


def _map_job_type(job_type: str) -> Optional[str]:
    """Map our job_type format to Remotive's format."""
    mapping = {
        "full-time": "full_time",
        "part-time": "part_time",
        "internship": "internship",
        "contract": "contract",
    }
    return mapping.get(job_type)


def _clean_description(html_desc: str) -> str:
    """Convert HTML description to plain text."""
    clean = re.sub(r'<[^>]+>', ' ', html_desc)
    clean = re.sub(r'\s+', ' ', clean)
    return clean[:800]