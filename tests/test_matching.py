"""
Unit tests for Profile-Opportunity Matching engine.
"""

import pytest
from profile.models import UserProfile, Education
from analysis.opportunity import Opportunity
from profile.matcher import ProfileMatcher

def test_matching_high_skill_overlap():
    profile = UserProfile(
        name="Jane Developer",
        skills=["Python", "Streamlit", "PostgreSQL", "Git"],
        education=Education(degree="B.Tech CS", university="Delhi Tech University", year="2025")
    )
    
    opp = Opportunity(
        id="opp_101",
        title="Python Software Engineer Intern",
        company="TechCorp",
        required_skills=["Python", "Streamlit", "PostgreSQL"],
        preferred_skills=["Docker"]
    )
    
    matcher = ProfileMatcher()
    res = matcher.calculate_match(profile, opp)
    
    assert res.overall_score >= 50.0
    assert "Python" in res.matched_skills
    assert "Streamlit" in res.matched_skills
    assert len(res.explanation) > 0

def test_matching_zero_skills():
    profile = UserProfile(name="Novice", skills=[])
    opp = Opportunity(
        id="opp_102",
        title="Senior C++ Graphics Developer",
        company="GameStudio",
        required_skills=["C++", "OpenGL", "Vulkan"]
    )
    
    matcher = ProfileMatcher()
    res = matcher.calculate_match(profile, opp)
    
    assert res.overall_score < 60.0
    assert len(res.missing_skills) >= 2
