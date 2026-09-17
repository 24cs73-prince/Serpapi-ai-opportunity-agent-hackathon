"""
Unit tests for OpportunityIQ Scoring Engine.
"""

import pytest
from analysis.scoring import MatchScorer, ScoreBreakdown

def test_score_breakdown_total():
    breakdown = ScoreBreakdown(
        skill_score=80.0,
        experience_score=60.0,
        education_score=90.0,
        location_score=100.0,
        preference_score=70.0,
        total=78.0
    )
    total = breakdown.total_score()
    assert total == pytest.approx(78.0)

def test_score_explanation():
    breakdown = ScoreBreakdown(
        skill_score=100.0,
        experience_score=50.0,
        education_score=50.0,
        location_score=50.0,
        preference_score=50.0,
        total=75.0
    )
    expl = MatchScorer.explain_score(breakdown)
    assert "Overall Match Score: 75/100" in expl
