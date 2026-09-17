"""
OpportunityIQ — Profile-Opportunity Matcher

Transparent, weighted matching between user profile and opportunities.
Documents how scores are calculated — never produces unexplained scores.

Weights (configurable):
  Skills:      50%
  Experience:  20%
  Education:   10%
  Location:    10%
  Preferences: 10%
"""

from typing import Optional
from analysis.opportunity import Opportunity
from profile.models import UserProfile
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


from dataclasses import dataclass, field

@dataclass
class MatchResult:
    """Result of matching an opportunity against a user profile."""
    score: float
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    skill_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    location_score: float = 0.0
    preference_score: float = 0.0
    explanation: str = ""

    @property
    def overall_score(self) -> float:
        return self.score * 100.0 if self.score <= 1.0 else self.score

    @property
    def score_percent(self) -> int:
        return int(self.score * 100) if self.score <= 1.0 else int(self.score)

    @property
    def tier(self) -> str:
        if self.score >= 0.75:
            return "high"
        if self.score >= 0.50:
            return "medium"
        return "low"


class ProfileMatcher:
    """Class wrapper for profile matching."""

    def calculate_match(self, profile: UserProfile, opportunity: Opportunity, weights: Optional[dict] = None) -> MatchResult:
        return match_opportunity(profile, opportunity, weights)



def match_opportunity(
    profile: UserProfile,
    opportunity: Opportunity,
    weights: Optional[dict] = None,
) -> MatchResult:
    """
    Match a user profile against an opportunity.
    
    Returns a transparent MatchResult with component scores.
    
    Args:
        profile: User profile.
        opportunity: Opportunity to match against.
        weights: Optional weight overrides (keys: skills, experience, education, location, preferences).
    """
    w = weights or {
        "skills": config.match_weight_skills,
        "experience": config.match_weight_experience,
        "education": config.match_weight_education,
        "location": config.match_weight_location,
        "preferences": config.match_weight_preferences,
    }

    # 1. Skills matching (50%)
    skill_score, matched, missing = _match_skills(profile, opportunity)

    # 2. Experience matching (20%)
    experience_score = _match_experience(profile, opportunity)

    # 3. Education matching (10%)
    education_score = _match_education(profile, opportunity)

    # 4. Location matching (10%)
    location_score = _match_location(profile, opportunity)

    # 5. Preference matching (10%)
    preference_score = _match_preferences(profile, opportunity)

    # Weighted total
    total = (
        skill_score * w["skills"]
        + experience_score * w["experience"]
        + education_score * w["education"]
        + location_score * w["location"]
        + preference_score * w["preferences"]
    )

    # Generate explanation
    explanation = _generate_explanation(
        profile, opportunity, total,
        matched, missing,
        skill_score, experience_score,
        education_score, location_score, preference_score,
    )

    return MatchResult(
        score=round(total, 3),
        matched_skills=matched,
        missing_skills=missing,
        skill_score=round(skill_score, 3),
        experience_score=round(experience_score, 3),
        education_score=round(education_score, 3),
        location_score=round(location_score, 3),
        preference_score=round(preference_score, 3),
        explanation=explanation,
    )


def match_opportunities(
    profile: UserProfile,
    opportunities: list[Opportunity],
    weights: Optional[dict] = None,
) -> list[tuple[Opportunity, MatchResult]]:
    """
    Match a profile against multiple opportunities and sort by score.
    
    Returns list of (opportunity, match_result) tuples, highest score first.
    """
    results = []
    for opp in opportunities:
        match = match_opportunity(profile, opp, weights)
        # Update the opportunity with match data
        opp.match_score = match.score
        opp.matched_skills = match.matched_skills
        opp.missing_skills = match.missing_skills
        opp.explanation = match.explanation
        results.append((opp, match))
    
    # Sort by score descending
    results.sort(key=lambda x: x[1].score, reverse=True)
    logger.info(f"Matched {len(results)} opportunities against profile")
    return results


# ── Component Matchers ──

def _match_skills(profile: UserProfile, opportunity: Opportunity) -> tuple[float, list[str], list[str]]:
    """
    Match profile skills against opportunity requirements.
    
    Returns (score, matched_skills, missing_skills).
    """
    user_skills = profile.all_technologies
    
    # Combine required and preferred skills
    required = {s.lower().strip() for s in opportunity.required_skills}
    preferred = {s.lower().strip() for s in opportunity.preferred_skills}
    all_opp_skills = required | preferred
    
    if not all_opp_skills:
        # No skills listed — partial match based on profile having skills
        return (0.5 if user_skills else 0.3), [], []
    
    matched = []
    missing = []
    
    for skill in all_opp_skills:
        if skill in user_skills:
            # Find original case
            original = next(
                (s for s in opportunity.required_skills + opportunity.preferred_skills
                 if s.lower().strip() == skill),
                skill,
            )
            matched.append(original)
        else:
            original = next(
                (s for s in opportunity.required_skills + opportunity.preferred_skills
                 if s.lower().strip() == skill),
                skill,
            )
            missing.append(original)
    
    # Weight required skills higher
    total_weight = 0
    matched_weight = 0
    
    for skill in required:
        total_weight += 2  # Required skills count double
        if skill in user_skills:
            matched_weight += 2
    
    for skill in preferred:
        total_weight += 1
        if skill in user_skills:
            matched_weight += 1
    
    score = matched_weight / total_weight if total_weight > 0 else 0.5
    return score, matched, missing


