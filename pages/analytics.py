"""
Analytics Page — Interactive filtered charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.ui_helpers import (
    inject_css, section_header, require_auth,
    PLOTLY_LAYOUT, COLORS, DEPARTMENTS
)
from database.services.data_service import DataService


def render():
    inject_css()
    if not require_auth():
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        📈 Analytics Dashboard
    </h1>
    """, unsafe_allow_html=True)

    # Filters
    section_header("🔍 Filters")
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        dept = st.selectbox("Department", ["All"] + DEPARTMENTS, key="an_dept")
    with fc2:
        year = st.selectbox("Year", [0, 1, 2, 3, 4],
                            format_func=lambda x: "All" if x == 0 else f"Year {x}", key="an_year")
    with fc3:
        risk = st.selectbox("Risk Level", ["All", "Low", "Medium", "High"], key="an_risk")
    with fc4:
        ay = st.selectbox("Academic Year", ["All", "2024-2025", "2025-2026"], key="an_ay")

    # Fetch and filter data
    try:
        df = DataService.get_all_students_as_df()
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    if df is None or len(df) == 0:
        st.info("No data available.")
        return

    # Apply filters
    if dept != "All":
        df = df[df['department'] == dept]
    if year != 0:
        df = df[df['year'] == year]
    if risk != "All":
        df = df[df['risk_level'] == risk]
    if ay != "All":
        df = df[df['academic_year'] == ay]

    st.markdown(f"<div style='color:#94a3b8;font-size:13px;margin:8px 0;'>Filtered: {len(df)} students</div>", unsafe_allow_html=True)

    if len(df) == 0:
        st.warning("No students match the selected filters.")
        return

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(df, x='final_score', nbins=25, color='risk_level',
                          color_discrete_map={"Low": COLORS["success"], "Medium": COLORS["warning"], "High": COLORS["danger"]},
                          labels={"final_score": "Final Score", "risk_level": "Risk"})
        fig.update_layout(title="Score Distribution", **PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.box(df, x='department', y='final_score', color='department',
                     color_discrete_sequence=COLORS["palette"])
        fig.update_layout(title="Score by Department", **PLOTLY_LAYOUT, height=380,
                         showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig = px.scatter(df, x='attendance_percentage', y='final_score',
                        color='risk_level', size='study_hours_per_day',
                        color_discrete_map={"Low": COLORS["success"], "Medium": COLORS["warning"], "High": COLORS["danger"]},
                        opacity=0.6, hover_data=['student_name', 'department'],
                        labels={"attendance_percentage": "Attendance %", "final_score": "Final Score"})
        fig.update_layout(title="Attendance vs Performance (size=study hours)",
                         **PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.scatter(df, x='study_hours_per_day', y='final_score',
                        color='department', opacity=0.6, trendline="ols",
                        color_discrete_sequence=COLORS["palette"],
                        labels={"study_hours_per_day": "Study Hours/Day", "final_score": "Final Score"})
        fig.update_layout(title="Study Hours vs Performance", **PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)

    with col5:
        corr_cols = ['attendance_percentage', 'study_hours_per_day', 'assignment_completion_rate',
                     'participation_score', 'previous_gpa', 'internal_marks', 'final_score']
        avail = [c for c in corr_cols if c in df.columns]
        if len(avail) >= 2:
            corr = df[avail].corr()
            fig = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu_r',
                           aspect='auto')
            fig.update_layout(title="Feature Correlation Heatmap", **PLOTLY_LAYOUT, height=450)
            st.plotly_chart(fig, use_container_width=True)

    with col6:
        if 'gender' in df.columns:
            fig = px.violin(df, x='gender', y='final_score', color='gender',
                           box=True, color_discrete_sequence=[COLORS["primary"], COLORS["accent"]])
            fig.update_layout(title="Performance by Gender", **PLOTLY_LAYOUT, height=450,
                             showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # Summary stats table
    section_header("📊 Summary Statistics")
    numeric_cols = ['final_score', 'attendance_percentage', 'study_hours_per_day',
                    'assignment_completion_rate', 'participation_score', 'previous_gpa']
    avail = [c for c in numeric_cols if c in df.columns]
    if avail:
        summary = df[avail].describe().round(2)
        st.dataframe(summary, use_container_width=True)
