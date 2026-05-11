import streamlit as st
import numpy as np
import pandas as pd
import time
from datetime import datetime

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists, create_teacher, teacher_login,
    get_teacher_subjects, get_attendance_for_teacher,
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
from src.database.config import supabase
from src.components.dialog_voice_attendance import voice_attendance_dialog


def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


# ── Dashboard ────────────────────────────────────────────────────────────────

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    teacher_id = teacher_data['teacher_id']

    # Header bar
    c1, c2 = st.columns([1, 2], vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        info_col, btn_col = st.columns([3, 1])
        with info_col:
            st.markdown(f"""
                <p style="color:#94A3B8; margin:0; font-size:0.82rem; font-family:Outfit,sans-serif;">Welcome back</p>
                <p style="color:#0F172A; font-weight:700; font-size:1.05rem; margin:0; font-family:Outfit,sans-serif;">{teacher_data['name']}</p>
            """, unsafe_allow_html=True)
        with btn_col:
            if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
                st.session_state['is_logged_in'] = False
                del st.session_state.teacher_data
                st.rerun()

    st.divider()

    # Quick stats
    subjects = get_teacher_subjects(teacher_id)
    total_subjects = len(subjects)
    total_students = sum(s.get('total_students', 0) for s in subjects)
    total_classes = sum(s.get('total_classes', 0) for s in subjects)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(_stat_card("📚", "Subjects", total_subjects, "#6366F1"), unsafe_allow_html=True)
    with s2:
        st.markdown(_stat_card("👥", "Students", total_students, "#8B5CF6"), unsafe_allow_html=True)
    with s3:
        st.markdown(_stat_card("📅", "Sessions", total_classes, "#06B6D4"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # Tab nav
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    tab1, tab2, tab3 = st.columns(3, gap='small')
    with tab1:
        t = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance', type=t, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()
    with tab2:
        t = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('My Subjects', type=t, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()
    with tab3:
        t = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Records', type=t, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance(subjects)
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects(teacher_id, subjects)
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records(teacher_id)

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


# ── Take Attendance tab ───────────────────────────────────────────────────────

def teacher_tab_take_attendance(subjects):
    st.header('Take AI Attendance')

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    if not subjects:
        st.warning('You haven\'t created any subjects yet. Create one in My Subjects.')
        return

    subject_options = {f"{s['name']} — {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))
    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.markdown("**Added Photos**")
        gallery_cols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, width='stretch', caption=f'Photo {idx + 1}')

    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear Photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}
                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)
                    if detected:
                        for sid in detected.keys():
                            all_detected_ids.setdefault(int(sid), []).append(f"Photo {idx + 1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course.')
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0
                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "—",
                            "Status": "✅ Present" if is_present else "❌ Absent",
                        })
                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present),
                        })

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)


# ── Manage Subjects tab ───────────────────────────────────────────────────────

def teacher_tab_manage_subjects(teacher_id, subjects):
    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        st.header('My Subjects')
    with col2:
        if st.button('+ New Subject', type='primary', width='stretch'):
            create_subject_dialog(teacher_id)

    if not subjects:
        st.markdown("""
            <div style="text-align:center; padding:3rem 1rem; background:white; border-radius:16px; border:1px solid #E2E8F0; margin-top:1rem;">
                <p style="font-size:2rem; margin:0;">📚</p>
                <p style="color:#64748B; font-size:0.95rem; margin:0.5rem 0 0; font-family:Outfit,sans-serif;">No subjects yet. Create your first one above.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    cols = st.columns(2, gap='medium')
    for i, sub in enumerate(subjects):
        stats = [
            ("👥", "Students", sub['total_students']),
            ("📅", "Classes", sub['total_classes']),
        ]

        def share_btn(sub=sub):
            if st.button(f"Share", key=f"share_{sub['subject_code']}", icon=":material/share:", type='tertiary'):
                share_subject_dialog(sub['name'], sub['subject_code'])

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=share_btn,
            )


# ── Attendance Records tab ────────────────────────────────────────────────────

def teacher_tab_attendance_records(teacher_id):
    st.header('Attendance Records')

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.markdown("""
            <div style="text-align:center; padding:3rem 1rem; background:white; border-radius:16px; border:1px solid #E2E8F0; margin-top:1rem;">
                <p style="font-size:2rem; margin:0;">📊</p>
                <p style="color:#64748B; font-size:0.95rem; margin:0.5rem 0 0; font-family:Outfit,sans-serif;">No attendance records yet.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    data = []
    for r in records:
        ts = r.get('timestamp')
        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False)),
        })

    df = pd.DataFrame(data)
    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(Present_Count=('is_present', 'sum'), Total_Count=('is_present', 'count'))
        .reset_index()
    )
    summary['Attendance'] = (
        "✅ " + summary['Present_Count'].astype(str) + " / " + summary['Total_Count'].astype(str)
    )
    display_df = (
        summary.sort_values(by='ts_group', ascending=False)
        [['Time', 'Subject', 'Subject Code', 'Attendance']]
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ── Auth ──────────────────────────────────────────────────────────────────────

def _auth_header():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()


def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def teacher_screen_login():
    _auth_header()

    st.markdown("""
        <div style="max-width:420px; margin:2rem auto 0;">
            <h2 style="color:#0F172A; margin-bottom:0.25rem;">Welcome back</h2>
            <p style="color:#64748B; font-family:Outfit,sans-serif; margin-top:0;">Sign in to your teacher account.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='max-width:420px; margin:0 auto;'>", unsafe_allow_html=True)
    teacher_username = st.text_input("Username", placeholder='e.g. ananya.roy')
    teacher_pass = st.text_input("Password", type='password', placeholder='Enter password')
    st.divider()

    btnc1, btnc2 = st.columns(2)
    with btnc1:
        if st.button('Sign In', icon=':material/passkey:', shortcut='control+enter', width='stretch', type='primary'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Welcome back! 👋")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Incorrect username or password.")
    with btnc2:
        if st.button('Create Account', type='secondary', width='stretch'):
            st.session_state.teacher_login_type = 'register'
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    footer_dashboard()


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required."
    if check_teacher_exists(teacher_username):
        return False, "Username already taken."
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords don't match."
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Account created! Sign in now."
    except Exception:
        return False, "Unexpected error. Please try again."


def teacher_screen_register():
    _auth_header()

    st.markdown("""
        <div style="max-width:420px; margin:2rem auto 0;">
            <h2 style="color:#0F172A; margin-bottom:0.25rem;">Create account</h2>
            <p style="color:#64748B; font-family:Outfit,sans-serif; margin-top:0;">Set up your teacher profile.</p>
        </div>
    """, unsafe_allow_html=True)

    teacher_username = st.text_input("Username", placeholder='e.g. ananya.roy')
    teacher_name = st.text_input("Full Name", placeholder='e.g. Ananya Roy')
    teacher_pass = st.text_input("Password", type='password', placeholder='Choose a password')
    teacher_pass_confirm = st.text_input("Confirm Password", type='password', placeholder='Repeat password')

    st.divider()

    btnc1, btnc2 = st.columns(2)
    with btnc1:
        if st.button('Register', icon=':material/passkey:', shortcut='control+enter', width='stretch', type='primary'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)
    with btnc2:
        if st.button('Sign In Instead', type='secondary', width='stretch'):
            st.session_state.teacher_login_type = 'login'
            st.rerun()

    footer_dashboard()
