import streamlit as st

LOGO_URL = "https://i.ibb.co/YTYGn5qV/logo.png"


def header_home():
    st.markdown(f"""
        <div style="
            display:flex; flex-direction:column; align-items:center;
            justify-content:center; margin-bottom:1.75rem; margin-top:0.5rem;
            text-align:center;
        ">
            <img src='{LOGO_URL}' style='height:88px; margin-bottom:0.6rem; filter:drop-shadow(0 0 24px rgba(139,92,246,0.5));' />
            <h1 style='color:white; letter-spacing:3px; font-size:3.2rem; text-shadow:0 0 40px rgba(99,102,241,0.6);'>ATTENDLY</h1>
            <p style='color:rgba(255,255,255,0.6); font-size:1.05rem; margin-top:0.4rem; font-family:Outfit,sans-serif; font-weight:400;'>
                AI-powered attendance, redefined.
            </p>
        </div>
    """, unsafe_allow_html=True)


def header_dashboard():
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px;">
            <img src='{LOGO_URL}' style='height:48px;' />
            <span style='
                font-family: Climate Crisis, sans-serif;
                font-size: 1.55rem;
                background: linear-gradient(135deg, #6366F1, #8B5CF6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 400;
                letter-spacing: 1px;
            '>ATTENDLY</span>
        </div>
    """, unsafe_allow_html=True)
