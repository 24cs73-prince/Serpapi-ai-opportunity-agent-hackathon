"""
Unit tests for Search & SerpApi wrapper error handling.
"""

import pytest
from tools.serpapi_tools import SerpApiClient, _should_include_location
from tools.search_tools import search_jobs, SearchResponse, JobResult, WebResult

def test_serpapi_client_initialization():
    client = SerpApiClient(api_key="dummy_key_123")
    assert client.api_key == "dummy_key_123"

def test_search_jobs_handles_empty_query():
    res = search_jobs(query="", location="India")
    assert res.query == ""
    assert res.search_type == "google_jobs"

def test_search_response_results_property():
    resp = SearchResponse(jobs=[JobResult(title="Test Job")])
    assert len(resp.results) == 1
    assert resp.results[0].title == "Test Job"

    web_resp = SearchResponse(web_results=[WebResult(title="Test Web")])
    assert len(web_resp.results) == 1
    assert web_resp.results[0].title == "Test Web"

def test_should_include_location():
    # Location inside query -> False
    assert _should_include_location("AI ML internships Gujarat", "Gujarat") is False
    # Generic India when specific city/state is in query -> False
    assert _should_include_location("AI ML internships Gujarat", "India") is False
    # Unique location not in query -> True
    assert _should_include_location("Python Developer", "Bengaluru") is True
