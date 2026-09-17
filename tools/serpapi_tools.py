"""
OpportunityIQ — SerpApi Tools

Low-level wrapper around the current SerpApi Python client.
Handles connection, error management, and result normalization.
Never exposes API keys in logs or outputs.
"""

from typing import Optional
import serpapi

from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


KNOWN_LOCATIONS = [
    "gujarat", "bengaluru", "bangalore", "mumbai", "delhi", "noida", "gurgaon",
    "pune", "hyderabad", "chennai", "kolkata", "ahmedabad", "jaipur", "remote", "india"
]


def _should_include_location(query: str, location: Optional[str]) -> bool:
    """
    Determine if a separate location parameter should be passed to SerpApi.
    Prevents passing generic 'India' when the query string already specifies a location.
    """
    if not location or not location.strip():
        return False

    q_lower = query.lower()
    loc_lower = location.strip().lower()

    # If location string is already contained inside the query text
    if loc_lower in q_lower:
        return False

    # If location is generic 'india' and query specifies a more specific city/state
    if loc_lower == "india":
        if any(loc in q_lower for loc in KNOWN_LOCATIONS if loc != "india"):
            return False

    return True


class SerpApiError(Exception):
    """Raised when a SerpApi request fails."""
    pass


class SerpApiClient:
    """
    Wrapper around SerpApi for structured, safe search calls.

    Uses the current SerpApi Python SDK:
        serpapi.Client(...)

    Validates configuration before making requests.
    Handles errors gracefully and never logs the API key.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.serpapi.api_key

        if not self.api_key:
            logger.warning("SerpApi API key not configured")

        self.client = (
            serpapi.Client(api_key=self.api_key)
            if self.api_key
            else None
        )

    @property
    def is_configured(self) -> bool:
        """Return True when a SerpApi API key is available."""
        return bool(self.api_key)

    def _execute_search(self, params: dict) -> dict:
        """
        Execute a SerpApi search with timeout control.

        Raises:
            SerpApiError: If configuration, request, or API response fails.
        """
        if not self.is_configured or self.client is None:
            raise SerpApiError(
                "SerpApi API key is not configured. "
                "Add SERPAPI_API_KEY to your .env file."
            )

        try:
            # Do NOT add api_key to params.
            # The current serpapi.Client manages authentication.
            results = self.client.search(
                params,
                timeout=25,
            )

            if not isinstance(results, dict):
                results = dict(results)

            if "error" in results:
                error_msg = results["error"]
                logger.error(f"SerpApi error: {error_msg}")
                raise SerpApiError(f"SerpApi returned an error: {error_msg}")

            return results

        except SerpApiError:
            raise

        except Exception as e:
            logger.error(f"SerpApi request failed: {type(e).__name__}: {e}")
            raise SerpApiError(f"Search request failed: {e}") from e

    def search_google_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        chips: Optional[str] = None,
        num: int = 10,
    ) -> dict:
        """Search Google Jobs via SerpApi."""
        params = {
            "engine": "google_jobs",
            "q": query,
        }

        if _should_include_location(query, location):
            params["location"] = location

        if chips:
            params["chips"] = chips

        logger.info(f"Google Jobs search: query='{query}', location='{params.get('location', 'any')}'")
        results = self._execute_search(params)
        job_count = len(results.get("jobs_results", []))
        logger.info(f"Google Jobs search complete: {job_count} results")
        return results

    def search_google(
        self,
        query: str,
        location: Optional[str] = None,
        num: int = 10,
    ) -> dict:
        """Search Google web results via SerpApi."""
        params = {
            "engine": "google",
            "q": query,
            "num": num,
        }

        if _should_include_location(query, location):
            params["location"] = location

        logger.info(f"Google Search: query='{query}', num={num}")
        results = self._execute_search(params)
        result_count = len(results.get("organic_results", []))
        logger.info(f"Google Search complete: {result_count} organic results")
        return results

    def search_google_news(
        self,
        query: str,
        location: Optional[str] = None,
    ) -> dict:
        """Search Google News via SerpApi."""
        params = {
            "engine": "google",
            "q": query,
            "tbm": "nws",
        }

        if _should_include_location(query, location):
            params["location"] = location

        logger.info(f"Google News search: query='{query}'")
        results = self._execute_search(params)
        news_count = len(results.get("news_results", []))
        logger.info(f"Google News search complete: {news_count} results")
        return results

    def validate_connection(self) -> tuple[bool, str]:
        """
        Test the SerpApi connection with a minimal query.

        Returns:
            (success, message)
        """
        if not self.is_configured:
            return False, "API key not configured"

        try:
            results = self.search_google("test", num=1)
            if "search_metadata" in results:
                return True, "Connected successfully"
            return False, "Unexpected response format"
        except SerpApiError as e:
            return False, str(e)