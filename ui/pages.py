"""
OpportunityIQ — Master UI Page Renderers

Renders all pages of the Streamlit application:
- Dashboard
- Find Opportunities (Live SerpApi + AI Agent Workflow)
- My Profile (Resume Upload + Manual Profile Editor + RAG status)
- Saved Opportunities
- Skill Gap Analysis
- Search History
- Settings
"""

import streamlit as st
import time
import json
import html
import textwrap
from typing import Optional, List

from ui.components import (
    render_header, render_metric_card, render_opportunity_card,
    render_opportunity_detail_modal, render_skill_badges,
    render_empty_state, render_section_title
)
from profile.models import UserProfile, Education, Experience, Project
from profile.parser import parse_resume_file
from profile.matcher import match_opportunity
from analysis.opportunity import Opportunity
from analysis.skill_gap import SkillGapAnalyzer
from tools.search_tools import search_jobs, search_web, search_news
from tools.extraction_tools import extract_opportunities_from_search
from agent.state import AgentState
from agent.graph import AgentWorkflow
from config import get_config

cfg = get_config()


def render_dashboard():
    render_header("Dashboard", "Your centralized career intelligence hub")

    profile: Optional[UserProfile] = st.session_state.get("user_profile")
    saved_opps: List[Opportunity] = st.session_state.get("saved_opportunities", [])
    history: List[dict] = st.session_state.get("search_history", [])

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        comp_score = profile.completeness_score() if profile else 0
        render_metric_card("Profile Completeness", f"{comp_score}%", "Upload resume to boost" if comp_score < 70 else "Profile ready for matching")
    with col2:
        render_metric_card("Saved Opportunities", str(len(saved_opps)), "Ready for application")
    with col3:
        render_metric_card("Searches Conducted", str(len(history)), "Live SerpApi queries")
    with col4:
        serp_status = "Connected" if cfg.has_serpapi_key() else "Missing Key"
        render_metric_card("SerpApi Status", serp_status, "Google Jobs & Search API")

    st.markdown("---")

    # Quick Search Bar
    st.subheader("⚡ Quick AI Opportunity Search")
    with st.form("quick_search_form"):
        q_col1, q_col2, q_col3 = st.columns([3, 2, 1])
        with q_col1:
            q_role = st.text_input("Role / Skills", placeholder="e.g. Python Developer Intern")
        with q_col2:
            q_loc = st.text_input("Location", value="India")
        with q_col3:
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Search Now", use_container_width=True)

        if submit and q_role:
            st.session_state["search_query_input"] = q_role
            st.session_state["search_location_input"] = q_loc
            st.session_state["current_page"] = "Find Opportunities"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Saved preview or recent results
    if saved_opps:
        render_section_title("📌 Saved Opportunities", "Quick access to your bookmarked positions")
        cols = st.columns(2)
        for idx, opp in enumerate(saved_opps[:4]):
            with cols[idx % 2]:
                render_opportunity_card(opp)
    else:
        render_empty_state("No Saved Opportunities Yet", "Search for jobs or internships and bookmark them to track your applications.")


