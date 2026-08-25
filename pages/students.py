"""
Student Management Page — Full CRUD with search, filter, pagination.
"""

import streamlit as st
import pandas as pd
from utils.ui_helpers import (
    inject_css, section_header, require_auth, require_role,
    risk_badge, show_success, show_error, DEPARTMENTS
)
from database.services.data_service import DataService


def render():
    inject_css()
    if not require_role("Admin", "Faculty"):
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        👨‍🎓 Student Management
    </h1>
    """, unsafe_allow_html=True)

    # ─── Controls Row ─────────────────────────────────────────────
    ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns([2, 1.5, 1, 1, 1.2])

    with ctrl1:
        search = st.text_input("🔍 Search", placeholder="Name, ID, or email...", label_visibility="collapsed")
    with ctrl2:
        dept_filter = st.selectbox("Department", ["All"] + DEPARTMENTS, key="stu_dept")
    with ctrl3:
        year_filter = st.selectbox("Year", [0, 1, 2, 3, 4], format_func=lambda x: "All" if x == 0 else f"Year {x}", key="stu_year")
    with ctrl4:
        risk_filter = st.selectbox("Risk", ["All", "Low", "Medium", "High"], key="stu_risk")
    with ctrl5:
        if st.button("➕ Add Student", use_container_width=True, type="primary"):
            st.session_state["show_add_student"] = True

    # ─── Add Student Form ─────────────────────────────────────────
    if st.session_state.get("show_add_student", False):
        section_header("➕ Add New Student")
        with st.form("add_student_form", clear_on_submit=True):
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                new_sid = st.number_input("Student ID", value=DataService.get_next_student_id(), min_value=1)
                new_name = st.text_input("Student Name")
                new_gender = st.selectbox("Gender", ["Male", "Female"])
                new_dept = st.selectbox("Department", DEPARTMENTS, key="new_dept")
            with ac2:
                new_reg = st.text_input("Register Number")
                new_email = st.text_input("Email")
                new_phone = st.text_input("Phone")
                new_course = st.text_input("Course", value=f"B.E. {DEPARTMENTS[0]}")
            with ac3:
                new_year = st.selectbox("Year", [1, 2, 3, 4], key="new_year")
                new_sem = st.selectbox("Semester", list(range(1, 9)), key="new_sem")
                new_section = st.selectbox("Section", ["A", "B", "C"], key="new_sec")
                new_ay = st.selectbox("Academic Year", ["2024-2025", "2025-2026"], key="new_ay")

            fc1, fc2 = st.columns(2)
            with fc1:
                submitted = st.form_submit_button("💾 Save Student", use_container_width=True, type="primary")
            with fc2:
                cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)

            if submitted:
                if not new_name or not new_email or not new_reg:
                    show_error("Name, Email, and Register Number are required.")
                else:
                    try:
                        DataService.create_student({
                            "student_id": new_sid,
                            "register_number": new_reg,
                            "student_name": new_name,
                            "email": new_email,
                            "phone": new_phone,
                            "gender": new_gender,
                            "department": new_dept,
                            "course": new_course,
                            "year": new_year,
                            "semester": new_sem,
                            "section": new_section,
                            "academic_year": new_ay,
                            "previous_gpa": 0, "previous_percentage": 0,
                            "internal_marks": 0, "assignment_score": 0,
                            "quiz_score": 0, "midterm_score": 0,
                            "final_exam_score": 0, "classes_held": 0,
                            "classes_attended": 0, "attendance_percentage": 0,
                            "study_hours_per_day": 0, "assignment_completion_rate": 0,
                            "online_learning_hours": 0, "library_usage": 0,
                            "participation_score": 0, "final_score": 0,
                            "grade": "NA", "pass_fail": "NA", "risk_level": "Medium",
                        })
                        show_success(f"Student '{new_name}' added successfully!")
                        st.session_state["show_add_student"] = False
                        st.rerun()
                    except Exception as e:
                        show_error(f"Failed to add student: {e}")
            if cancelled:
                st.session_state["show_add_student"] = False
                st.rerun()

    # ─── Pagination ───────────────────────────────────────────────
    page_size = 20
    page_num = st.session_state.get("stu_page", 1)

    # ─── Fetch Data ───────────────────────────────────────────────
    try:
        students, total = DataService.get_students(
            offset=(page_num - 1) * page_size,
            limit=page_size,
            search=search if search else None,
            department=dept_filter,
            year=year_filter,
            risk_level=risk_filter,
            sort_by="student_id",
            sort_order="asc",
        )
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    total_pages = max(1, (total + page_size - 1) // page_size)

    st.markdown(f"<div style='color:#94a3b8;font-size:13px;margin:8px 0;'>Showing {len(students)} of {total} students</div>", unsafe_allow_html=True)

    # ─── Student Table ────────────────────────────────────────────
    if not students:
        st.info("No students found matching the criteria.")
    else:
        # Edit / Delete state
        edit_id = st.session_state.get("edit_student_id")
        delete_id = st.session_state.get("delete_student_id")

        for s in students:
            with st.container():
                cols = st.columns([0.5, 2, 2, 0.8, 0.8, 1, 1, 1.2])
                cols[0].markdown(f"**{s.student_id}**")
                cols[1].markdown(f"**{s.student_name}**")
                cols[2].markdown(f"{s.department}")
                cols[3].markdown(f"Y{s.year}")
                cols[4].markdown(f"S{s.semester}")
                cols[5].markdown(f"{s.attendance_percentage or 0:.1f}%")
                cols[6].markdown(f"{s.final_score or 0:.1f}")
                # Risk badge
                risk = s.risk_level or "Medium"
                cols[7].markdown(risk_badge(risk), unsafe_allow_html=True)

                # Action buttons
                act1, act2, act3 = st.columns([1, 1, 1])
                with act1:
                    if st.button("👁️ View", key=f"view_{s.student_id}", use_container_width=True):
                        st.session_state.selected_student_id = s.student_id
                        st.rerun()
                with act2:
                    if st.button("✏️ Edit", key=f"edit_{s.student_id}", use_container_width=True):
                        st.session_state["edit_student_id"] = s.student_id
                        st.rerun()
                with act3:
                    if st.button("🗑️ Delete", key=f"del_{s.student_id}", use_container_width=True):
                        st.session_state["delete_student_id"] = s.student_id
                        st.rerun()

                st.markdown("---")

        # ─── Edit Modal ────────────────────────────────────────
        if edit_id:
            student = DataService.get_student(edit_id)
            if student:
                section_header(f"✏️ Edit Student: {student.student_name}")
                with st.form(f"edit_form_{edit_id}", clear_on_submit=False):
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        ed_name = st.text_input("Name", value=student.student_name)
                        ed_email = st.text_input("Email", value=student.email)
                        ed_phone = st.text_input("Phone", value=student.phone or "")
                        ed_gender = st.selectbox("Gender", ["Male", "Female"],
                                                 index=0 if student.gender == "Male" else 1)
                    with ec2:
                        ed_dept = st.selectbox("Department", DEPARTMENTS,
                                               index=DEPARTMENTS.index(student.department) if student.department in DEPARTMENTS else 0)
                        ed_year = st.selectbox("Year", [1, 2, 3, 4], index=(student.year or 1) - 1)
                        ed_sem = st.selectbox("Semester", list(range(1, 9)), index=(student.semester or 1) - 1)
                        ed_section = st.selectbox("Section", ["A", "B", "C"],
                                                  index=["A", "B", "C"].index(student.section) if student.section in ["A", "B", "C"] else 0)
                    with ec3:
                        ed_gpa = st.number_input("Previous GPA", value=float(student.previous_gpa or 0), min_value=0.0, max_value=10.0, step=0.1)
                        ed_study = st.number_input("Study Hours/Day", value=float(student.study_hours_per_day or 0), min_value=0.0, max_value=16.0, step=0.5)
                        ed_participation = st.number_input("Participation Score", value=float(student.participation_score or 0), min_value=0.0, max_value=100.0)
                        ed_assign_rate = st.number_input("Assignment Completion %", value=float(student.assignment_completion_rate or 0), min_value=0.0, max_value=100.0)

                    efc1, efc2 = st.columns(2)
                    with efc1:
                        save = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                    with efc2:
                        cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

                    if save:
                        try:
                            DataService.update_student(edit_id, {
                                "student_name": ed_name,
                                "email": ed_email,
                                "phone": ed_phone,
                                "gender": ed_gender,
                                "department": ed_dept,
                                "year": ed_year,
                                "semester": ed_sem,
                                "section": ed_section,
                                "previous_gpa": ed_gpa,
                                "study_hours_per_day": ed_study,
                                "participation_score": ed_participation,
                                "assignment_completion_rate": ed_assign_rate,
                            })
                            show_success("Student updated successfully!")
                            st.session_state["edit_student_id"] = None
                            st.rerun()
                        except Exception as e:
                            show_error(f"Update failed: {e}")
                    if cancel:
                        st.session_state["edit_student_id"] = None
                        st.rerun()

        # ─── Delete Confirmation ──────────────────────────────
        if delete_id:
            student = DataService.get_student(delete_id)
            if student:
                st.warning(f"⚠️ Are you sure you want to delete **{student.student_name}** (ID: {delete_id})?")
                dc1, dc2 = st.columns(2)
                with dc1:
                    if st.button("🗑️ Confirm Delete", key="confirm_del", type="primary", use_container_width=True):
                        try:
                            DataService.delete_student(delete_id)
                            show_success(f"Student '{student.student_name}' has been archived.")
                            st.session_state["delete_student_id"] = None
                            st.rerun()
                        except Exception as e:
                            show_error(f"Delete failed: {e}")
                with dc2:
                    if st.button("❌ Cancel", key="cancel_del", use_container_width=True):
                        st.session_state["delete_student_id"] = None
                        st.rerun()

    # ─── Pagination Controls ─────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    pc1, pc2, pc3, pc4, pc5 = st.columns([1, 1, 2, 1, 1])
    with pc1:
        if st.button("⏮ First", disabled=(page_num <= 1), use_container_width=True):
            st.session_state["stu_page"] = 1
            st.rerun()
    with pc2:
        if st.button("◀ Prev", disabled=(page_num <= 1), use_container_width=True):
            st.session_state["stu_page"] = page_num - 1
            st.rerun()
    with pc3:
        st.markdown(f"<div style='text-align:center;padding:8px;color:#94a3b8;'>Page {page_num} of {total_pages}</div>", unsafe_allow_html=True)
    with pc4:
        if st.button("Next ▶", disabled=(page_num >= total_pages), use_container_width=True):
            st.session_state["stu_page"] = page_num + 1
            st.rerun()
    with pc5:
        if st.button("Last ⏭", disabled=(page_num >= total_pages), use_container_width=True):
            st.session_state["stu_page"] = total_pages
            st.rerun()
