"""
Recommendations Page — Personalized recommendations for students.
"""

import streamlit as st
from utils.ui_helpers import (
    inject_css, section_header, require_auth,
    kpi_card, COLORS
)
from database.services.data_service import DataService
from ml.feature_engineering import get_risk_factors, generate_recommendations


def render():
    inject_css()
    if not require_auth():
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        💡 Personalized Recommendations
    </h1>
    """, unsafe_allow_html=True)

    sid = st.number_input("Enter Student ID", min_value=1, value=1, key="rec_sid")

    if st.button("💡 Generate Recommendations", key="gen_rec", type="primary"):
        student = DataService.get_student(sid)
        if not student:
            st.error(f"Student {sid} not found.")
            return

        st.markdown(f"### {student.student_name}")
        st.markdown(f"{student.department} • Year {student.year} • Grade: {student.grade}")

        student_dict = {
            "attendance_percentage": student.attendance_percentage,
            "study_hours_per_day": student.study_hours_per_day,
            "assignment_completion_rate": student.assignment_completion_rate,
            "previous_gpa": student.previous_gpa,
            "participation_score": student.participation_score,
            "internal_marks": student.internal_marks,
            "midterm_score": student.midterm_score,
        }

        # Risk factors
        risk_factors = get_risk_factors(student_dict)

        if risk_factors:
            section_header("⚠️ Identified Risk Factors")
            for factor, value, severity in risk_factors:
                color = COLORS["danger"] if severity == "critical" else COLORS["warning"]
                icon = "🔴" if severity == "critical" else "🟡"
                st.markdown(f"""
                <div style="background:rgba({','.join(str(int(color[i:i+2],16)) for i in (1,3,5))},0.1);
                     border-left:3px solid {color};padding:10px 14px;border-radius:8px;margin:6px 0;">
                    {icon} <strong>{factor}</strong>: {value}
                </div>
                """, unsafe_allow_html=True)

        # Recommendations
        recommendations = generate_recommendations(student_dict, risk_factors)

        section_header("💡 Action Plan")
        for i, rec in enumerate(recommendations, 1):
            priority_colors = {"High": COLORS["danger"], "Medium": COLORS["warning"], "Low": COLORS["success"]}
            color = priority_colors.get(rec["priority"], COLORS["info"])
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(30,30,63,0.8),rgba(45,45,94,0.8));
                 border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:16px;margin:10px 0;">
                <div style="font-size:16px;margin-bottom:8px;">
                    {rec['icon']} <strong>#{i} {rec['area']}</strong>
                    <span style="float:right;font-size:11px;color:{color};font-weight:600;
                          text-transform:uppercase;background:rgba({','.join(str(int(color[i2:i2+2],16)) for i2 in (1,3,5))},0.15);
                          padding:3px 10px;border-radius:12px;">{rec['priority']} Priority</span>
                </div>
                <div style="color:#b0b8c8;font-size:14px;line-height:1.5;">{rec['recommendation']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Bulk recommendations for at-risk students
    st.markdown("---")
    section_header("📋 Bulk: High-Risk Students Needing Attention")
    if st.button("📋 Show High-Risk Students", key="bulk_rec"):
        try:
            students_df = DataService.get_all_students_as_df()
            if students_df is not None:
                high_risk = students_df[students_df['risk_level'] == 'High'].head(20)
                if len(high_risk) == 0:
                    st.success("No high-risk students found! 🎉")
                else:
                    for _, s in high_risk.iterrows():
                        factors = get_risk_factors(s.to_dict())
                        main_factor = factors[0][0] if factors else "Multiple factors"
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;align-items:center;
                             padding:10px 14px;border-bottom:1px solid rgba(99,102,241,0.1);">
                            <div>
                                <strong>{s.get('student_name', 'Unknown')}</strong>
                                <span style="color:#94a3b8;font-size:12px;"> — {s.get('department', '')}</span>
                            </div>
                            <div style="color:{COLORS['danger']};font-size:12px;">
                                Main Issue: {main_factor}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