def render_find_opportunities():
    render_header("Find Opportunities", "Discover, verify, and match jobs & internships powered by SerpApi & AI")

    # Mode Selector
    search_mode = st.radio("Search Mode", ["⚡ Quick Search", "🤖 Autonomous AI Agent (LangGraph)"], horizontal=True)

    profile: Optional[UserProfile] = st.session_state.get("user_profile")

    with st.form("search_form"):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            query = st.text_input("Query / Target Role", value=st.session_state.get("search_query_input", "Python Developer Intern"))
        with c2:
            location = st.text_input("Location", value=st.session_state.get("search_location_input", "India"))
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            btn_label = "Run Agent" if "Agent" in search_mode else "Search"
            submitted = st.form_submit_button(btn_label, use_container_width=True)

    if submitted and query:
        st.session_state["last_query"] = query
        st.session_state["last_location"] = location

        if "Agent" in search_mode:
            # Run Autonomous Agent Workflow
            progress_container = st.container()
            with progress_container:
                st.info("🤖 AI Agent Workflow active...")
                status_placeholder = st.empty()

                def update_status(msg: str):
                    status_placeholder.markdown(f"```\n{msg}\n```")

                workflow = AgentWorkflow()
                initial_state = AgentState(
                    user_query=query,
                    target_location=location,
                    profile=profile
                )
                final_state = workflow.run(initial_state, status_callback=update_status)

                st.success("✅ Agent execution complete!")
                st.session_state["current_opportunities"] = final_state.structured_opportunities
                st.session_state["current_skill_gap"] = final_state.skill_gap_report
                st.session_state["agent_summary"] = final_state.final_summary
        else:
            # Quick Search
            with st.spinner("Searching SerpApi for live opportunities..."):
                res = search_jobs(query=query, location=location)
                opps = extract_opportunities_from_search(res.results)
                
                # Match if profile present
                if profile:
                    for opp in opps:
                        match_res = match_opportunity(profile, opp)
                        opp.match_score = match_res.overall_score
                        opp.matched_skills = match_res.matched_skills
                        opp.missing_skills = match_res.missing_skills
                        opp.explanation = match_res.explanation
                    opps.sort(key=lambda x: x.match_score or 0, reverse=True)

                st.session_state["current_opportunities"] = opps
                
                # Save search history
                history = st.session_state.get("search_history", [])
                history.append({"query": query, "location": location, "count": len(opps), "timestamp": time.strftime("%Y-%m-%d %H:%M")})
                st.session_state["search_history"] = history

    # Display Agent Summary if available
    if st.session_state.get("agent_summary"):
        st.markdown(f"> **AI Agent Insights:** {st.session_state['agent_summary']}")

    # Display Results
    opps: List[Opportunity] = st.session_state.get("current_opportunities", [])
    if opps:
        render_section_title(f"Found {len(opps)} Opportunities", f"Results for '{st.session_state.get('last_query', '')}'")

        cols = st.columns(2)
        for idx, opp in enumerate(opps):
            with cols[idx % 2]:
                render_opportunity_card(opp)
    elif submitted:
        render_empty_state("No Results Found", "Try broadening your query or location criteria.")


def render_my_profile():
    render_header("My Profile", "Upload your resume or manage your profile for AI matching & RAG retrieval")

    profile: UserProfile = st.session_state.get("user_profile") or UserProfile()

    # Resume Upload Section
    st.subheader("📄 Resume Import")
    uploaded_file = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        if st.button("Parse Resume with AI"):
            with st.spinner("Parsing resume content & extracting skills..."):
                parsed_profile = parse_resume_file(uploaded_file.getvalue(), uploaded_file.name)
                if parsed_profile:
                    st.session_state["user_profile"] = parsed_profile
                    profile = parsed_profile
                    st.success("✅ Resume parsed successfully! Profile updated.")
                    st.rerun()
                else:
                    st.error("Failed to parse resume file.")

    st.markdown("---")

    # Manual Profile Editor
    st.subheader("✍️ Profile Details")

    with st.form("profile_editor_form"):
        p_name = st.text_input("Full Name", value=profile.name or "")
        p_location = st.text_input("Location", value=profile.location or "")
        p_skills_str = st.text_area("Technical Skills (comma-separated)", value=", ".join(profile.skills))
        p_exp_years = st.number_input("Years of Experience", min_value=0, max_value=40, value=profile.experience_years)
        p_remote = st.selectbox("Remote Preference", ["Any", "Remote", "Hybrid", "On-site"], index=0)
        p_domains_str = st.text_input("Preferred Domains (comma-separated)", value=", ".join(profile.preferred_domains))

        save_profile = st.form_submit_button("Save Profile Changes", use_container_width=True)

        if save_profile:
            profile.name = p_name
            profile.location = p_location
            profile.skills = [s.strip() for s in p_skills_str.split(",") if s.strip()]
            profile.experience_years = int(p_exp_years)
            profile.remote_preference = p_remote
            profile.preferred_domains = [d.strip() for d in p_domains_str.split(",") if d.strip()]

            st.session_state["user_profile"] = profile
            st.success("✅ Profile saved!")
            st.rerun()

    # RAG Vector Text Preview
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔍 Preview Vector RAG Representation (Text Index)"):
        st.code(profile.to_text_summary(), language="text")


