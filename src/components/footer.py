import streamlit as st


def footer_home():
    st.markdown("""
        <div style="text-align:center; margin-top:2rem; padding-top:1rem; border-top:1px solid rgba(255,255,255,0.08);">
            <p style="color:rgba(255,255,255,0.35); font-size:0.78rem; font-family:Outfit,sans-serif; margin:0;">
                Attendly &nbsp;·&nbsp; AI-powered attendance for modern classrooms
            </p>
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    st.markdown("""
        <div style="text-align:center; margin-top:3rem; padding-top:1rem; border-top:1px solid #E2E8F0;">
            <p style="color:#94A3B8; font-size:0.78rem; font-family:Outfit,sans-serif; margin:0;">
                Attendly &nbsp;·&nbsp; AI-powered attendance for modern classrooms
            </p>
        </div>
    """, unsafe_allow_html=True)
