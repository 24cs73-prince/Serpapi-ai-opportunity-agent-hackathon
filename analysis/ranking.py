"""
OpportunityIQ — Multi-Factor Opportunity Ranking

Ranks opportunities based on match score, urgency, verified status, and query relevance.
"""

from typing import List, Dict, Any, Optional
from analysis.opportunity import Opportunity
from profile.matcher import MatchResult

class OpportunityRanker:
    """Ranks opportunities using multi-factor scoring."""

    @staticmethod
    def rank(opportunities: List[Opportunity], match_results: Dict[str, MatchResult]) -> List[Opportunity]:
        """Sorts opportunities by composite ranking score."""
        def calculate_rank_score(opp: Opportunity) -> float:
            match_res = match_results.get(opp.id)
            match_score = match_res.overall_score if match_res else 50.0

            # Verified boost
            verified_boost = 10.0 if opp.verified else 0.0

            # Direct apply link boost
            link_boost = 5.0 if opp.apply_link else 0.0

            # Composite ranking score
            rank_score = (match_score * 0.8) + verified_boost + link_boost
            return rank_score

        return sorted(opportunities, key=calculate_rank_score, reverse=True)
