"""
OpportunityIQ — Skill Gap Analysis

Identifies skills the user needs to develop, prioritizes them
based on frequency across target opportunities, and suggests
preparation actions.
"""

from typing import Optional
from collections import Counter
from dataclasses import dataclass, field
from profile.models import UserProfile
from analysis.opportunity import Opportunity
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SkillGapItem:
    """A single skill gap with context."""
    skill: str
    priority: str  # "High", "Medium", "Low"
    frequency: int  # How many opportunities require it
    reason: str
    suggestion: str


@dataclass
class SkillGapReport:
    """Complete skill gap analysis report."""
    strong_skills: list[str] = field(default_factory=list)
    developing_skills: list[str] = field(default_factory=list)
    missing_skills: list[SkillGapItem] = field(default_factory=list)
    total_opportunities_analyzed: int = 0


def analyze_skill_gaps(
    profile: UserProfile,
    opportunities: list[Opportunity],
) -> SkillGapReport:
    """
    Analyze skill gaps across multiple opportunities.
    
    Identifies which skills the user has, which are developing,
    and which are missing — prioritized by frequency across opportunities.
    """
    user_skills = profile.all_technologies
    report = SkillGapReport(total_opportunities_analyzed=len(opportunities))
    
    # Count skill frequency across all opportunities
    required_counter = Counter()
    preferred_counter = Counter()
    
    for opp in opportunities:
        for skill in opp.required_skills:
            required_counter[skill.lower().strip()] += 1
        for skill in opp.preferred_skills:
            preferred_counter[skill.lower().strip()] += 1
    
    all_opp_skills = set(required_counter.keys()) | set(preferred_counter.keys())
    
    # Classify skills
    for skill_lower in all_opp_skills:
        # Find the best original-case version
        original = _find_original_case(skill_lower, opportunities)
        
        if skill_lower in user_skills:
            report.strong_skills.append(original)
        else:
            freq = required_counter.get(skill_lower, 0) + preferred_counter.get(skill_lower, 0)
            required_freq = required_counter.get(skill_lower, 0)
            
            # Determine priority
            if required_freq >= 3:
                priority = "High"
            elif required_freq >= 1 or freq >= 3:
                priority = "Medium"
            else:
                priority = "Low"
            
            # Generate reason
            if required_freq > 0:
                reason = f"Required by {required_freq} opportunit{'ies' if required_freq > 1 else 'y'}"
                if preferred_counter.get(skill_lower, 0) > 0:
                    reason += f", preferred by {preferred_counter[skill_lower]} more"
            else:
                reason = f"Preferred by {freq} opportunit{'ies' if freq > 1 else 'y'}"
            
            # Generate suggestion
            suggestion = _generate_suggestion(original, priority)
            
            report.missing_skills.append(SkillGapItem(
                skill=original,
                priority=priority,
                frequency=freq,
                reason=reason,
                suggestion=suggestion,
            ))
    
    # Sort: High priority first, then by frequency
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    report.missing_skills.sort(
        key=lambda x: (priority_order.get(x.priority, 3), -x.frequency)
    )
    
    # Sort strong skills by frequency (most relevant first)
    report.strong_skills.sort(
        key=lambda s: -(required_counter.get(s.lower(), 0) + preferred_counter.get(s.lower(), 0))
    )
    
    logger.info(
        f"Skill gap analysis: {len(report.strong_skills)} strong, "
        f"{len(report.missing_skills)} missing across {len(opportunities)} opportunities"
    )
    
    return report


def _find_original_case(skill_lower: str, opportunities: list[Opportunity]) -> str:
    """Find the best original-case version of a skill across opportunities."""
    for opp in opportunities:
        for s in opp.required_skills + opp.preferred_skills:
            if s.lower().strip() == skill_lower:
                return s
    return skill_lower.title()


def _generate_suggestion(skill: str, priority: str) -> str:
    """Generate a preparation suggestion for a missing skill."""
    suggestions = {
        "python": "Practice Python through coding challenges and small projects",
        "docker": "Learn Docker basics — build and containerize a simple application",
        "kubernetes": "Start with Docker first, then learn Kubernetes fundamentals",
        "aws": "Explore AWS Free Tier — set up EC2, S3, and Lambda",
        "azure": "Use Azure Free Account to practice cloud services",
        "gcp": "Start with Google Cloud Skills Boost free courses",
        "react": "Build a small interactive web app using React",
        "machine learning": "Complete a structured ML course and build 2-3 projects",
        "deep learning": "Learn PyTorch or TensorFlow through hands-on tutorials",
        "pytorch": "Follow official PyTorch tutorials and implement a neural network",
        "tensorflow": "Start with TensorFlow's beginner tutorials",
        "sql": "Practice SQL on LeetCode or HackerRank database challenges",
        "git": "Use Git daily for all your projects — learn branching and merging",
        "fastapi": "Build a REST API with FastAPI — it's beginner-friendly",
        "ci/cd": "Set up a GitHub Actions pipeline for one of your projects",
        "linux": "Use Linux (or WSL) for your development workflow",
        "nlp": "Study NLP fundamentals and build a text classification project",
        "langchain": "Build a simple RAG application using LangChain",
        "rag": "Implement a retrieval-augmented generation pipeline",
        "llm": "Experiment with LLM APIs and build a structured output pipeline",
    }
    
    skill_lower = skill.lower()
    if skill_lower in suggestions:
        return suggestions[skill_lower]
    
    if priority == "High":
        return f"Learn {skill} fundamentals — this is frequently required in your target roles"
    elif priority == "Medium":
        return f"Consider learning {skill} to strengthen your profile"
    else:
        return f"Explore {skill} when time permits"
