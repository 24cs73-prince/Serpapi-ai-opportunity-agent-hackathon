"""
Unit tests for OpportunityIQ Profile Models and Parsing logic.
"""

import pytest
from profile.models import UserProfile, Education, Experience, Project

def test_profile_completeness_empty():
    profile = UserProfile(name="")
    assert profile.completeness_score() == 0

def test_profile_completeness_partial():
    profile = UserProfile(
        name="Alex Dev",
        skills=["Python", "FastAPI"]
    )
    score = profile.completeness_score()
    assert 20 <= score <= 60

def test_profile_completeness_full():
    profile = UserProfile(
        name="Alex Dev",
        skills=["Python", "PyTorch", "Streamlit"],
        education=Education(degree="B.Tech CS", university="IIT Madras", year="2025"),
        experiences=[Experience(title="ML Intern", organization="AI Corp")],
        projects=[Project(name="AI Agent", description="Built career agent")]
    )
    assert profile.completeness_score() >= 60

def test_text_summary_contains_skills():
    profile = UserProfile(
        name="Sam Tech",
        skills=["React", "TypeScript", "Python"]
    )
    summary = profile.to_text_summary()
    assert "Python" in summary
    assert "React" in summary
