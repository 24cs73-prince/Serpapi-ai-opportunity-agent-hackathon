"""
OpportunityIQ — Agent State Models

Defines the state container for the LangGraph / Agent Orchestrator.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from analysis.opportunity import Opportunity
from profile.models import UserProfile
from profile.matcher import MatchResult
from analysis.skill_gap import SkillGapReport

class SearchPlan(BaseModel):
    queries: List[str] = Field(default_factory=list)
    search_types: List[str] = Field(default_factory=list, description="['jobs', 'web', 'news']")
    reasoning: str = ""

class AgentState(BaseModel):
    user_query: str = ""
    target_role: Optional[str] = None
    target_location: Optional[str] = None
    profile: Optional[UserProfile] = None
    
    # State tracking
    search_plan: Optional[SearchPlan] = None
    raw_results: List[Dict[str, Any]] = Field(default_factory=list)
    structured_opportunities: List[Opportunity] = Field(default_factory=list)
    match_results: Dict[str, MatchResult] = Field(default_factory=dict)
    skill_gap_report: Optional[SkillGapReport] = None
    
    # Output & Progress
    final_summary: str = ""
    logs: List[str] = Field(default_factory=list)
    current_step: str = "initialized"