def render_saved_opportunities():
    render_header("Saved Opportunities", "Track and manage your saved roles")

    saved_opps: List[Opportunity] = st.session_state.get("saved_opportunities", [])
    if saved_opps:
        col_export, _ = st.columns([1, 3])
        with col_export:
            json_str = json.dumps([opp.model_dump() for opp in saved_opps], indent=2)
            st.download_button("📥 Export Saved (JSON)", data=json_str, file_name="saved_opportunities.json", mime="application/json")

        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, opp in enumerate(saved_opps):
            with cols[idx % 2]:
                render_opportunity_card(opp)
    else:
        render_empty_state("No Saved Opportunities", "Bookmark opportunities on the Find Opportunities page to view them here.")


def render_skill_gap():
    render_header("Skill Gap Analysis", "Identify missing skills and get actionable preparation roadmaps")

    profile: Optional[UserProfile] = st.session_state.get("user_profile")
    opps: List[Opportunity] = st.session_state.get("current_opportunities", [])

    if not profile or not profile.skills:
        st.warning("⚠️ Please complete your profile skills in 'My Profile' to see a detailed skill gap analysis.")
        return

    if not opps:
        st.info("ℹ️ Search for opportunities first on the 'Find Opportunities' page to analyze skill gaps across active listings.")
        return

    analyzer = SkillGapAnalyzer()
    report = analyzer.analyze(profile, opps)

    st.subheader(f"Target Role Analysis ({len(opps)} opportunities analyzed)")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 💪 Strong Skills")
        if report.strong_skills:
            for s in report.strong_skills:
                st.markdown(f"- ✅ **{s}**")
        else:
            st.caption("No strong skills matched yet.")

    with col2:
        st.markdown("### 📈 Developing Skills")
        if report.developing_skills:
            for s in report.developing_skills:
                st.markdown(f"- ⚡ **{s}**")
        else:
            st.caption("No developing skills detected.")

    with col3:
        st.markdown("### ⚠️ Priority Skill Gaps")
        if report.missing_priority_skills:
            for s in report.missing_priority_skills:
                st.markdown(f"- 🚨 **{s}**")
        else:
            st.caption("Great job! No major skill gaps detected.")

    st.markdown("---")

    st.subheader("🚀 Actionable Preparation Roadmap")
    for idx, rec in enumerate(report.recommendations, 1):
        st.markdown(f"**Step {idx}:** {rec}")


def render_history():
    render_header("Search History", "Log of your recent SerpApi search queries")

    history: List[dict] = st.session_state.get("search_history", [])

    if history:
        for item in reversed(history):
            query = html.escape(str(item.get('query', '')))
            loc = html.escape(str(item.get('location', '')))
            count = item.get('count', 0)
            timestamp = html.escape(str(item.get('timestamp', '')))
            st.markdown(textwrap.dedent(f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
                <strong>Query:</strong> {query} &nbsp;|&nbsp; 
                <strong>Location:</strong> {loc} &nbsp;|&nbsp; 
                <strong>Results:</strong> {count} &nbsp;|&nbsp; 
                <span style="color: #64748B;">{timestamp}</span>
            </div>
            """).strip(), unsafe_allow_html=True)
    else:
        render_empty_state("No Search History", "Your SerpApi searches will be logged here.")


def render_settings():
    render_header("Settings", "Configure API keys, LLM providers, and view system status")

    st.subheader("🔑 API Key Status")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### SerpApi")
        if cfg.has_serpapi_key():
            st.success("✅ SerpApi Key Configured")
        else:
            st.error("❌ SerpApi Key Missing")

    with c2:
        st.markdown(f"#### LLM Provider ({cfg.LLM_PROVIDER.upper()})")
        if cfg.has_llm_key():
            st.success(f"✅ {cfg.LLM_PROVIDER.title()} Key Configured")
        else:
            st.info(f"ℹ️ {cfg.LLM_PROVIDER.title()} Key Optional (Heuristic fallback active)")

    st.markdown("---")

    st.subheader("🧪 Test Connections")
    if st.button("Test SerpApi Connection"):
        with st.spinner("Testing SerpApi..."):
            res = search_jobs(query="Python Intern", location="India")
            if res.error:
                st.error(f"SerpApi Error: {res.error}")
            else:
                st.success(f"✅ SerpApi Working! Retrieved {len(res.results)} test results.")


# Aliases for app.py router
render_saved = render_saved_opportunities
render_search_history = render_history

