"""
Attendance Page — CRUD for attendance records.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.ui_helpers import (
    inject_css, section_header, require_auth, require_role,
    show_success, show_error, kpi_card, PLOTLY_LAYOUT, COLORS
)
from database.services.data_service import DataService


def render():
    inject_css()
    if not require_auth():
        return

    role = st.session_state.user_role

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        📅 Attendance Management
    </h1>
    """, unsafe_allow_html=True)

    # For students, show only their own attendance
    if role == "Student":
        # Find student record by user email
        st.info("Showing your attendance records.")
        return

    # Admin/Faculty view
    fc1, fc2 = st.columns([1.5, 1])
    with fc1:
        student_id = st.number_input("Student ID", min_value=0, value=0, key="att_sid",
                                     help="Enter student ID (0 = browse)")
    with fc2:
        if st.button("📋 Update Attendance", use_container_width=True, type="primary"):
            st.session_state["show_att_form"] = True

    # Update Attendance Form
    if st.session_state.get("show_att_form", False):
        section_header("📋 Update Student Attendance")
        with st.form("att_form", clear_on_submit=True):
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                a_sid = st.number_input("Student ID", min_value=1, key="a_sid")
            with ac2:
                a_held = st.number_input("Classes Held", min_value=0, value=60, key="a_held")
            with ac3:
                a_attended = st.number_input("Classes Attended", min_value=0, value=45, key="a_att")

            # Validate
            if a_attended > a_held and a_held > 0:
                st.error("❌ Attended cannot exceed classes held!")
                att_pct = 0
            elif a_held > 0:
                att_pct = round(a_attended / a_held * 100, 2)
            else:
                att_pct = 0

            st.info(f"📊 Calculated Attendance: {att_pct}%")

            fc1, fc2 = st.columns(2)
            with fc1:
                if st.form_submit_button("💾 Save", use_container_width=True, type="primary"):
                    if a_attended > a_held:
                        show_error("Attended cannot exceed classes held.")
                    else:
                        try:
                            DataService.update_student(a_sid, {
                                "classes_held": a_held,
                                "classes_attended": a_attended,
                                "attendance_percentage": att_pct,
                            })
                            show_success(f"Attendance updated for student {a_sid}")
                            st.session_state["show_att_form"] = False
                            st.rerun()
                        except Exception as e:
                            show_error(f"Failed: {e}")
            with fc2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state["show_att_form"] = False
                    st.rerun()

    # Show student attendance if specific ID entered
    if student_id > 0:
        student = DataService.get_student(student_id)
        if student:
            section_header(f"📅 {student.student_name}'s Attendance")
            c1, c2, c3 = st.columns(3)
            with c1:
                kpi_card("📅", student.classes_held or 0, "Classes Held")
            with c2:
                kpi_card("✅", student.classes_attended or 0, "Attended")
            with c3:
                kpi_card("📊", f"{student.attendance_percentage or 0:.1f}%", "Attendance %")

            # Module-wise attendance
            records = DataService.get_records_for_student(student_id)
            if records:
                att_data = []
                for r in records:
                    mod = DataService.get_module(r.module_id)
                    att_data.append({
                        "Module": mod.module_name if mod else f"Module {r.module_id}",
                        "Attendance %": r.attendance_percentage,
                    })
                df_att = pd.DataFrame(att_data)
                fig = go.Figure(data=[go.Bar(
                    x=df_att['Module'], y=df_att['Attendance %'],
                    marker=dict(
                        color=[COLORS["danger"] if a < 60 else COLORS["warning"] if a < 75 else COLORS["success"]
                               for a in df_att['Attendance %']],
                    ),
                    text=df_att['Attendance %'].round(1),
                    textposition="outside",
                )])
                fig.update_layout(
                    title="Module-wise Attendance",
                    yaxis_title="Attendance %",
                    **PLOTLY_LAYOUT, height=380, xaxis_tickangle=-30,
                )
                fig.add_hline(y=75, line_dash="dash", line_color=COLORS["warning"],
                              annotation_text="75% Threshold")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"Student with ID {student_id} not found.")
    else:
        # Overview: attendance distribution
        section_header("📊 Attendance Overview")
        try:
            students_df = DataService.get_all_students_as_df()
            if students_df is not None and len(students_df) > 0:
                c1, c2 = st.columns(2)
                with c1:
                    fig = go.Figure(data=[go.Histogram(
                        x=students_df['attendance_percentage'],
                        nbinsx=20,
                        marker=dict(color=COLORS["primary"], line=dict(width=1, color='rgba(255,255,255,0.2)')),
                    )])
                    fig.update_layout(
                        title="Attendance Distribution",
                        xaxis_title="Attendance %", yaxis_title="Students",
                        **PLOTLY_LAYOUT, height=380,
                    )
                    fig.add_vline(x=75, line_dash="dash", line_color=COLORS["warning"],
                                  annotation_text="75% Threshold")
                    st.plotly_chart(fig, use_container_width=True)

                with c2:
                    below = (students_df['attendance_percentage'] < 75).sum()
                    above = (students_df['attendance_percentage'] >= 75).sum()
                    fig = go.Figure(data=[go.Pie(
                        labels=["Below 75%", "75% & Above"],
                        values=[below, above],
                        hole=0.55,
                        marker=dict(colors=[COLORS["danger"], COLORS["success"]]),
                    )])
                    fig.update_layout(
                        title="Attendance Compliance",
                        **PLOTLY_LAYOUT, height=380,
                    )
                    st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("No attendance data available.")
