"""
OpportunityIQ — SerpApi Tools

Low-level wrapper around the SerpApi Python client.
Handles connection, error management, and result normalization.
Never exposes API keys in logs or outputs.
"""

from typing import Any, Optional
from serpapi import GoogleSearch
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class SerpApiError(Exception):
    """Raised when a SerpApi request fails."""
    pass


class SerpApiClient:
    """
    Wrapper around SerpApi for structured, safe search calls.
    
    Validates configuration before making requests.
    Handles errors gracefully — never crashes the application.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.serpapi.api_key
        if not self.api_key:
            logger.warning("SerpApi API key not configured")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _execute_search(self, params: dict) -> dict:
        """
        Execute a SerpApi search with the given parameters.
        
        Raises SerpApiError on failure.
        """
        if not self.is_configured:
            raise SerpApiError("SerpApi API key is not configured. Add SERPAPI_API_KEY to your .env file.")

        params["api_key"] = self.api_key

        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            # Check for API errors
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
        """
        Search Google Jobs via SerpApi.
        
        Args:
            query: Job search query (e.g., "AI/ML internship").
            location: Location filter (e.g., "Gujarat, India").
            chips: Additional filter chips (e.g., "date_posted:week").
            num: Number of results to request.
        
        Returns:
            Raw SerpApi response dict.
        """
        params = {
            "engine": "google_jobs",
            "q": query,
        }
        if location:
            params["location"] = location
        if chips:
            params["chips"] = chips

        logger.info(f"Google Jobs search: query='{query}', location='{location or 'any'}'")
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
        """
        Search Google web results via SerpApi.
        
        Args:
            query: Search query string.
            location: Location for localized results.
            num: Number of results.
        
        Returns:
            Raw SerpApi response dict.
        """
        params = {
            "engine": "google",
            "q": query,
            "num": num,
        }
        if location:
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
        """
        Search Google News via SerpApi.
        
        Args:
            query: News search query.
            location: Location for localized results.
        
        Returns:
            Raw SerpApi response dict.
        """
        params = {
            "engine": "google",
            "q": query,
            "tbm": "nws",
        }
        if location:
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
