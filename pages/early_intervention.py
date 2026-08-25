"""
Early Intervention Page — Track and manage interventions for at-risk students.
"""

import streamlit as st
import pandas as pd
from utils.ui_helpers import (
    inject_css, section_header, require_auth, require_role,
    show_success, show_error, kpi_card, COLORS
)
from database.services.data_service import DataService
from database.repositories.intervention_repo import VALID_STATUSES
from ml.predict import Predictor
from ml.feature_engineering import get_risk_factors, generate_recommendations


def render():
    inject_css()
    if not require_role("Admin", "Faculty"):
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        🚨 Early Intervention Center
    </h1>
    """, unsafe_allow_html=True)

    # KPIs
    try:
        status_counts = DataService.get_intervention_status_counts()
    except Exception:
        status_counts = {}

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("⏳", status_counts.get("Pending", 0), "Pending")
    with c2: kpi_card("📞", status_counts.get("Contacted", 0), "Contacted")
    with c3: kpi_card("🚀", status_counts.get("Intervention Started", 0), "In Progress")
    with c4: kpi_card("👁️", status_counts.get("Monitoring", 0), "Monitoring")
    with c5: kpi_card("✅", status_counts.get("Resolved", 0), "Resolved")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Controls
    ctrl1, ctrl2, ctrl3 = st.columns([1.5, 1.5, 1])
    with ctrl1:
        status_filter = st.selectbox("Filter by Status", ["All"] + VALID_STATUSES, key="intv_status")
    with ctrl2:
        risk_filter = st.selectbox("Filter by Risk", ["All", "High", "Medium", "Low"], key="intv_risk")
    with ctrl3:
        if st.button("➕ Create Intervention", use_container_width=True, type="primary"):
            st.session_state["show_create_intv"] = True

    # Create Intervention
    if st.session_state.get("show_create_intv", False):
        section_header("➕ Create New Intervention")
        with st.form("create_intv_form", clear_on_submit=True):
            ic1, ic2 = st.columns(2)
            with ic1:
                intv_sid = st.number_input("Student ID", min_value=1, key="intv_sid")
                intv_mod = st.number_input("Module ID (optional, 0=none)", min_value=0, value=0, key="intv_mid")

            with ic2:
                intv_risk = st.selectbox("Risk Level", ["High", "Medium", "Low"], key="intv_risk_level")
                intv_status = st.selectbox("Initial Status", VALID_STATUSES, key="intv_init_status")

            # Auto-populate from student data
            student = DataService.get_student(intv_sid) if intv_sid > 0 else None
            if student:
                factors = get_risk_factors({
                    "attendance_percentage": student.attendance_percentage,
                    "study_hours_per_day": student.study_hours_per_day,
                    "assignment_completion_rate": student.assignment_completion_rate,
                    "previous_gpa": student.previous_gpa,
                    "participation_score": student.participation_score,
                    "internal_marks": student.internal_marks,
                    "midterm_score": student.midterm_score,
                })
                main_factor = factors[0][0] if factors else "Multiple academic risk factors"
                recs = generate_recommendations({
                    "attendance_percentage": student.attendance_percentage,
                    "study_hours_per_day": student.study_hours_per_day,
                    "assignment_completion_rate": student.assignment_completion_rate,
                    "previous_gpa": student.previous_gpa,
                    "participation_score": student.participation_score,
                    "internal_marks": student.internal_marks,
                    "midterm_score": student.midterm_score,
                }, factors)
                rec_text = recs[0]["recommendation"] if recs else "Schedule meeting with academic advisor."
            else:
                main_factor = ""
                rec_text = ""

            intv_factor = st.text_input("Main Risk Factor", value=main_factor)
            intv_rec = st.text_area("Recommendation", value=rec_text)
            intv_score = st.number_input("Predicted Score", value=float(student.final_score or 0) if student else 0.0)
            intv_notes = st.text_area("Notes", placeholder="Additional notes...")

            fc1, fc2 = st.columns(2)
            with fc1:
                if st.form_submit_button("💾 Create", use_container_width=True, type="primary"):
                    try:
                        DataService.create_intervention({
                            "student_id": intv_sid,
                            "module_id": intv_mod if intv_mod > 0 else None,
                            "risk_level": intv_risk,
                            "predicted_score": intv_score,
                            "main_risk_factor": intv_factor,
                            "recommendation": intv_rec,
                            "status": intv_status,
                            "notes": intv_notes,
                            "assigned_to": st.session_state.get("user_name", ""),
                        })
                        show_success("Intervention created!")
                        st.session_state["show_create_intv"] = False
                        st.rerun()
                    except Exception as e:
                        show_error(f"Failed: {e}")
            with fc2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state["show_create_intv"] = False
                    st.rerun()

    # Interventions list
    section_header("📋 Interventions")
    try:
        interventions, total = DataService.get_interventions(
            status=status_filter, risk_level=risk_filter,
            offset=0, limit=50,
        )
    except Exception as e:
        st.error(f"Error: {e}")
        return

    if not interventions:
        st.info("No interventions found.")
    else:
        for intv in interventions:
            student = DataService.get_student(intv.student_id)
            student_name = student.student_name if student else f"Student #{intv.student_id}"

            status_colors = {
                "Pending": "#f59e0b", "Contacted": "#3b82f6",
                "Intervention Started": "#a78bfa", "Monitoring": "#06b6d4",
                "Resolved": "#10b981",
            }
            s_color = status_colors.get(intv.status, "#94a3b8")

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(30,30,63,0.8),rgba(45,45,94,0.8));
                 border:1px solid rgba(99,102,241,0.15);border-radius:12px;padding:16px;margin:8px 0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <strong style="font-size:16px;">{student_name}</strong>
                        <span style="color:#94a3b8;font-size:12px;"> (ID: {intv.student_id})</span>
                    </div>
                    <span style="color:{s_color};font-weight:600;font-size:13px;
                          background:rgba({','.join(str(int(s_color[i:i+2],16)) for i in (1,3,5))},0.15);
                          padding:4px 12px;border-radius:12px;">{intv.status}</span>
                </div>
                <div style="color:#94a3b8;font-size:13px;margin-top:8px;">
                    Risk: <strong>{intv.risk_level}</strong> |
                    Predicted: <strong>{intv.predicted_score or 'N/A'}</strong> |
                    Factor: {intv.main_risk_factor or 'N/A'}
                </div>
                <div style="color:#7c8594;font-size:12px;margin-top:4px;">
                    {intv.recommendation or ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Update status inline
            uc1, uc2, uc3 = st.columns([2, 2, 1])
            with uc1:
                new_status = st.selectbox(
                    "Status", VALID_STATUSES, key=f"intv_st_{intv.id}",
                    index=VALID_STATUSES.index(intv.status) if intv.status in VALID_STATUSES else 0,
                )
            with uc2:
                new_notes = st.text_input("Notes", value=intv.notes or "", key=f"intv_notes_{intv.id}")
            with uc3:
                if st.button("💾 Update", key=f"intv_update_{intv.id}", use_container_width=True):
                    DataService.update_intervention_status(intv.id, new_status, new_notes)
                    show_success(f"Intervention #{intv.id} updated.")
                    st.rerun()
