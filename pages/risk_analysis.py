"""
Risk Analysis Page — Identify and visualize at-risk students.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.ui_helpers import (
    inject_css, section_header, require_auth,
    kpi_card, risk_badge, PLOTLY_LAYOUT, COLORS
)
from database.services.data_service import DataService
from ml.feature_engineering import get_risk_factors


def render():
    inject_css()
    if not require_auth():
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        ⚠️ Risk Analysis
    </h1>
    """, unsafe_allow_html=True)

    try:
        students_df = DataService.get_all_students_as_df()
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    if students_df is None or len(students_df) == 0:
        st.info("No student data available.")
        return

    # KPIs
    high = (students_df['risk_level'] == 'High').sum()
    medium = (students_df['risk_level'] == 'Medium').sum()
    low = (students_df['risk_level'] == 'Low').sum()
    total = len(students_df)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("🔴", high, "High Risk")
    with c2: kpi_card("🟡", medium, "Medium Risk")
    with c3: kpi_card("🟢", low, "Low Risk")
    with c4: kpi_card("📊", f"{high/total*100:.1f}%", "High Risk %")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure(data=[go.Pie(
            labels=["Low", "Medium", "High"],
            values=[low, medium, high],
            hole=0.55,
            marker=dict(colors=[COLORS["success"], COLORS["warning"], COLORS["danger"]]),
            textinfo="label+value+percent",
        )])
        fig.update_layout(title="Risk Distribution", **PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        risk_dept = students_df.groupby(['department', 'risk_level']).size().reset_index(name='count')
        fig = px.bar(risk_dept, x='department', y='count', color='risk_level',
                     color_discrete_map={"Low": COLORS["success"], "Medium": COLORS["warning"], "High": COLORS["danger"]},
                     barmode='stack', labels={"department": "Department", "count": "Students"})
        fig.update_layout(title="Risk by Department", **PLOTLY_LAYOUT, height=380, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    # High-risk students table
    section_header("🔴 High Risk Students")
    high_risk = students_df[students_df['risk_level'] == 'High'].sort_values('final_score')

    if len(high_risk) == 0:
        st.info("No high-risk students found. 🎉")
    else:
        display_cols = ['student_id', 'student_name', 'department', 'year',
                       'attendance_percentage', 'study_hours_per_day',
                       'assignment_completion_rate', 'final_score', 'grade']
        display_cols = [c for c in display_cols if c in high_risk.columns]
        st.dataframe(
            high_risk[display_cols].head(30),
            use_container_width=True, hide_index=True,
        )

    # Risk factor analysis for a student
    section_header("🔍 Individual Risk Analysis")
    sid = st.number_input("Student ID", min_value=1, value=1, key="risk_sid")
    if st.button("Analyze Risk", key="analyze_risk", type="primary"):
        student = DataService.get_student(sid)
        if student:
            st.markdown(f"### {student.student_name}")
            st.markdown(risk_badge(student.risk_level or "Medium"), unsafe_allow_html=True)

            factors = get_risk_factors({
                "attendance_percentage": student.attendance_percentage,
                "study_hours_per_day": student.study_hours_per_day,
                "assignment_completion_rate": student.assignment_completion_rate,
                "previous_gpa": student.previous_gpa,
                "participation_score": student.participation_score,
                "internal_marks": student.internal_marks,
                "midterm_score": student.midterm_score,
            })

            if factors:
                for factor, value, severity in factors:
                    icon = "🔴" if severity == "critical" else "🟡"
                    st.markdown(f"{icon} **{factor}**: {value}")
            else:
                st.success("✅ No significant risk factors identified.")
        else:
            st.warning(f"Student {sid} not found.")
