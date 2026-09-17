"""
OpportunityIQ — High-Level Search Tools

Clean, validated search functions that the agent and UI can call.
Each function returns structured, normalized results —
never raw chaotic JSON.
"""

from typing import Any, Optional
from dataclasses import dataclass, field
from tools.serpapi_tools import SerpApiClient, SerpApiError
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class JobResult:
    """Normalized job result from Google Jobs."""
    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    extensions: list[str] = field(default_factory=list)
    detected_extensions: dict = field(default_factory=dict)
    apply_link: str = ""
    source: str = "Google Jobs"
    thumbnail: str = ""
    raw: dict = field(default_factory=dict)

    @property
    def work_mode(self) -> str:
        """Detect work mode from extensions."""
        ext_text = " ".join(self.extensions).lower()
        if "remote" in ext_text:
            return "Remote"
        if "hybrid" in ext_text:
            return "Hybrid"
        if "on-site" in ext_text or "on site" in ext_text:
            return "On-site"
        return "Not specified"

    @property
    def posted_at(self) -> str:
        """Extract posting time from detected extensions."""
        return self.detected_extensions.get("posted_at", "Not specified")

    @property
    def schedule_type(self) -> str:
        """Extract schedule type (full-time, part-time, internship)."""
        return self.detected_extensions.get("schedule_type", "Not specified")

    @property
    def salary(self) -> str:
        """Extract salary if available."""
        sal = self.detected_extensions.get("salary", "")
        return sal if sal else "Not found in available sources"


@dataclass
class WebResult:
    """Normalized web search result."""
    title: str = ""
    link: str = ""
    snippet: str = ""
    source: str = ""
    position: int = 0

    @property
    def display_source(self) -> str:
        return self.source or "Web"


@dataclass
class NewsResult:
    """Normalized news search result."""
    title: str = ""
    link: str = ""
    snippet: str = ""
    source: str = ""
    date: str = ""
    thumbnail: str = ""


@dataclass
class SearchResponse:
    """Unified search response container."""
    success: bool = True
    error: str = ""
    query: str = ""
    search_type: str = ""
    jobs: list[JobResult] = field(default_factory=list)
    web_results: list[WebResult] = field(default_factory=list)
    news_results: list[NewsResult] = field(default_factory=list)
    total_results: int = 0
    search_metadata: dict = field(default_factory=dict)

    @property
    def results(self) -> list[Any]:
        """Return all retrieved items (jobs, web results, or news results)."""
        if self.jobs:
            return self.jobs
        if self.web_results:
            return self.web_results
        if self.news_results:
            return self.news_results
        return []


# ── Module-level client ──
_client: Optional[SerpApiClient] = None


def _get_client() -> SerpApiClient:
    """Get or create the SerpApi client singleton."""
    global _client
    if _client is None:
        _client = SerpApiClient()
    return _client


def search_jobs(
    query: str,
    location: Optional[str] = None,
    date_posted: Optional[str] = None,
) -> SearchResponse:
    """
    Search for job/internship opportunities via Google Jobs.
    Includes automatic controlled fallback to Google Search if jobs API times out.
    """
    client = _get_client()
    response = SearchResponse(query=query, search_type="google_jobs")

    chips = None
    if date_posted:
        chips_map = {
            "today": "date_posted:today",
            "3days": "date_posted:3days",
            "week": "date_posted:week",
            "month": "date_posted:month",
        }
        chips = chips_map.get(date_posted)

    try:
        raw = client.search_google_jobs(query=query, location=location, chips=chips)
        response.search_metadata = raw.get("search_metadata", {})

        for job in raw.get("jobs_results", []):
            apply_options = job.get("apply_options", [])
            apply_link = apply_options[0].get("link", "") if apply_options else ""

            result = JobResult(
                title=job.get("title", ""),
                company=job.get("company_name", ""),
                location=job.get("location", ""),
                description=job.get("description", ""),
                extensions=job.get("extensions", []),
                detected_extensions=job.get("detected_extensions", {}),
                apply_link=apply_link,
                thumbnail=job.get("thumbnail", ""),
                raw=job,
            )
            response.jobs.append(result)

        response.total_results = len(response.jobs)
        logger.info(f"search_jobs: {response.total_results} results for '{query}'")

    except SerpApiError as e:
        response.success = False
        response.error = str(e)
        logger.warning(f"search_jobs issue for '{query}': {e}. Triggering controlled Google Search fallback...")

        # Controlled Fallback to Google Search
        try:
            web_resp = search_web(query=query, location=location, num=5)
            if web_resp.web_results:
                response.web_results = web_resp.web_results
                response.total_results = len(web_resp.web_results)
                logger.info(f"Fallback Google Search returned {response.total_results} results.")
        except Exception as fallback_err:
            logger.error(f"Fallback search failed: {fallback_err}")

    return response


def search_web(
    query: str,
    location: Optional[str] = None,
    num: int = 10,
) -> SearchResponse:
    """Search Google web results via SerpApi."""
    client = _get_client()
    response = SearchResponse(query=query, search_type="google")

    try:
        raw = client.search_google(query=query, location=location, num=num)
        response.search_metadata = raw.get("search_metadata", {})

        for item in raw.get("organic_results", []):
            result = WebResult(
                title=item.get("title", ""),
                link=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source=item.get("source", ""),
                position=item.get("position", 0),
            )
            response.web_results.append(result)

        response.total_results = len(response.web_results)
        logger.info(f"search_web: {response.total_results} results for '{query}'")

    except SerpApiError as e:
        response.success = False
        response.error = str(e)
        logger.error(f"search_web failed: {e}")

    return response


def search_news(
    query: str,
    location: Optional[str] = None,
) -> SearchResponse:
    """Search Google News via SerpApi."""
    client = _get_client()
    response = SearchResponse(query=query, search_type="google_news")

    try:
        raw = client.search_google_news(query=query, location=location)
        response.search_metadata = raw.get("search_metadata", {})

        for item in raw.get("news_results", []):
            result = NewsResult(
                title=item.get("title", ""),
                link=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source=item.get("source", {}).get("name", "") if isinstance(item.get("source"), dict) else item.get("source", ""),
                date=item.get("date", ""),
                thumbnail=item.get("thumbnail", ""),
            )
            response.news_results.append(result)

        response.total_results = len(response.news_results)
        logger.info(f"search_news: {response.total_results} results for '{query}'")

    except SerpApiError as e:
        response.success = False
        response.error = str(e)
        logger.error(f"search_news failed: {e}")

    return response
