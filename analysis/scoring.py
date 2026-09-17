"""
OpportunityIQ — Scoring Engine

Provides documented, transparent scoring for opportunity matching.
This module defines the scoring logic used by the matching engine.
"""

from dataclasses import dataclass


@dataclass
class ScoreBreakdown:
    """
    Transparent breakdown of how a match score was calculated.
    
    Score Formula:
        total = (skill_score × 0.50) + (experience_score × 0.20) +
                (education_score × 0.10) + (location_score × 0.10) +
                (preference_score × 0.10)
    
    Each component score is 0.0 to 1.0.
    The total is a profile-to-opportunity similarity indicator,
    NOT a hiring probability prediction.
    """
    skill_score: float
    experience_score: float
    education_score: float
    location_score: float
    preference_score: float
    total: float
    
    # Weights used
    skill_weight: float = 0.50
    experience_weight: float = 0.20
    education_weight: float = 0.10
    location_weight: float = 0.10
    preference_weight: float = 0.10
    
    def total_score(self) -> float:
        return (
            (self.skill_score * self.skill_weight) +
            (self.experience_score * self.experience_weight) +
            (self.education_score * self.education_weight) +
            (self.location_score * self.location_weight) +
            (self.preference_score * self.preference_weight)
        )

    def to_dict(self) -> dict:
        return {
            "total": round(self.total * 100),
            "components": {
                "skills": {"score": round(self.skill_score * 100), "weight": f"{int(self.skill_weight * 100)}%"},
                "experience": {"score": round(self.experience_score * 100), "weight": f"{int(self.experience_weight * 100)}%"},
                "education": {"score": round(self.education_score * 100), "weight": f"{int(self.education_weight * 100)}%"},
                "location": {"score": round(self.location_score * 100), "weight": f"{int(self.location_weight * 100)}%"},
                "preferences": {"score": round(self.preference_score * 100), "weight": f"{int(self.preference_weight * 100)}%"},
            },
            "note": "Score is a profile-to-opportunity similarity indicator, not a hiring probability."
        }


class MatchScorer:
    """Scoring engine wrapper."""
    
    @classmethod
    def explain_score(cls, breakdown: ScoreBreakdown) -> str:
        score_val = int(breakdown.total_score())
        return f"Overall Match Score: {score_val}/100. Component breakdown: Skills {int(breakdown.skill_score)}%, Experience {int(breakdown.experience_score)}%."

