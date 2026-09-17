"""
OpportunityIQ — Profile Models

Pydantic models for user profiles.
Supports both resume-parsed and manually-entered profiles.
"""

from typing import Optional
from pydantic import BaseModel, Field


class Education(BaseModel):
    """User's educational background."""
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    university: Optional[str] = None
    year: Optional[str] = None  # "1st Year", "2nd Year", etc.
    expected_graduation: Optional[str] = None


class Experience(BaseModel):
    """A single experience entry."""
    title: Optional[str] = None
    organization: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None


class Project(BaseModel):
    """A single project entry."""
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    """
    Complete user profile for matching.
    
    Can be populated from resume parsing or manual entry.
    """
    name: Optional[str] = None
    
    # Education
    education: Optional[Education] = None
    
    # Location
    location: Optional[str] = None
    preferred_locations: list[str] = Field(default_factory=list)
    
    # Experience
    experience_years: int = 0
    experiences: list[Experience] = Field(default_factory=list)
    
    # Skills — the core matching input
    skills: list[str] = Field(default_factory=list)
    
    # Projects
    projects: list[Project] = Field(default_factory=list)
    
    # Certifications
    certifications: list[str] = Field(default_factory=list)
    
    # Preferences
    preferred_domains: list[str] = Field(default_factory=list)
    opportunity_types: list[str] = Field(default_factory=list)  # Internship, Job, etc.
    remote_preference: Optional[str] = None  # Remote, Hybrid, On-site, Any

    @property
    def skills_lower(self) -> set[str]:
        """Return skills as a lowercase set for matching."""
        return {s.lower().strip() for s in self.skills if s.strip()}

    @property
    def all_technologies(self) -> set[str]:
        """Return all technologies from skills and projects."""
        techs = set(self.skills)
        for project in self.projects:
            techs.update(project.technologies)
        return {t.lower().strip() for t in techs if t.strip()}

    def completeness_score(self) -> int:
        """Calculate profile completeness as a percentage."""
        fields = {
            "name": bool(self.name),
            "education": self.education is not None and bool(self.education.degree),
            "skills": len(self.skills) > 0,
            "location": bool(self.location),
            "experience": len(self.experiences) > 0 or self.experience_years > 0,
            "projects": len(self.projects) > 0,
            "certifications": len(self.certifications) > 0,
            "preferences": len(self.preferred_domains) > 0,
        }
        filled = sum(1 for v in fields.values() if v)
        return int((filled / len(fields)) * 100)
    
    def to_text(self) -> str:
        """Convert profile to text for embedding/RAG."""
        parts = []
        if self.name:
            parts.append(f"Name: {self.name}")
        if self.education:
            edu_parts = []
            if self.education.degree:
                edu_parts.append(self.education.degree)
            if self.education.field_of_study:
                edu_parts.append(self.education.field_of_study)
            if self.education.university:
                edu_parts.append(f"at {self.education.university}")
            if self.education.year:
                edu_parts.append(f"({self.education.year})")
            parts.append("Education: " + " ".join(edu_parts))
        if self.location:
            parts.append(f"Location: {self.location}")
        if self.skills:
            parts.append(f"Skills: {', '.join(self.skills)}")
        if self.experiences:
            for exp in self.experiences:
                exp_text = f"Experience: {exp.title or ''} at {exp.organization or ''}"
                if exp.description:
                    exp_text += f" — {exp.description}"
                parts.append(exp_text)
        if self.projects:
            for proj in self.projects:
                proj_text = f"Project: {proj.name or ''}"
                if proj.description:
                    proj_text += f" — {proj.description}"
                if proj.technologies:
                    proj_text += f" (Tech: {', '.join(proj.technologies)})"
                parts.append(proj_text)
        if self.certifications:
            parts.append(f"Certifications: {', '.join(self.certifications)}")
        if self.preferred_domains:
            parts.append(f"Preferred domains: {', '.join(self.preferred_domains)}")
        return "\n".join(parts)

    def to_text_summary(self) -> str:
        """Alias for to_text."""
        return self.to_text()

