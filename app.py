"""
OpportunityIQ — AI Opportunity Intelligence Agent

Streamlit application entry point.
Discover. Verify. Analyze. Act.
"""

import streamlit as st
from config import config
from ui.styles import get_custom_css
from ui.components import render_status_indicator
from ui.pages import (
    render_dashboard,
    render_find_opportunities,
    render_my_profile,
    render_saved,
    render_skill_gap,
    render_search_history,
    render_settings,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Page Config ──
st.set_page_config(
    page_title="OpportunityIQ — AI Opportunity Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Custom CSS ──
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Initialize Session State ──
defaults = {
    "current_page": "Dashboard",
    "user_profile": None,
    "search_history": [],
    "saved_opportunities": [],
    "search_results": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ── Sidebar Navigation ──
with st.sidebar:
    # Brand
    st.markdown(
        '<h2 style="color: #FFFFFF; font-weight: 700; font-size: 20px; '
        'letter-spacing: -0.3px; margin-bottom: 0;">◆ OpportunityIQ</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color: #64748B; font-size: 11px; margin-top: 2px; margin-bottom: 16px;">'
        'AI Opportunity Intelligence</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Navigation
    pages = [
        "Dashboard",
        "Find Opportunities",
        "My Profile",
        "Saved",
        "Skill Gap",
        "Search History",
        "Settings",
    ]

    selected = st.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state["current_page"]),
        key="nav_radio",
        label_visibility="collapsed",
    )
    st.session_state["current_page"] = selected

    # Bottom section — API status
    st.markdown("---")
    st.markdown(
        '<p style="color: #475569; font-size: 11px; text-transform: uppercase; '
        'letter-spacing: 0.5px; margin-bottom: 8px;">Connections</p>',
        unsafe_allow_html=True,
    )

    # SerpApi status
    if config.serpapi.is_configured:
        st.markdown(
            render_status_indicator("SerpApi Connected", "green"),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            render_status_indicator("SerpApi — Not configured", "red"),
            unsafe_allow_html=True,
        )

    # LLM status
    if config.llm.is_configured:
        st.markdown(
            render_status_indicator(f"LLM — {config.llm.provider.title()}", "green"),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            render_status_indicator("LLM — Not configured", "orange"),
            unsafe_allow_html=True,
        )

    # Live search indicator
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        render_status_indicator("Live Search", "green" if config.serpapi.is_configured else "red"),
        unsafe_allow_html=True,
    )

    # Version
    st.markdown(
        f'<p style="color: #334155; font-size: 10px; margin-top: 24px;">'
        f'v{config.version}</p>',
        unsafe_allow_html=True,
    )

# ── Page Router ──
page = st.session_state["current_page"]

if page == "Dashboard":
    render_dashboard()
elif page == "Find Opportunities":
    render_find_opportunities()
elif page == "My Profile":
    render_my_profile()
elif page == "Saved":
    render_saved()
elif page == "Skill Gap":
    render_skill_gap()
elif page == "Search History":
    render_search_history()
elif page == "Settings":
    render_settings()
else:
    render_dashboard()

logger.info(f"Page rendered: {page}")
