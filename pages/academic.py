"""
Academic Performance Page — CRUD for academic records.
"""

import streamlit as st
import pandas as pd
from utils.ui_helpers import (
    inject_css, section_header, require_auth, require_role,
    show_success, show_error
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
        📊 Academic Performance
    </h1>
    """, unsafe_allow_html=True)

    # Filters
    fc1, fc2, fc3 = st.columns([1.5, 1.5, 1])
    with fc1:
        student_id_input = st.number_input("Student ID", min_value=0, value=0, key="acad_sid",
                                           help="Enter student ID to filter records (0 = all)")
    with fc2:
        module_id_input = st.number_input("Module ID", min_value=0, value=0, key="acad_mid",
                                          help="Enter module ID to filter records (0 = all)")
    with fc3:
        if role in ["Admin", "Faculty"]:
            if st.button("➕ Add Record", use_container_width=True, type="primary"):
                st.session_state["show_add_record"] = True

    # Add Record Form
    if st.session_state.get("show_add_record", False) and role in ["Admin", "Faculty"]:
        section_header("➕ Add Academic Record")
        with st.form("add_record_form", clear_on_submit=True):
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                r_sid = st.number_input("Student ID", min_value=1, key="r_sid")
                r_mid = st.number_input("Module ID", min_value=1, key="r_mid")
                r_att = st.number_input("Attendance %", min_value=0.0, max_value=100.0, value=75.0)
            with rc2:
                r_internal = st.number_input("Internal Marks (0-40)", min_value=0.0, max_value=40.0, value=20.0)
                r_assign = st.number_input("Assignment Marks (0-25)", min_value=0.0, max_value=25.0, value=15.0)
                r_quiz = st.number_input("Quiz Marks (0-20)", min_value=0.0, max_value=20.0, value=10.0)
            with rc3:
                r_midterm = st.number_input("Midterm Marks (0-50)", min_value=0.0, max_value=50.0, value=25.0)
                r_final = st.number_input("Final Exam Marks (0-75)", min_value=0.0, max_value=75.0, value=40.0)

            # Auto-calculate
            total = round((r_internal / 40) * 20 + (r_assign / 25) * 10 + (r_quiz / 20) * 10 + (r_midterm / 50) * 25 + (r_final / 75) * 35, 2)
            if total >= 90: grade = "O"
            elif total >= 80: grade = "A+"
            elif total >= 70: grade = "A"
            elif total >= 60: grade = "B+"
            elif total >= 50: grade = "B"
            elif total >= 40: grade = "C"
            else: grade = "F"
            result = "Pass" if total >= 40 else "Fail"

            st.info(f"📊 Calculated: Total = {total}, Grade = {grade}, Result = {result}")

            fc1, fc2 = st.columns(2)
            with fc1:
                if st.form_submit_button("💾 Save Record", use_container_width=True, type="primary"):
                    try:
                        DataService.create_student_module({
                            "student_id": r_sid, "module_id": r_mid,
                            "attendance_percentage": r_att,
                            "internal_marks": r_internal, "assignment_marks": r_assign,
                            "quiz_marks": r_quiz, "midterm_marks": r_midterm,
                            "final_exam_marks": r_final, "total_marks": total,
                            "grade": grade, "result": result,
                        })
                        show_success("Academic record added!")
                        st.session_state["show_add_record"] = False
                        st.rerun()
                    except Exception as e:
                        show_error(f"Failed: {e}")
            with fc2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state["show_add_record"] = False
                    st.rerun()

    # Fetch records
    try:
        records, total = DataService.get_student_modules(
            student_id=student_id_input if student_id_input > 0 else None,
            module_id=module_id_input if module_id_input > 0 else None,
            offset=0, limit=50,
        )
    except Exception as e:
        st.error(f"Error: {e}")
        return

    st.markdown(f"<div style='color:#94a3b8;font-size:13px;margin:8px 0;'>{total} records found</div>", unsafe_allow_html=True)

    if records:
        data = []
        for r in records:
            data.append({
                "ID": r.id, "Student": r.student_id, "Module": r.module_id,
                "Internal": r.internal_marks, "Assignment": r.assignment_marks,
                "Quiz": r.quiz_marks, "Midterm": r.midterm_marks,
                "Final": r.final_exam_marks, "Total": r.total_marks,
                "Grade": r.grade, "Result": r.result,
                "Attendance": f"{r.attendance_percentage:.1f}%",
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

        # Edit / Delete
        if role in ["Admin", "Faculty"]:
            section_header("Edit / Delete Record")
            ec1, ec2 = st.columns([1, 3])
            with ec1:
                record_id = st.number_input("Record ID to edit/delete", min_value=1, key="edit_rec_id")
            with ec2:
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("✏️ Edit Record", key="btn_edit_rec", use_container_width=True):
                        st.session_state["editing_record_id"] = record_id
                        st.rerun()
                with bc2:
                    if st.button("🗑️ Delete Record", key="btn_del_rec", use_container_width=True):
                        st.session_state["deleting_record_id"] = record_id
                        st.rerun()

        # Edit Form
        edit_rid = st.session_state.get("editing_record_id")
        if edit_rid:
            rec = DataService.get_student_module_record(edit_rid)
            if rec:
                with st.form(f"edit_rec_form_{edit_rid}"):
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        e_internal = st.number_input("Internal", value=float(rec.internal_marks or 0), max_value=40.0)
                        e_assign = st.number_input("Assignment", value=float(rec.assignment_marks or 0), max_value=25.0)
                    with ec2:
                        e_quiz = st.number_input("Quiz", value=float(rec.quiz_marks or 0), max_value=20.0)
                        e_midterm = st.number_input("Midterm", value=float(rec.midterm_marks or 0), max_value=50.0)
                    with ec3:
                        e_final = st.number_input("Final Exam", value=float(rec.final_exam_marks or 0), max_value=75.0)
                        e_att = st.number_input("Attendance %", value=float(rec.attendance_percentage or 0), max_value=100.0)

                    fc1, fc2 = st.columns(2)
                    with fc1:
                        if st.form_submit_button("💾 Update", use_container_width=True, type="primary"):
                            DataService.update_student_module(edit_rid, {
                                "internal_marks": e_internal, "assignment_marks": e_assign,
                                "quiz_marks": e_quiz, "midterm_marks": e_midterm,
                                "final_exam_marks": e_final, "attendance_percentage": e_att,
                            })
                            show_success("Record updated!")
                            st.session_state["editing_record_id"] = None
                            st.rerun()
                    with fc2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state["editing_record_id"] = None
                            st.rerun()

        # Delete Confirmation
        del_rid = st.session_state.get("deleting_record_id")
        if del_rid:
            st.warning(f"⚠️ Delete record #{del_rid}?")
            dc1, dc2 = st.columns(2)
            with dc1:
                if st.button("🗑️ Confirm", key="confirm_del_rec", type="primary"):
                    DataService.delete_student_module(del_rid)
                    show_success("Record deleted.")
                    st.session_state["deleting_record_id"] = None
                    st.rerun()
            with dc2:
                if st.button("❌ Cancel", key="cancel_del_rec"):
                    st.session_state["deleting_record_id"] = None
                    st.rerun()
    else:
        st.info("No academic records found.")
