"""
OpportunityIQ — Design System

Professional CSS styles and theming for the Streamlit application.
Color system, typography, and component styles.
"""


def get_custom_css() -> str:
    """Return the complete custom CSS for the application."""
    return """
    <style>
    /* ================================================================
       OpportunityIQ Design System
       Professional SaaS aesthetic — Inter font, blue accent, clean layout
       ================================================================ */

    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global Reset ── */
    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .stApp {
        background-color: #F8FAFC;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        min-width: 260px !important;
        max-width: 260px !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: #E2E8F0 !important;
    }

    section[data-testid="stSidebar"] .stMarkdown a {
        color: #93C5FD !important;
        text-decoration: none;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #1E293B;
        margin: 0.75rem 0;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: #CBD5E1 !important;
        font-size: 14px;
        font-weight: 400;
        padding: 6px 0;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        color: #FFFFFF !important;
    }

    /* ── Main Content Area ── */
    .main .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ── Typography ── */
    h1 {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 32px !important;
        letter-spacing: -0.5px;
        margin-bottom: 0.25rem !important;
    }

    h2 {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 24px !important;
        letter-spacing: -0.3px;
    }

    h3 {
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 18px !important;
    }

    p, li {
        color: #334155;
        font-size: 14px;
        line-height: 1.6;
    }

    /* ── Cards ── */
    .oiq-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 12px;
        transition: box-shadow 0.15s ease;
    }

    .oiq-card:hover {
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }

    .oiq-card-title {
        font-size: 16px;
        font-weight: 600;
        color: #0F172A;
        margin: 0 0 4px 0;
    }

    .oiq-card-subtitle {
        font-size: 13px;
        color: #64748B;
        margin: 0 0 12px 0;
    }

    /* ── Metric Cards ── */
    .oiq-metric {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }

    .oiq-metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }

    .oiq-metric-label {
        font-size: 12px;
        font-weight: 500;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 4px 0 0 0;
    }

    /* ── Badges / Tags ── */
    .oiq-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin: 2px 4px 2px 0;
    }

    .oiq-badge-blue {
        background: #EFF6FF;
        color: #2563EB;
        border: 1px solid #BFDBFE;
    }

    .oiq-badge-green {
        background: #F0FDF4;
        color: #16A34A;
        border: 1px solid #BBF7D0;
    }

    .oiq-badge-orange {
        background: #FFFBEB;
        color: #D97706;
        border: 1px solid #FDE68A;
    }

    .oiq-badge-red {
        background: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FECACA;
    }

    .oiq-badge-gray {
        background: #F8FAFC;
        color: #64748B;
        border: 1px solid #E2E8F0;
    }

    /* ── Match Score ── */
    .oiq-match-score {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 52px;
        height: 52px;
        border-radius: 50%;
        font-size: 16px;
        font-weight: 700;
    }

    .oiq-match-high {
        background: #F0FDF4;
        color: #16A34A;
        border: 2px solid #86EFAC;
    }

    .oiq-match-medium {
        background: #FFFBEB;
        color: #D97706;
        border: 2px solid #FDE68A;
    }

    .oiq-match-low {
        background: #FEF2F2;
        color: #DC2626;
        border: 2px solid #FECACA;
    }

    /* ── Progress Bar ── */
    .oiq-progress-bar {
        background: #E2E8F0;
        border-radius: 4px;
        height: 8px;
        overflow: hidden;
        margin: 8px 0;
    }

    .oiq-progress-fill {
        height: 100%;
        border-radius: 4px;
        background: #2563EB;
        transition: width 0.3s ease;
    }

    /* ── Status Indicators ── */
    .oiq-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 500;
    }

    .oiq-status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }

    .oiq-status-dot-green {
        background: #16A34A;
        box-shadow: 0 0 4px rgba(22, 163, 74, 0.4);
    }

    .oiq-status-dot-orange {
        background: #D97706;
    }

    .oiq-status-dot-red {
        background: #DC2626;
    }

    /* ── Buttons ── */
    .stButton > button {
        background-color: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        font-size: 14px;
        padding: 8px 20px;
        transition: background-color 0.15s ease;
    }

    .stButton > button:hover {
        background-color: #1D4ED8;
        color: #FFFFFF;
        border: none;
    }

    .stButton > button:active {
        background-color: #1E40AF;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        font-size: 14px;
        font-family: 'Inter', sans-serif;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #2563EB;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
    }

    .stSelectbox > div > div {
        border-radius: 6px;
    }

    /* ── Divider ── */
    .oiq-divider {
        border: none;
        border-top: 1px solid #E2E8F0;
        margin: 16px 0;
    }

    /* ── Empty State ── */
    .oiq-empty-state {
        text-align: center;
        padding: 48px 24px;
        color: #94A3B8;
    }

    .oiq-empty-state-icon {
        font-size: 36px;
        margin-bottom: 12px;
    }

    .oiq-empty-state-text {
        font-size: 14px;
        color: #94A3B8;
        margin: 0;
    }

    /* ── Search Progress ── */
    .oiq-progress-step {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        font-size: 14px;
        color: #475569;
    }

    .oiq-progress-step-done {
        color: #16A34A;
    }

    .oiq-progress-step-active {
        color: #2563EB;
        font-weight: 500;
    }

    /* ── Source Link ── */
    .oiq-source-link {
        font-size: 12px;
        color: #64748B;
    }

    .oiq-source-link a {
        color: #2563EB;
        text-decoration: none;
    }

    .oiq-source-link a:hover {
        text-decoration: underline;
    }

    /* ── Section Header ── */
    .oiq-section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }

    /* ── Streamlit Overrides ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #E2E8F0;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: #64748B;
        padding: 8px 16px;
    }

    .stTabs [aria-selected="true"] {
        color: #2563EB !important;
        border-bottom-color: #2563EB !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    </style>
    """
