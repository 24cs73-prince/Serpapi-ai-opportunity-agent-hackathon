"""
OpportunityIQ — Opportunity Data Model

Pydantic models for structured opportunity data.
All fields use Optional types — never fabricate unavailable data.
"""

import uuid
from typing import Optional
from pydantic import BaseModel, Field


class Opportunity(BaseModel):
    """
    Structured representation of a career opportunity.

    All optional fields default to None — we never fabricate data.
    If information cannot be found in search results, it stays None
    and the UI displays "Not found in available sources."
    """

    # Core identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    company: Optional[str] = None
    description: Optional[str] = None

    # Location & mode
    location: Optional[str] = None
    work_mode: Optional[str] = None  # Remote / Hybrid / On-site

    # Type & level
    opportunity_type: Optional[str] = None  # Internship / Full-time / Part-time
    experience_required: Optional[str] = None

    # Compensation
    salary: Optional[str] = None
    stipend: Optional[str] = None

    # Requirements
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    eligibility: Optional[str] = None

    # Dates
    deadline: Optional[str] = None
    published_date: Optional[str] = None

    # Source tracking
    source: Optional[str] = None
    source_url: Optional[str] = None
    application_url: Optional[str] = None

    # Matching (populated by matching engine)
    match_score: Optional[float] = None  # 0.0 - 1.0
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    explanation: Optional[str] = None

    # Internal
    search_confidence: Optional[str] = None  # high / medium / low
    raw_extensions: list[str] = Field(default_factory=list)

    @property
    def apply_link(self) -> Optional[str]:
        """Alias for canonical application_url field."""
        return self.application_url

    @property
    def salary_or_stipend(self) -> Optional[str]:
        """Return salary or stipend if available."""
        if self.salary:
            return self.salary
        if self.stipend:
            return self.stipend
        return None

    @property
    def verified(self) -> bool:
        """Return True if application URL or source is verified."""
        return bool(self.application_url or self.source)

    def display_salary(self) -> str:
        """Return salary/stipend for display, or explicit unavailable message."""
        if self.salary:
            return self.salary
        if self.stipend:
            return self.stipend
        return "Not found in available sources"

    def display_field(self, value: Optional[str], fallback: str = "Not found in available sources") -> str:
        """Display a field value or a fallback message."""
        return value if value else fallback

    def match_tier(self) -> str:
        """Return match tier based on score."""
        if self.match_score is None:
            return "unscored"
        if self.match_score >= 0.75:
            return "high"
        if self.match_score >= 0.50:
            return "medium"
        return "low"
