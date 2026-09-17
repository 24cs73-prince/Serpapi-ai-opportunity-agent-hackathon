"""
Unit tests for Search & SerpApi wrapper error handling.
"""

import pytest
from tools.serpapi_tools import SerpApiClient
from tools.search_tools import search_jobs

def test_serpapi_client_initialization():
    client = SerpApiClient(api_key="dummy_key_123")
    assert client.api_key == "dummy_key_123"

def test_search_jobs_handles_empty_query():
    res = search_jobs(query="", location="India")
    assert res.query == ""
    assert res.search_type == "google_jobs"
