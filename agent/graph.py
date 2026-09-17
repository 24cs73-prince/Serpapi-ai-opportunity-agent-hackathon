"""
OpportunityIQ — Agent Workflow Graph

Orchestrates the autonomous agent workflow:
Plan → Search → Extract → Match → Skill Gap Analysis → Rank → Executive Summary
"""

from typing import Optional, Callable
import logging
from agent.state import AgentState, SearchPlan
from agent.planner import SearchPlanner
from tools.search_tools import search_jobs, search_web
from tools.extraction_tools import extract_opportunities_from_search
from profile.models import UserProfile
from profile.matcher import ProfileMatcher
from analysis.skill_gap import SkillGapAnalyzer
from analysis.ranking import OpportunityRanker
from config import get_config

logger = logging.getLogger(__name__)

class AgentWorkflow:
    """Agent workflow orchestrator."""

    def __init__(self):
        self.planner = SearchPlanner()
        self.matcher = ProfileMatcher()
        self.gap_analyzer = SkillGapAnalyzer()
        self.ranker = OpportunityRanker()

    def run(self, state: AgentState, status_callback: Optional[Callable[[str], None]] = None) -> AgentState:
        """Executes the full agent workflow sequentially."""
        def log(msg: str):
            state.logs.append(msg)
            logger.info(msg)
            if status_callback:
                status_callback(msg)

        log("🚀 Launching OpportunityIQ AI Agent...")

        # Step 1: Plan Search
        state.current_step = "planning"
        log("📋 Generating intelligent search plan...")
        state.search_plan = self.planner.plan_search(state.user_query, state.target_location)
        log(f"Plan created: {len(state.search_plan.queries)} queries planned ({', '.join(state.search_plan.search_types)})")

        # Step 2: Execute Search via SerpApi
        state.current_step = "searching"
        log("🔍 Executing live SerpApi search queries...")
        raw_items = []
        executed_queries = set()

        for q in state.search_plan.queries:
            q_norm = " ".join(q.lower().split())
            if q_norm in executed_queries:
                continue
            executed_queries.add(q_norm)

            if "jobs" in state.search_plan.search_types:
                job_res = search_jobs(query=q, location=state.target_location)
                if job_res.results:
                    raw_items.extend(job_res.results)

            if "web" in state.search_plan.search_types and len(raw_items) < 5:
                web_res = search_web(query=q, location=state.target_location)
                if web_res.results:
                    raw_items.extend(web_res.results)

        state.raw_results = raw_items
        log(f"Search complete: {len(raw_items)} raw results retrieved from SerpApi.")

        # Step 3: Extract & Normalize Opportunities
        state.current_step = "extracting"
        log("⚡ Structuring and normalizing opportunities into Pydantic models...")
        state.structured_opportunities = extract_opportunities_from_search(raw_items)
        log(f"Normalized {len(state.structured_opportunities)} structured opportunity records.")

        # Step 4: Profile Match & Scoring
        if state.profile:
            state.current_step = "matching"
            log("🎯 Computing weighted profile compatibility scores...")
            for opp in state.structured_opportunities:
                match_res = self.matcher.calculate_match(state.profile, opp)
                state.match_results[opp.id] = match_res

            log("Rank-ordering opportunities based on composite match & verified trust factors...")
            state.structured_opportunities = self.ranker.rank(state.structured_opportunities, state.match_results)

            # Step 5: Skill Gap Analysis
            state.current_step = "skill_gap"
            log("💡 Analyzing skill gaps and generating actionable prep recommendations...")
            state.skill_gap_report = self.gap_analyzer.analyze(state.profile, state.structured_opportunities)

        # Step 6: Generate Executive Summary
        state.current_step = "summarizing"
        log("📊 Generating executive career intelligence summary...")
        top_count = len(state.structured_opportunities)
        state.final_summary = f"Identified **{top_count} verified opportunities** matching your request for '{state.user_query}'."

        state.current_step = "completed"
        log("✅ OpportunityIQ Agent workflow completed successfully!")

        return state
