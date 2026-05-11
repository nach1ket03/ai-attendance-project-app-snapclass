import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    stats_html = ""
    if stats:
        chips = "".join(
            f'<span style="background:#EEF2FF; color:#6366F1; padding:4px 12px; border-radius:20px; font-size:0.82rem; font-weight:600; display:inline-flex; align-items:center; gap:4px;">{icon} <b>{value}</b>&nbsp;{label}</span>'
            for icon, label, value in stats
        )
        stats_html = f'<div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:14px;">{chips}</div>'

    html = f"""
        <div style="
            background: white;
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 1rem;
            box-shadow: 0 2px 12px rgba(99,102,241,0.07);
            border: 1px solid #E2E8F0;
        ">
            <div style="height:4px; background:linear-gradient(90deg,#6366F1,#8B5CF6);"></div>
            <div style="padding:1.25rem 1.5rem 1rem;">
                <h3 style="margin:0 0 6px; color:#0F172A; font-size:1.15rem; font-weight:700;">{name}</h3>
                <p style="color:#64748B; margin:0; font-size:0.88rem; display:flex; align-items:center; gap:8px;">
                    <span style="background:#EEF2FF; color:#6366F1; padding:2px 10px; border-radius:6px; font-weight:600; font-size:0.82rem;">{code}</span>
                    <span style="color:#CBD5E1;">·</span>
                    Section {section}
                </p>
                {stats_html}
            </div>
        </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        with st.container():
            footer_callback()
        st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)
