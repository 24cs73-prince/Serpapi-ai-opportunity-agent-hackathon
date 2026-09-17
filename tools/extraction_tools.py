"""
OpportunityIQ — Extraction Tools

LLM-powered extraction of structured Opportunity objects
from raw search results. Normalizes messy web data into
clean, comparable records.
"""

import json
from typing import Optional
from analysis.opportunity import Opportunity
from tools.search_tools import SearchResponse, JobResult
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_opportunities_from_jobs(search_response: SearchResponse) -> list[Opportunity]:
    """
    Convert job search results into structured Opportunity objects.
    
    This does basic extraction from the structured Google Jobs data.
    For deeper analysis, LLM extraction can be used.
    """
    opportunities = []
    
    for job in search_response.jobs:
        opp = Opportunity(
            title=job.title,
            company=job.company or None,
            description=job.description or None,
            location=job.location or None,
            work_mode=job.work_mode if job.work_mode != "Not specified" else None,
            opportunity_type=_detect_opportunity_type(job),
            salary=job.salary if job.salary != "Not found in available sources" else None,
            published_date=job.posted_at if job.posted_at != "Not specified" else None,
            source="Google Jobs",
            application_url=job.apply_link or None,
            required_skills=_extract_skills_from_description(job.description),
            raw_extensions=job.extensions,
            search_confidence="high",
        )
        opportunities.append(opp)
    
    logger.info(f"Extracted {len(opportunities)} opportunities from job results")
    return opportunities


def extract_opportunities_from_search(items: list | SearchResponse) -> list[Opportunity]:
    """
    High-level extractor for search results.
    Accepts SearchResponse, list of JobResult objects, or list of dicts/Opportunity objects.
    """
    if isinstance(items, SearchResponse):
        return extract_opportunities_with_llm(items)
    
    if isinstance(items, list):
        if not items:
            return []
        if all(isinstance(x, Opportunity) for x in items):
            return items
            
        jobs = []
        for item in items:
            if isinstance(item, JobResult):
                jobs.append(item)
            elif isinstance(item, dict):
                jobs.append(JobResult(
                    title=item.get("title", "Opportunity"),
                    company=item.get("company", "Company"),
                    location=item.get("location"),
                    description=item.get("description"),
                    apply_link=item.get("apply_link") or item.get("link"),
                    salary=item.get("salary") or "Not found",
                    posted_at=item.get("posted_at") or "Not specified",
                    extensions=item.get("extensions", []),
                ))
        
        response = SearchResponse(success=True, search_type="google_jobs", jobs=jobs)
        return extract_opportunities_with_llm(response)
    
    return []



def extract_opportunities_with_llm(
    search_response: SearchResponse,
    max_results: int = 10,
) -> list[Opportunity]:
    """
    Use LLM to extract detailed, structured opportunities from search results.
    Falls back to basic extraction if LLM is unavailable.
    """
    from config import config
    
    if not config.llm.is_configured:
        logger.info("LLM not configured — using basic extraction")
        return extract_opportunities_from_jobs(search_response)
    
    # First do basic extraction
    opportunities = extract_opportunities_from_jobs(search_response)
    
    # Then enhance with LLM for skill extraction
    if opportunities:
        enhanced = _enhance_with_llm(opportunities[:max_results], config)
        if enhanced:
            return enhanced
    
    return opportunities


def _enhance_with_llm(opportunities: list[Opportunity], config) -> Optional[list[Opportunity]]:
    """Use LLM to enhance opportunities with better skill extraction."""
    
    # Build a compact representation for the LLM
    opp_summaries = []
    for i, opp in enumerate(opportunities):
        opp_summaries.append({
            "index": i,
            "title": opp.title,
            "company": opp.company,
            "description": (opp.description or "")[:500],
            "extensions": opp.raw_extensions,
        })
    
    prompt = f"""Analyze these job/internship listings and extract skills for each.

For each listing, return:
- required_skills: skills explicitly required
- preferred_skills: nice-to-have skills
- opportunity_type: "Internship", "Full-time", "Part-time", "Contract", or "Unknown"
- eligibility: who should apply (if mentioned)

Return ONLY a valid JSON array:
[
  {{
    "index": 0,
    "required_skills": ["Python", "ML"],
    "preferred_skills": ["Docker"],
    "opportunity_type": "Internship",
    "eligibility": "3rd/4th year CS students"
  }}
]

Listings:
{json.dumps(opp_summaries, indent=2)}
"""
    
    try:
        if config.llm.provider == "gemini":
            result = _call_gemini(prompt, config)
        elif config.llm.provider == "openai":
            result = _call_openai(prompt, config)
        else:
            return None
        
        if not result:
            return None
        
        # Apply enhancements
        for item in result:
            idx = item.get("index", -1)
            if 0 <= idx < len(opportunities):
                opp = opportunities[idx]
                if item.get("required_skills"):
                    opp.required_skills = item["required_skills"]
                if item.get("preferred_skills"):
                    opp.preferred_skills = item["preferred_skills"]
                if item.get("opportunity_type"):
                    opp.opportunity_type = item["opportunity_type"]
                if item.get("eligibility"):
                    opp.eligibility = item["eligibility"]
        
        logger.info(f"Enhanced {len(result)} opportunities with LLM")
        return opportunities
        
    except Exception as e:
        logger.error(f"LLM enhancement failed: {e}")
        return None


def _call_gemini(prompt: str, config) -> Optional[list]:
    """Call Gemini API and parse JSON response."""
    import google.generativeai as genai
    
    genai.configure(api_key=config.llm.api_key)
    model = genai.GenerativeModel(config.llm.model_name)
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    
    return json.loads(text)


def _call_openai(prompt: str, config) -> Optional[list]:
    """Call OpenAI API and parse JSON response."""
    from openai import OpenAI
    
    client = OpenAI(api_key=config.llm.api_key)
    response = client.chat.completions.create(
        model=config.llm.model_name,
        messages=[
            {"role": "system", "content": "You extract structured data from job listings. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    text = response.choices[0].message.content.strip()
    parsed = json.loads(text)
    
    # Handle both {"results": [...]} and [...] formats
    if isinstance(parsed, dict):
        return parsed.get("results", parsed.get("opportunities", []))
    return parsed


def _detect_opportunity_type(job: JobResult) -> Optional[str]:
    """Detect opportunity type from job extensions."""
    ext_text = " ".join(job.extensions).lower()
    title_lower = job.title.lower()
    
    if "intern" in title_lower or "intern" in ext_text:
        return "Internship"
    if "full-time" in ext_text or "full time" in ext_text:
        return "Full-time"
    if "part-time" in ext_text or "part time" in ext_text:
        return "Part-time"
    if "contract" in ext_text:
        return "Contract"
    return None


def _extract_skills_from_description(description: str) -> list[str]:
    """Basic skill extraction from description text using keyword matching."""
    if not description:
        return []
    
    # Common tech skills to look for
    known_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "Scikit-learn", "Keras",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git",
        "SQL", "PostgreSQL", "MongoDB", "Redis",
        "REST", "GraphQL", "Microservices",
        "Linux", "CI/CD", "Jenkins",
        "Pandas", "NumPy", "Spark",
        "LLM", "RAG", "LangChain", "GenAI", "Generative AI",
        "HTML", "CSS", "Streamlit",
    ]
    
    desc_lower = description.lower()
    found = []
    for skill in known_skills:
        if skill.lower() in desc_lower:
            found.append(skill)
    
    return found[:15]  # Cap at 15 skills
