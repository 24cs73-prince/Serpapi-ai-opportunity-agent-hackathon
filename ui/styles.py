"""
OpportunityIQ — Modern Luxury Design System

Professional, high-contrast, human-crafted CSS for Streamlit.
Clean Porcelain Canvas (#F8FAFC), Royal Indigo Accent (#2563EB),
Deep Slate Sidebar (#0F172A), and crisp typography.
"""


def get_custom_css() -> str:
    """Return the complete custom CSS for the application."""
    return """
    <style>
    /* ================================================================
       OpportunityIQ — Luxury Modern Design System
       ================================================================ */

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global Theme Canvas ── */
    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }

    .stApp {
        background-color: #F8FAFC;
    }

    /* ── Sidebar Styling ── */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
        min-width: 270px !important;
        max-width: 270px !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: #F1F5F9 !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #334155 !important;
        margin: 1rem 0 !important;
    }

    /* Sidebar Radio Nav Items */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 4px;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: #94A3B8 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        color: #FFFFFF !important;
        background-color: #1E293B !important;
    }

    /* Selected Radio Item */
    section[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] {
        color: #FFFFFF !important;
        background-color: #2563EB !important;
        font-weight: 600 !important;
    }

    /* ── Main Container ── */
    .main .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* ── Typography ── */
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #0F172A !important;
    }

    h1 {
        font-size: 32px !important;
        font-weight: 800 !important;
        letter-spacing: -0.6px !important;
        margin-bottom: 6px !important;
    }

    h2 {
        font-size: 24px !important;
        font-weight: 700 !important;
        letter-spacing: -0.4px !important;
    }

    h3 {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
    }

    p, li, label, .stMarkdown p {
        color: #334155;
        font-size: 14px;
        line-height: 1.6;
    }

    /* ── File Uploader Styling (Fix for uploadUpload text duplication) ── */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        transition: border-color 0.2s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #2563EB !important;
    }

    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
        background-color: #F8FAFC !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 16px !important;
    }

    [data-testid="stFileUploader"] button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 18px !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    }

    [data-testid="stFileUploader"] button * {
        color: #FFFFFF !important;
    }

    /* Hide internal icon span text to prevent duplicate "uploadUpload" */
    [data-testid="stFileUploader"] button span[aria-hidden="true"],
    [data-testid="stFileUploader"] button span[data-testid="stIconMaterial"] {
        display: none !important;
    }

    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] p {
        color: #475569 !important;
    }

    /* ── Form Buttons & Action Buttons (High Contrast White Text) ── */
    div.stButton > button,
    div[data-testid="stForm"] div.stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 20px !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease !important;
    }

    /* Force all text elements inside main buttons to be solid white */
    div.stButton > button *,
    div[data-testid="stForm"] div.stButton > button * {
        color: #FFFFFF !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
        transform: translateY(-1px);
    }

    /* Exclude utility buttons inside NumberInputs & Selectboxes from main button styles */
    div[data-testid="stNumberInputContainer"] button,
    div[data-testid="stNumberInputContainer"] button * {
        background: #F8FAFC !important;
        color: #334155 !important;
        box-shadow: none !important;
        transform: none !important;
    }

    div[data-testid="stNumberInputContainer"] button:hover {
        background: #F1F5F9 !important;
        color: #0F172A !important;
    }

    /* Link Buttons */
    .stLinkButton > a {
        background-color: #EFF6FF !important;
        color: #2563EB !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 16px !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.15s ease !important;
    }

    .stLinkButton > a:hover {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
    }

    /* ── Form Inputs & Widgets ── */
    .stTextInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        color: #0F172A !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }

    /* Selectbox, NumberInput & BaseWeb Containers Fix */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInputContainer"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        color: #0F172A !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    div[data-baseweb="input"] input,
    div[data-testid="stNumberInputContainer"] input {
        color: #0F172A !important;
        background-color: transparent !important;
    }

    div[data-testid="stNumberInputContainer"] button svg {
        fill: #334155 !important;
    }

    /* Dropdown Option List Popovers */
    div[data-baseweb="popover"] ul,
    div[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.1) !important;
    }

    div[role="option"] {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
    }

    div[role="option"]:hover, div[role="option"][aria-selected="true"] {
        background-color: #EFF6FF !important;
        color: #2563EB !important;
    }

    /* ── Custom Cards ── */
    .oiq-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px -2px rgba(15, 23, 42, 0.04);
        transition: all 0.2s ease;
    }

    .oiq-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 8px 20px -4px rgba(15, 23, 42, 0.08);
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #0F172A !important;
    }

    /* ── Expander Overrides & Icon Fix ── */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
    }

    [data-testid="stExpander"] details {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
    }

    [data-testid="stExpander"] summary {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    [data-testid="stExpander"] summary:hover {
        color: #2563EB !important;
    }

    [data-testid="stExpander"] summary svg {
        fill: #475569 !important;
    }

    div[data-testid="stPopover"] > button {
        background-color: #F8FAFC !important;
        color: #334155 !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: none !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
    }

    /* ── Streamlit Header Cleanup ── */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    </style>
    """
