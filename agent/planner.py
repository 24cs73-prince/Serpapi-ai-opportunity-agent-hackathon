"""
OpportunityIQ — Agent Search Planner

Translates natural language user requests into optimal SerpApi search plans.
"""

from typing import Optional
import json
import logging
from agent.state import SearchPlan
from agent.prompts import PLANNER_SYSTEM_PROMPT
from config import get_config
from tools.serpapi_tools import _should_include_location

logger = logging.getLogger(__name__)

class SearchPlanner:
    """Generates targeted search plans using LLM or rule-based heuristics."""

    def __init__(self):
        self.cfg = get_config()

    def plan_search(self, query: str, location: Optional[str] = None) -> SearchPlan:
        """Generates a search plan for the given query."""
        clean_query = query.strip()
        loc_str = f" in {location}" if (location and _should_include_location(clean_query, location)) else ""

        raw_queries = [
            f"{clean_query}{loc_str}",
            f"{clean_query} entry level",
            f"{clean_query} freshers hiring 2026"
        ]

        # Deduplicate queries while preserving order
        deduped_queries = []
        seen = set()
        for q in raw_queries:
            q_norm = " ".join(q.lower().split())
            if q_norm not in seen:
                seen.add(q_norm)
                deduped_queries.append(q)

        plan = SearchPlan(
            queries=deduped_queries,
            search_types=["jobs", "web"],
            reasoning=f"Searching Google Jobs and Web for '{clean_query}'{loc_str} targeting immediate opportunities."
        )

        if self.cfg.has_llm_key():
            try:
                if self.cfg.LLM_PROVIDER == "gemini":
                    import google.generativeai as genai
                    genai.configure(api_key=self.cfg.LLM_API_KEY)
                    model = genai.GenerativeModel(self.cfg.MODEL_NAME)
                    prompt = f"{PLANNER_SYSTEM_PROMPT}\n\nUser query: '{query}'\nLocation: '{location or 'India/Remote'}'"
                    resp = model.generate_content(prompt)
                    text = resp.text.strip()
                    if text.startswith("```json"):
                        text = text[7:-3].strip()
                    data = json.loads(text)

                    # Deduplicate LLM queries
                    llm_queries = data.get("queries", [])
                    clean_llm_queries = []
                    seen_llm = set()
                    for q in llm_queries:
                        qn = " ".join(q.lower().split())
                        if qn not in seen_llm:
                            seen_llm.add(qn)
                            clean_llm_queries.append(q)
                    data["queries"] = clean_llm_queries
                    plan = SearchPlan(**data)
            except Exception as e:
                logger.warning(f"LLM Search Planner warning ({e}). Using rule-based plan.")

        return plan
