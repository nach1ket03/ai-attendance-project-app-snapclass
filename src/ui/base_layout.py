import streamlit as st


def style_background_home():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 55%, #0C1445 100%) !important;
            min-height: 100vh;
        }
        .stApp div[data-testid="stColumn"] {
            background: rgba(255,255,255,0.07) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            padding: 2.25rem !important;
            border-radius: 1.25rem !important;
        }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
        <style>
        .stApp {
            background: #F1F5F9 !important;
        }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979..1990&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        #MainMenu, footer, header { visibility: hidden; }

        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }

        *, p, span, div, label, li {
            font-family: 'Outfit', sans-serif !important;
        }

        h1 {
            font-family: 'Climate Crisis', sans-serif !important;
            font-size: 2.8rem !important;
            line-height: 1.05 !important;
            letter-spacing: -0.5px !important;
            margin-bottom: 0 !important;
        }

        h2 {
            font-family: 'Climate Crisis', sans-serif !important;
            font-size: 1.75rem !important;
            line-height: 1 !important;
            margin-bottom: 0 !important;
        }

        h3 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
        }

        /* ── Buttons ── */
        button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-family: 'Outfit', sans-serif !important;
            transition: all 0.18s ease !important;
            border: none !important;
            letter-spacing: 0.2px !important;
        }

        button[kind="primary"] {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
            color: white !important;
            box-shadow: 0 4px 14px rgba(99,102,241,0.38) !important;
        }

        button[kind="secondary"] {
            background: white !important;
            color: #6366F1 !important;
            border: 2px solid #6366F1 !important;
            box-shadow: none !important;
        }

        button[kind="tertiary"] {
            background: transparent !important;
            color: #64748B !important;
            border: 1.5px solid #CBD5E1 !important;
            box-shadow: none !important;
        }

        button:hover {
            transform: translateY(-2px) !important;
            filter: brightness(1.06) !important;
        }

        /* ── Inputs ── */
        [data-testid="stTextInput"] input {
            border-radius: 10px !important;
            border: 1.5px solid #CBD5E1 !important;
            font-family: 'Outfit', sans-serif !important;
            padding: 10px 14px !important;
            transition: border-color 0.15s ease !important;
        }

        [data-testid="stTextInput"] input:focus {
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
            outline: none !important;
        }

        [data-testid="stSelectbox"] > div {
            border-radius: 10px !important;
            border: 1.5px solid #CBD5E1 !important;
        }

        /* ── Divider ── */
        hr {
            border-color: #E2E8F0 !important;
            margin: 1.25rem 0 !important;
        }

        /* ── Dataframe ── */
        [data-testid="stDataFrame"] {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid #E2E8F0 !important;
        }

        /* ── Info / warning / error boxes ── */
        [data-testid="stAlert"] {
            border-radius: 10px !important;
        }

        /* ── Spinner ── */
        [data-testid="stSpinner"] {
            font-family: 'Outfit', sans-serif !important;
        }
        </style>
    """, unsafe_allow_html=True)
