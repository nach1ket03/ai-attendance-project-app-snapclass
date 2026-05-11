import streamlit as st
import numpy as np
import time
from PIL import Image

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import (
    create_student, get_student_by_id,
    get_student_subjects, get_student_attendance,
    unenroll_student_to_subject,
)
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    _student_login()


# ── Dashboard ─────────────────────────────────────────────────────────────────

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    c1, c2 = st.columns([1, 2], vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        info_col, btn_col = st.columns([3, 1])
        with info_col:
            st.markdown(f"""
                <p style="color:#94A3B8; margin:0; font-size:0.82rem; font-family:Outfit,sans-serif;">Welcome back</p>
                <p style="color:#0F172A; font-weight:700; font-size:1.05rem; margin:0; font-family:Outfit,sans-serif;">{student_data['name']}</p>
            """, unsafe_allow_html=True)
        with btn_col:
            if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
                st.session_state['is_logged_in'] = False
                del st.session_state.student_data
                st.rerun()

    st.divider()

    with st.spinner('Loading your subjects...'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    # Build per-subject stats
    stats_map = {}
    for log in logs:
        sid = log['subject_id']
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]['total'] += 1
        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    total_classes = sum(v['total'] for v in stats_map.values())
    total_attended = sum(v['attended'] for v in stats_map.values())
    rate = round(total_attended / total_classes * 100) if total_classes else 0

    # Quick stats
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(_stat_card("📚", "Enrolled", len(subjects), "#6366F1"), unsafe_allow_html=True)
    with s2:
        st.markdown(_stat_card("✅", "Attended", total_attended, "#10B981"), unsafe_allow_html=True)
    with s3:
        st.markdown(_stat_card("📈", "Rate", f"{rate}%", "#8B5CF6"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    hdr_c1, hdr_c2 = st.columns([3, 1], vertical_alignment='bottom')
    with hdr_c1:
        st.header('Enrolled Subjects')
    with hdr_c2:
        if st.button('+ Enroll', type='primary', width='stretch'):
            enroll_dialog()

    st.divider()

    if not subjects:
        st.markdown("""
            <div style="text-align:center; padding:3rem 1rem; background:white; border-radius:16px; border:1px solid #E2E8F0; margin-top:1rem;">
                <p style="font-size:2rem; margin:0;">🎓</p>
                <p style="color:#64748B; font-size:0.95rem; margin:0.5rem 0 0; font-family:Outfit,sans-serif;">Not enrolled in any subjects yet. Use the Enroll button above.</p>
            </div>
        """, unsafe_allow_html=True)
        footer_dashboard()
        return

    cols = st.columns(2, gap='medium')
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']
        s = stats_map.get(sid, {"total": 0, "attended": 0})

        def unenroll_btn(sub=sub, sid=sid):
            if st.button("Unenroll", key=f"unenroll_{sid}", type='tertiary',
                         width='stretch', icon=':material/delete_forever:'):
                unenroll_student_to_subject(student_id, sid)
                st.toast(f"Unenrolled from {sub['name']}")
                st.rerun()

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('📅', 'Total', s['total']),
                    ('✅', 'Attended', s['attended']),
                ],
                footer_callback=unenroll_btn,
            )

    footer_dashboard()


def _stat_card(icon, label, value, color):
    return f"""
        <div style="
            background:white; border-radius:14px; padding:1.1rem 1.25rem;
            border:1px solid #E2E8F0; box-shadow:0 1px 6px rgba(0,0,0,0.05);
        ">
            <p style="color:#94A3B8; font-size:0.78rem; margin:0; font-family:Outfit,sans-serif; font-weight:500;">{icon} {label}</p>
            <p style="color:{color}; font-size:1.9rem; font-weight:800; margin:4px 0 0; font-family:Outfit,sans-serif; line-height:1;">{value}</p>
        </div>
    """


# ── Login / Registration ───────────────────────────────────────────────────────

def _student_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("""
        <div style="max-width:480px; margin:1.5rem auto 0; text-align:center;">
            <h2 style="color:#0F172A; margin-bottom:0.25rem;">Student Sign In</h2>
            <p style="color:#64748B; font-family:Outfit,sans-serif; margin-top:0;">Look at your camera to log in instantly with Face ID.</p>
        </div>
    """, unsafe_allow_html=True)

    show_registration = False
    photo_source = st.camera_input("Position your face in the center")

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner('Scanning with AI...'):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning('No face detected. Make sure your face is clearly visible.')
            elif num_faces > 1:
                st.warning('Multiple faces detected. Only one student can log in at a time.')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    student = get_student_by_id(student_id)  # direct lookup — no full table scan

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome back, {student['name']}! 👋")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error('Profile not found. Please register below.')
                        show_registration = True
                else:
                    st.info('Face not recognized. Are you new? Register below.')
                    show_registration = True

    if show_registration:
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("""
                <h3 style="margin:0 0 0.25rem; color:#0F172A;">Create your profile</h3>
                <p style="color:#64748B; font-size:0.88rem; margin-bottom:1rem; font-family:Outfit,sans-serif;">Your face photo above will be saved for future logins.</p>
            """, unsafe_allow_html=True)

            new_name = st.text_input("Full Name", placeholder='e.g. Hamza Rizvi')

            st.markdown("""
                <p style="color:#64748B; font-size:0.85rem; margin:0.75rem 0 0.25rem; font-family:Outfit,sans-serif;">
                    <b>Optional:</b> Voice Enrollment — enables voice-based attendance.
                </p>
            """, unsafe_allow_html=True)

            audio_data = None
            try:
                audio_data = st.audio_input('Record a short phrase, e.g. "I am present, my name is …"')
            except Exception:
                st.caption('Audio input unavailable on this device.')

            if st.button('Create Account', type='primary', width='stretch'):
                if not new_name:
                    st.warning('Please enter your name.')
                else:
                    with st.spinner('Creating profile...'):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = get_voice_embedding(audio_data.read()) if audio_data else None
                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f"Profile created! Welcome, {new_name}! 🎉")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("Couldn't capture your facial features. Try retaking the photo.")

    footer_dashboard()
