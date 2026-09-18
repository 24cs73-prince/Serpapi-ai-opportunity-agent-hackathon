"""
OpportunityIQ — Reusable UI Components

Streamlit-compatible component builders for cards, badges,
metrics, progress indicators, headers, and modal overlays.
"""

import html
import textwrap
import streamlit as st
from typing import Optional, List
from analysis.opportunity import Opportunity


def render_header(title: str, subtitle: str = ""):
    """Render page header title & subtitle."""
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"<p style='color: #64748B; font-size: 15px; margin-top: -6px; margin-bottom: 20px;'>{html.escape(subtitle)}</p>", unsafe_allow_html=True)


def render_section_title(title: str, subtitle: str = ""):
    """Render section heading."""
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def render_metric_card(label: str, value: str, hint: str = ""):
    """Render a styled Streamlit metric card."""
    st.metric(label=label, value=value, delta=hint if hint else None)


def render_status_indicator(label: str, status: str = "green") -> str:
    """Render a status indicator with dot. Status: green, orange, red."""
    color_map = {"green": "#16A34A", "orange": "#D97706", "red": "#DC2626"}
    dot_color = color_map.get(status, "#16A34A")
    return f'<span style="height: 8px; width: 8px; background-color: {dot_color}; border-radius: 50%; display: inline-block; margin-right: 6px;"></span><span style="font-size: 13px; color: #475569;">{html.escape(label)}</span>'


def render_badge(text: str, variant: str = "blue") -> str:
    """Render an inline badge. Variants: blue, green, orange, red, gray."""
    escaped_text = html.escape(str(text).replace("\n", " "))
    return f'<span style="background-color: #EFF6FF; color: #1E40AF; border: 1px solid #DBEAFE; padding: 3px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; margin-right: 6px; display: inline-block; margin-bottom: 4px;">{escaped_text}</span>'


def render_skill_badges(skills: List[str], variant: str = "blue") -> str:
    """Render a list of skills as inline badges."""
    if not skills:
        return ""
    return " ".join(render_badge(skill, variant) for skill in skills if skill)


def render_match_score(score: float) -> str:
    """Render match score indicator."""
    color = "#059669" if score >= 75 else ("#D97706" if score >= 50 else "#DC2626")
    bg_color = "#ECFDF5" if score >= 75 else ("#FFFBEB" if score >= 50 else "#FEF2F2")
    border_color = "#A7F3D0" if score >= 75 else ("#FDE68A" if score >= 50 else "#FECACA")
    return f'<span style="background-color: {bg_color}; color: {color}; border: 1px solid {border_color}; padding: 4px 10px; border-radius: 16px; font-weight: 700; font-size: 13px;">{int(score)}% Match</span>'


def render_opportunity_card(opp: Opportunity):
    """Render an opportunity card in Streamlit using native border container."""
    url = opp.application_url or opp.apply_link
    title = (opp.title or "Opportunity").strip().replace("\n", " ")
    company = (opp.company or "Company").strip().replace("\n", " ")
    location = (opp.location or "India").strip().replace("\n", " ")
    
    raw_desc = (opp.description or "").replace("\n", " ").replace("\r", " ").strip()
    description = raw_desc[:140] + ("..." if len(raw_desc) > 140 else "")

    with st.container(border=True):
        col_title, col_score = st.columns([4, 1])
        with col_title:
            st.subheader(title)
            st.markdown(f"**:blue[{html.escape(company)}]** &nbsp;•&nbsp; <span style='color: #64748B;'>{html.escape(location)}</span>", unsafe_allow_html=True)
        with col_score:
            if opp.match_score:
                st.markdown(render_match_score(opp.match_score), unsafe_allow_html=True)

        if description:
            st.caption(description)

        if opp.required_skills:
            st.markdown(render_skill_badges(opp.required_skills[:4]), unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

        col_apply, col_save, col_details = st.columns([2, 2, 3])
        with col_apply:
            if url:
                st.link_button("Apply ↗", url, use_container_width=True)
            else:
                st.button("Apply ↗", key=f"apply_{opp.id}", disabled=True, use_container_width=True)

        with col_save:
            saved_list: List[Opportunity] = st.session_state.get("saved_opportunities", [])
            is_saved = any(
                s.id == opp.id or (s.title.lower() == opp.title.lower() and (s.company or "").lower() == (opp.company or "").lower())
                for s in saved_list
            )
            btn_label = "Saved ✓" if is_saved else "Bookmark"
            if st.button(btn_label, key=f"save_{opp.id}", use_container_width=True):
                if is_saved:
                    st.session_state["saved_opportunities"] = [
                        s for s in saved_list
                        if not (s.id == opp.id or (s.title.lower() == opp.title.lower() and (s.company or "").lower() == (opp.company or "").lower()))
                    ]
                    st.toast("Removed from bookmarks")
                else:
                    saved_list.append(opp)
                    st.session_state["saved_opportunities"] = saved_list
                    st.toast("📌 Opportunity saved to your bookmarks!")
                st.rerun()

        with col_details:
            with st.popover("View Details"):
                render_opportunity_detail_modal(opp)


def render_opportunity_detail_modal(opp: Opportunity):
    """Render details popover for an opportunity."""
    url = opp.application_url or opp.apply_link
    st.subheader(opp.title)
    st.markdown(f"**Company:** {opp.company or 'Not specified'}")
    st.markdown(f"**Location:** {opp.location or 'Not specified'}")
    st.markdown(f"**Experience:** {opp.experience_required or 'Not specified'}")
    if opp.salary_or_stipend:
        st.markdown(f"**Salary/Stipend:** {opp.salary_or_stipend}")

    if opp.explanation:
        st.info(f"💡 **AI Match Analysis:** {opp.explanation}")

    if opp.required_skills:
        st.markdown("#### Required Skills")
        st.markdown(render_skill_badges(opp.required_skills), unsafe_allow_html=True)

    if opp.preferred_skills:
        st.markdown("#### Preferred Skills")
        st.markdown(render_skill_badges(opp.preferred_skills, variant="green"), unsafe_allow_html=True)

    st.markdown("#### Description")
    st.write(opp.description or "No detailed description provided.")

    if url:
        st.link_button("Apply Directly on Source", url)


def render_empty_state(title: str, description: str):
    """Render empty state card."""
    with st.container(border=True):
        st.markdown(f"#### {html.escape(title)}")
        st.caption(description)
