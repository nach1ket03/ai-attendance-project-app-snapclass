import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():
    style_background_home()
    style_base_layout()

    header_home()

    st.markdown("""
        <div style="text-align:center; margin-bottom:2rem;">
            <p style="color:rgba(255,255,255,0.55); font-size:0.95rem; font-family:Outfit,sans-serif; margin:0;">
                Face recognition &nbsp;·&nbsp; Voice identification &nbsp;·&nbsp; Instant reports
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
            <div style="text-align:center; margin-bottom:1rem;">
                <div style="font-size:3rem; margin-bottom:0.5rem;">🎓</div>
                <h3 style="color:white; margin:0 0 0.3rem; font-size:1.2rem; font-weight:700;">Student Portal</h3>
                <p style="color:rgba(255,255,255,0.55); font-size:0.88rem; margin:0; font-family:Outfit,sans-serif; line-height:1.5;">
                    Log in instantly with your face.<br/>No passwords needed.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button('Enter as Student', type='primary', icon=':material/face:', width='stretch'):
            st.session_state['login_type'] = 'student'
            st.rerun()

    with col2:
        st.markdown("""
            <div style="text-align:center; margin-bottom:1rem;">
                <div style="font-size:3rem; margin-bottom:0.5rem;">📋</div>
                <h3 style="color:white; margin:0 0 0.3rem; font-size:1.2rem; font-weight:700;">Teacher Portal</h3>
                <p style="color:rgba(255,255,255,0.55); font-size:0.88rem; margin:0; font-family:Outfit,sans-serif; line-height:1.5;">
                    Manage subjects and take<br/>AI-powered attendance.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button('Enter as Teacher', type='primary', icon=':material/school:', width='stretch'):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    st.markdown("""
        <div style="display:flex; justify-content:center; gap:10px; flex-wrap:wrap; margin-top:2.25rem;">
            <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.13); padding:7px 16px; border-radius:20px; color:rgba(255,255,255,0.7); font-size:0.8rem; font-family:Outfit,sans-serif;">
                🤖 Face Recognition
            </div>
            <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.13); padding:7px 16px; border-radius:20px; color:rgba(255,255,255,0.7); font-size:0.8rem; font-family:Outfit,sans-serif;">
                🎙️ Voice ID
            </div>
            <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.13); padding:7px 16px; border-radius:20px; color:rgba(255,255,255,0.7); font-size:0.8rem; font-family:Outfit,sans-serif;">
                📊 Instant Reports
            </div>
            <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.13); padding:7px 16px; border-radius:20px; color:rgba(255,255,255,0.7); font-size:0.8rem; font-family:Outfit,sans-serif;">
                🔗 QR Enrollment
            </div>
        </div>
    """, unsafe_allow_html=True)

    footer_home()
