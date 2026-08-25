"""
Dashboard Page — KPI cards and interactive Plotly charts.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.ui_helpers import (
    inject_css, kpi_card, section_header, require_auth,
    PLOTLY_LAYOUT, COLORS
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
        🏠 Dashboard
    </h1>
    """, unsafe_allow_html=True)

    # ─── KPI Cards ───────────────────────────────────────────────
    try:
        stats = DataService.get_student_stats()
        module_count = DataService.get_module_count()
    except Exception as e:
        st.warning(f"⚠️ Database not available: {e}. Showing empty dashboard.")
        stats = {"total": 0, "avg_attendance": 0, "avg_performance": 0,
                 "pass_rate": 0, "high_risk": 0, "medium_risk": 0, "low_risk": 0}
        module_count = 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("👨‍🎓", stats["total"], "Total Students")
    with c2:
        kpi_card("📚", module_count, "Total Modules")
    with c3:
        kpi_card("📊", f"{stats['avg_performance']}%", "Avg Performance")
    with c4:
        kpi_card("📅", f"{stats['avg_attendance']}%", "Avg Attendance")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        kpi_card("🔴", stats["high_risk"], "High Risk")
    with c6:
        kpi_card("🟡", stats["medium_risk"], "Medium Risk")
    with c7:
        kpi_card("🟢", stats["low_risk"], "Low Risk")
    with c8:
        kpi_card("✅", f"{stats['pass_rate']}%", "Pass Rate")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ─── Charts Row 1 ────────────────────────────────────────────
    section_header("📊 Academic Overview")

    col1, col2 = st.columns(2)

    # Risk Distribution
    with col1:
        try:
            risk_data = DataService.get_risk_distribution()
            if risk_data:
                fig = go.Figure(data=[go.Pie(
                    labels=list(risk_data.keys()),
                    values=list(risk_data.values()),
                    hole=0.55,
                    marker=dict(colors=[COLORS["success"], COLORS["warning"], COLORS["danger"]]),
                    textinfo="label+percent",
                    textfont=dict(size=13, color="#e2e8f0"),
                )])
                fig.update_layout(
                    title=dict(text="Risk Distribution", font=dict(size=16)),
                    **PLOTLY_LAYOUT, height=380,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No risk data available.")
        except Exception:
            st.info("No risk data available.")

    # Grade Distribution
    with col2:
        try:
            grade_data = DataService.get_grade_distribution()
            if grade_data:
                grade_order = ["O", "A+", "A", "B+", "B", "C", "F"]
                sorted_grades = {k: grade_data.get(k, 0) for k in grade_order if k in grade_data}
                fig = go.Figure(data=[go.Bar(
                    x=list(sorted_grades.keys()),
                    y=list(sorted_grades.values()),
                    marker=dict(
                        color=COLORS["palette"][:len(sorted_grades)],
                        line=dict(width=0),
                    ),
                    text=list(sorted_grades.values()),
                    textposition="outside",
                    textfont=dict(size=12, color="#e2e8f0"),
                )])
                fig.update_layout(
                    title=dict(text="Grade Distribution", font=dict(size=16)),
                    xaxis_title="Grade", yaxis_title="Students",
                    **PLOTLY_LAYOUT, height=380,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No grade data available.")
        except Exception:
            st.info("No grade data available.")

    # ─── Charts Row 2 ────────────────────────────────────────────
    col3, col4 = st.columns(2)

    # Department Performance
    with col3:
        try:
            dept_stats = DataService.get_department_stats()
            if dept_stats:
                df_dept = pd.DataFrame(dept_stats)
                fig = go.Figure(data=[go.Bar(
                    x=df_dept['avg_score'],
                    y=df_dept['department'],
                    orientation='h',
                    marker=dict(
                        color=df_dept['avg_score'],
                        colorscale='Viridis',
                        line=dict(width=0),
                    ),
                    text=df_dept['avg_score'].round(1),
                    textposition="outside",
                    textfont=dict(size=11, color="#e2e8f0"),
                )])
                fig.update_layout(
                    title=dict(text="Department Avg Performance", font=dict(size=16)),
                    xaxis_title="Avg Score",
                    **PLOTLY_LAYOUT, height=400,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No department data available.")
        except Exception:
            st.info("No department data available.")

    # Attendance vs Performance scatter
    with col4:
        try:
            students_df = DataService.get_all_students_as_df()
            if students_df is not None and len(students_df) > 0:
                fig = px.scatter(
                    students_df,
                    x="attendance_percentage",
                    y="final_score",
                    color="risk_level",
                    color_discrete_map={"Low": COLORS["success"], "Medium": COLORS["warning"], "High": COLORS["danger"]},
                    opacity=0.6,
                    hover_data=["student_name", "department"],
                    labels={"attendance_percentage": "Attendance %", "final_score": "Final Score"},
                )
                fig.update_layout(
                    title=dict(text="Attendance vs Performance", font=dict(size=16)),
                    **PLOTLY_LAYOUT, height=400,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No student data available.")
        except Exception:
            st.info("No student data available.")

    # ─── Charts Row 3 ────────────────────────────────────────────
    col5, col6 = st.columns(2)

    with col5:
        try:
            if students_df is not None and len(students_df) > 0:
                fig = px.scatter(
                    students_df,
                    x="study_hours_per_day",
                    y="final_score",
                    color="risk_level",
                    color_discrete_map={"Low": COLORS["success"], "Medium": COLORS["warning"], "High": COLORS["danger"]},
                    opacity=0.6,
                    trendline="ols",
                    labels={"study_hours_per_day": "Study Hours/Day", "final_score": "Final Score"},
                )
                fig.update_layout(
                    title=dict(text="Study Hours vs Performance", font=dict(size=16)),
                    **PLOTLY_LAYOUT, height=400,
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("No study hours data available.")

    with col6:
        try:
            if dept_stats:
                df_dept2 = pd.DataFrame(dept_stats)
                fig = go.Figure(data=[go.Bar(
                    x=df_dept2['department'],
                    y=df_dept2['avg_attendance'],
                    marker=dict(
                        color=df_dept2['avg_attendance'],
                        colorscale='Tealgrn',
                    ),
                    text=df_dept2['avg_attendance'].round(1),
                    textposition="outside",
                    textfont=dict(size=11, color="#e2e8f0"),
                )])
                fig.update_layout(
                    title=dict(text="Department Avg Attendance", font=dict(size=16)),
                    xaxis_title="Department", yaxis_title="Attendance %",
                    **PLOTLY_LAYOUT, height=400,
                    xaxis_tickangle=-30,
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("No attendance data available.")

    # ─── Charts Row 4 ────────────────────────────────────────────
    col7, col8 = st.columns(2)

    with col7:
        try:
            if students_df is not None and len(students_df) > 0 and 'semester' in students_df.columns:
                sem_perf = students_df.groupby('semester')['final_score'].mean().reset_index()
                fig = go.Figure(data=[go.Scatter(
                    x=sem_perf['semester'],
                    y=sem_perf['final_score'],
                    mode='lines+markers',
                    line=dict(color=COLORS["primary"], width=3),
                    marker=dict(size=10, color=COLORS["accent"]),
                    fill='tozeroy',
                    fillcolor='rgba(129,140,248,0.1)',
                )])
                fig.update_layout(
                    title=dict(text="Semester-wise Performance Trend", font=dict(size=16)),
                    xaxis_title="Semester", yaxis_title="Avg Score",
                    **PLOTLY_LAYOUT, height=380,
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("No semester data available.")

    with col8:
        try:
            if students_df is not None and len(students_df) > 0 and 'year' in students_df.columns:
                year_risk = students_df.groupby(['year', 'risk_level']).size().reset_index(name='count')
                fig = px.bar(
                    year_risk,
                    x='year', y='count', color='risk_level',
                    color_discrete_map={"Low": COLORS["success"], "Medium": COLORS["warning"], "High": COLORS["danger"]},
                    barmode='group',
                    labels={"year": "Year", "count": "Students", "risk_level": "Risk"},
                )
                fig.update_layout(
                    title=dict(text="Risk Distribution by Year", font=dict(size=16)),
                    **PLOTLY_LAYOUT, height=380,
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("No year-risk data available.")
