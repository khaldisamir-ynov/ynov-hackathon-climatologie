import streamlit as st

COLORS = {
    "primary": "#1B6B93",
    "primary_light": "#E8F4F8",
    "accent": "#2E8B57",
    "warm": "#D4654A",
    "warm_light": "#FDEEE9",
    "cold": "#4A90D9",
    "cold_light": "#E8F0FA",
    "amber": "#D4A03C",
    "bg_card": "#FFFFFF",
    "bg_page": "#FAFBFC",
    "text_dark": "#1A1A2E",
    "text_muted": "#6B7280",
    "border": "#E2E8F0",
}


def inject_css():
    st.markdown("""
    <style>
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1B6B93 0%, #145374 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSlider label {
            color: rgba(255,255,255,0.85) !important;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 4px solid #1B6B93;
            border-radius: 8px;
            padding: 12px 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        div[data-testid="stMetric"] label {
            color: #6B7280 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #1A1A2E !important;
            font-weight: 600 !important;
        }

        /* Page header styling */
        .page-header {
            background: linear-gradient(135deg, #1B6B93 0%, #2E8B57 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            color: white;
        }
        .page-header h2 {
            margin: 0 0 4px 0;
            color: white !important;
            font-size: 1.6rem;
        }
        .page-header p {
            margin: 0;
            color: rgba(255,255,255,0.85);
            font-size: 0.95rem;
        }

        /* Nav cards on home */
        .nav-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .nav-card:hover {
            border-color: #1B6B93;
            box-shadow: 0 4px 12px rgba(27,107,147,0.12);
            transform: translateY(-2px);
        }
        .nav-card .icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .nav-card .title {
            font-weight: 600;
            color: #1A1A2E;
            font-size: 1rem;
            margin-bottom: 0.3rem;
        }
        .nav-card .desc {
            color: #6B7280;
            font-size: 0.8rem;
        }

        /* Filter containers */
        .filter-bar {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }

        /* Dataframe */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
        }

        /* Dividers */
        hr {
            border-color: #E2E8F0 !important;
        }

        /* Buttons */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1B6B93, #2E8B57) !important;
            border: none !important;
        }

        /* Info/warning boxes */
        div[data-testid="stAlert"] {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)


def page_header(title, subtitle):
    st.markdown(
        f'<div class="page-header">'
        f'<h2>{title}</h2>'
        f'<p>{subtitle}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def sidebar_brand():
    st.sidebar.markdown(
        '<div style="text-align:center; padding: 1rem 0 0.5rem;">'
        '<span style="font-size: 2rem;">🌡️</span><br>'
        '<span style="font-size: 1.3rem; font-weight: 700; letter-spacing: 1px;">ClimaFrance</span><br>'
        '<span style="font-size: 0.75rem; opacity: 0.8;">Exploration climatique</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.divider()