def _match_experience(profile: UserProfile, opportunity: Opportunity) -> float:
    """Match experience level."""
    exp_required = (opportunity.experience_required or "").lower()
    
    if not exp_required or "not specified" in exp_required:
        return 0.7  # No requirement = moderate match
    
    user_years = profile.experience_years
    
    if any(term in exp_required for term in ["entry", "fresher", "0", "student", "intern"]):
        return 1.0 if user_years <= 2 else 0.6
    
    if any(term in exp_required for term in ["1-2", "1-3", "junior"]):
        if user_years >= 1:
            return 0.9
        return 0.5
    
    if any(term in exp_required for term in ["3-5", "mid", "senior"]):
        if user_years >= 3:
            return 0.8
        return 0.3
    
    return 0.5  # Can't determine


def _match_education(profile: UserProfile, opportunity: Opportunity) -> float:
    """Match education level."""
    if not profile.education or not profile.education.degree:
        return 0.5
    
    degree = profile.education.degree.lower()
    
    # Most tech opportunities require at least a bachelor's
    if any(term in degree for term in ["b.tech", "btech", "b.e", "bachelor", "bs", "b.sc"]):
        return 0.8
    if any(term in degree for term in ["m.tech", "mtech", "master", "ms", "m.sc", "mba"]):
        return 0.9
    if "phd" in degree or "doctorate" in degree:
        return 1.0
    
    return 0.5


def _match_location(profile: UserProfile, opportunity: Opportunity) -> float:
    """Match location preferences."""
    opp_location = (opportunity.location or "").lower()
    opp_mode = (opportunity.work_mode or "").lower()
    
    # Remote is always a good match
    if "remote" in opp_mode or "remote" in opp_location:
        if profile.remote_preference in ["Remote", "Any", None]:
            return 1.0
        return 0.7
    
    if not opp_location or not profile.location:
        return 0.5
    
    user_loc = profile.location.lower()
    preferred = [loc.lower() for loc in profile.preferred_locations]
    
    # Check if opportunity location matches user location or preferences
    if any(loc in opp_location for loc in [user_loc] + preferred):
        return 1.0
    if any(opp_loc_part in user_loc for opp_loc_part in opp_location.split(",")):
        return 0.8
    
    return 0.3


def _match_preferences(profile: UserProfile, opportunity: Opportunity) -> float:
    """Match opportunity type and domain preferences."""
    score = 0.5
    
    # Opportunity type
    opp_type = (opportunity.opportunity_type or "").lower()
    if profile.opportunity_types:
        user_types = [t.lower() for t in profile.opportunity_types]
        if any(ut in opp_type for ut in user_types):
            score += 0.25
    
    # Domain matching (check if opportunity title/description matches preferred domains)
    if profile.preferred_domains and opportunity.title:
        title_lower = opportunity.title.lower()
        desc_lower = (opportunity.description or "").lower()
        for domain in profile.preferred_domains:
            domain_lower = domain.lower()
            if domain_lower in title_lower or domain_lower in desc_lower:
                score += 0.25
                break
    
    return min(score, 1.0)


def _generate_explanation(
    profile: UserProfile,
    opportunity: Opportunity,
    total_score: float,
    matched: list[str],
    missing: list[str],
    skill_score: float,
    experience_score: float,
    education_score: float,
    location_score: float,
    preference_score: float,
) -> str:
    """Generate a human-readable explanation of the match."""
    parts = []
    
    score_pct = int(total_score * 100)
    
    if score_pct >= 75:
        parts.append(f"Strong match ({score_pct}%) — this opportunity aligns well with your profile.")
    elif score_pct >= 50:
        parts.append(f"Moderate match ({score_pct}%) — this opportunity partially matches your profile.")
    else:
        parts.append(f"Low match ({score_pct}%) — this opportunity may require significant skill development.")
    
    if matched:
        parts.append(f"You already have: {', '.join(matched[:5])}.")
    
    if missing:
        parts.append(f"You may need to develop: {', '.join(missing[:5])}.")
    
    if skill_score >= 0.8:
        parts.append("Your technical skills are a strong fit.")
    elif skill_score < 0.4:
        parts.append("There is a notable skill gap for this role.")
    
    if location_score >= 0.8:
        parts.append("The location aligns with your preferences.")
    elif location_score < 0.4:
        parts.append("The location may not match your preference.")
    
    return " ".join(parts)
