"""
Student Profile Page — Detailed view with tabs.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.ui_helpers import (
    inject_css, section_header, require_auth, risk_badge,
    kpi_card, PLOTLY_LAYOUT, COLORS
)
from database.services.data_service import DataService
from ml.predict import Predictor
from ml.explain import ModelExplainer
from ml.feature_engineering import get_risk_factors, generate_recommendations


def render():
    inject_css()
    if not require_auth():
        return

    sid = st.session_state.get("selected_student_id")
    if not sid:
        st.warning("No student selected.")
        return

    student = DataService.get_student(sid)
    if not student:
        st.error(f"Student with ID {sid} not found.")
        return

    # Back button
    if st.button("← Back to Students", key="back_to_students"):
        st.session_state.selected_student_id = None
        st.session_state.current_page = "Students"
        st.rerun()

    # Header
    risk = student.risk_level or "Medium"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin:12px 0 20px 0;">
        <div style="font-size:42px;">👤</div>
        <div>
            <div style="font-size:24px;font-weight:800;color:#e2e8f0;">
                {student.student_name}
            </div>
            <div style="font-size:14px;color:#94a3b8;">
                {student.register_number} • {student.department} • Year {student.year}, Sem {student.semester}
            </div>
        </div>
        <div style="margin-left:auto;">{risk_badge(risk)}</div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Tabs ─────────────────────────────────────────────────────
    tabs = st.tabs(["📋 Overview", "📊 Academic", "📚 Modules", "📅 Attendance",
                     "🤖 AI Prediction", "🧠 Explainability", "💡 Recommendations", "🚨 Interventions"])

    # ── Overview Tab ──
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            section_header("Personal Information")
            info_data = {
                "Student ID": student.student_id,
                "Register Number": student.register_number,
                "Email": student.email,
                "Phone": student.phone,
                "Gender": student.gender,
                "Section": student.section,
                "Academic Year": student.academic_year,
                "Course": student.course,
            }
            for k, v in info_data.items():
                st.markdown(f"**{k}:** {v}")

        with c2:
            section_header("Academic Summary")
            k1, k2 = st.columns(2)
            with k1:
                kpi_card("📊", f"{student.final_score or 0:.1f}", "Final Score")
            with k2:
                kpi_card("🏆", student.grade or "NA", "Grade")
            k3, k4 = st.columns(2)
            with k3:
                kpi_card("📅", f"{student.attendance_percentage or 0:.1f}%", "Attendance")
            with k4:
                kpi_card("📈", f"{student.previous_gpa or 0:.1f}", "Previous GPA")

    # ── Academic Tab ──
    with tabs[1]:
        section_header("Academic Performance")
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            kpi_card("📝", f"{student.internal_marks or 0:.1f}/40", "Internal")
        with mc2:
            kpi_card("✍️", f"{student.assignment_score or 0:.1f}/25", "Assignment")
        with mc3:
            kpi_card("❓", f"{student.quiz_score or 0:.1f}/20", "Quiz")
        with mc4:
            kpi_card("📋", f"{student.midterm_score or 0:.1f}/50", "Midterm")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        mc5, mc6 = st.columns(2)
        with mc5:
            kpi_card("📄", f"{student.final_exam_score or 0:.1f}/75", "Final Exam")
        with mc6:
            kpi_card("✅", student.pass_fail or "NA", "Result")

        # Performance radar chart
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        categories = ['Internal', 'Assignment', 'Quiz', 'Midterm', 'Final Exam', 'Attendance']
        values = [
            (student.internal_marks or 0) / 40 * 100,
            (student.assignment_score or 0) / 25 * 100,
            (student.quiz_score or 0) / 20 * 100,
            (student.midterm_score or 0) / 50 * 100,
            (student.final_exam_score or 0) / 75 * 100,
            student.attendance_percentage or 0,
        ]
        fig = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(129,140,248,0.2)',
            line=dict(color=COLORS["primary"], width=2),
        ))
        fig.update_layout(
            title="Performance Radar",
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0, 100], color='#64748b'),
                angularaxis=dict(color='#94a3b8'),
            ),
            **PLOTLY_LAYOUT, height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Modules Tab ──
    with tabs[2]:
        section_header("Module Performance")
        try:
            records = DataService.get_records_for_student(sid)
            if records:
                mod_data = []
                for r in records:
                    mod = DataService.get_module(r.module_id)
                    mod_name = mod.module_name if mod else f"Module {r.module_id}"
                    mod_data.append({
                        "Module": mod_name,
                        "Internal": r.internal_marks,
                        "Assignment": r.assignment_marks,
                        "Quiz": r.quiz_marks,
                        "Midterm": r.midterm_marks,
                        "Final Exam": r.final_exam_marks,
                        "Total": r.total_marks,
                        "Grade": r.grade,
                        "Result": r.result,
                        "Attendance": f"{r.attendance_percentage:.1f}%",
                    })
                df_mods = pd.DataFrame(mod_data)
                st.dataframe(df_mods, use_container_width=True, hide_index=True)

                # Module performance bar chart
                fig = go.Figure(data=[go.Bar(
                    x=[m["Module"] for m in mod_data],
                    y=[m["Total"] for m in mod_data],
                    marker=dict(color=COLORS["palette"][:len(mod_data)]),
                    text=[f"{m['Total']:.1f}" for m in mod_data],
                    textposition="outside",
                )])
                fig.update_layout(
                    title="Module-wise Performance",
                    xaxis_title="Module", yaxis_title="Total Marks",
                    **PLOTLY_LAYOUT, height=380, xaxis_tickangle=-30,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No module records found.")
        except Exception as e:
            st.error(f"Error loading modules: {e}")

    # ── Attendance Tab ──
    with tabs[3]:
        section_header("Attendance Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("📅", student.classes_held or 0, "Classes Held")
        with c2:
            kpi_card("✅", student.classes_attended or 0, "Classes Attended")
        with c3:
            kpi_card("📊", f"{student.attendance_percentage or 0:.1f}%", "Attendance %")

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=student.attendance_percentage or 0,
            title=dict(text="Attendance Rate", font=dict(size=18, color="#e2e8f0")),
            delta=dict(reference=75, increasing=dict(color=COLORS["success"]),
                       decreasing=dict(color=COLORS["danger"])),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor="#64748b"),
                bar=dict(color=COLORS["primary"]),
                bgcolor="rgba(0,0,0,0)",
                steps=[
                    dict(range=[0, 60], color="rgba(239,68,68,0.2)"),
                    dict(range=[60, 75], color="rgba(249,115,22,0.2)"),
                    dict(range=[75, 100], color="rgba(16,185,129,0.2)"),
                ],
                threshold=dict(line=dict(color=COLORS["warning"], width=3), thickness=0.8, value=75),
            ),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=350)
        st.plotly_chart(fig, use_container_width=True)

    # ── AI Prediction Tab ──
    with tabs[4]:
        section_header("AI-Powered Prediction")
        if Predictor.models_exist():
            predictor = Predictor()
            student_dict = {
                "previous_gpa": student.previous_gpa,
                "previous_percentage": student.previous_percentage,
                "internal_marks": student.internal_marks,
                "assignment_score": student.assignment_score,
                "quiz_score": student.quiz_score,
                "midterm_score": student.midterm_score,
                "attendance_percentage": student.attendance_percentage,
                "study_hours_per_day": student.study_hours_per_day,
                "assignment_completion_rate": student.assignment_completion_rate,
                "online_learning_hours": student.online_learning_hours,
                "library_usage": student.library_usage,
                "participation_score": student.participation_score,
                "department": student.department,
                "gender": student.gender,
            }
            pred = predictor.predict_student(student_dict)
            if "error" in pred:
                st.error(pred["error"])
            else:
                pc1, pc2, pc3 = st.columns(3)
                with pc1:
                    kpi_card("⚠️", pred.get("risk_level", "N/A"), "Predicted Risk")
                with pc2:
                    kpi_card("📊", f"{pred.get('predicted_score', 0):.1f}", "Predicted Score")
                with pc3:
                    kpi_card("✅", pred.get("predicted_pass_fail", "N/A"), "Predicted Result")

                # Risk probabilities
                if "risk_probabilities" in pred:
                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                    rp = pred["risk_probabilities"]
                    fig = go.Figure(data=[go.Bar(
                        x=list(rp.keys()), y=list(rp.values()),
                        marker=dict(color=[COLORS["success"], COLORS["warning"], COLORS["danger"]]),
                        text=[f"{v*100:.1f}%" for v in rp.values()],
                        textposition="outside",
                    )])
                    fig.update_layout(
                        title="Risk Probabilities",
                        yaxis_title="Probability",
                        **PLOTLY_LAYOUT, height=350,
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ ML models not trained yet. Go to Model Performance page to train.")

    # ── Explainability Tab ──
    with tabs[5]:
        section_header("🧠 SHAP Explanation")
        if Predictor.models_exist():
            explainer = ModelExplainer()
            student_dict = {
                "previous_gpa": student.previous_gpa,
                "previous_percentage": student.previous_percentage,
                "internal_marks": student.internal_marks,
                "assignment_score": student.assignment_score,
                "quiz_score": student.quiz_score,
                "midterm_score": student.midterm_score,
                "attendance_percentage": student.attendance_percentage,
                "study_hours_per_day": student.study_hours_per_day,
                "assignment_completion_rate": student.assignment_completion_rate,
                "online_learning_hours": student.online_learning_hours,
                "library_usage": student.library_usage,
                "participation_score": student.participation_score,
                "department": student.department,
                "gender": student.gender,
            }
            explanation = explainer.explain_student(student_dict)
            if "error" in explanation:
                st.warning(explanation["error"])
            else:
                st.markdown(f"**Predicted Risk Level:** {explanation['predicted_risk']}")

                # SHAP bar chart (top features)
                contribs = explanation.get("contributions", [])[:10]
                if contribs:
                    features = [c['feature'] for c in contribs]
                    values = [c['shap_value'] for c in contribs]
                    colors = [COLORS["danger"] if v > 0 else COLORS["success"] for v in values]

                    fig = go.Figure(data=[go.Bar(
                        x=values, y=features, orientation='h',
                        marker=dict(color=colors),
                        text=[f"{v:+.4f}" for v in values],
                        textposition="outside",
                    )])
                    fig.update_layout(
                        title="Feature Contributions (SHAP Values)",
                        xaxis_title="SHAP Value (impact on prediction)",
                        **PLOTLY_LAYOUT, height=400,
                        yaxis=dict(autorange="reversed"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Contribution table
                    section_header("Feature Contribution Details")
                    contrib_df = pd.DataFrame(contribs)[['feature', 'shap_value', 'direction']]
                    contrib_df.columns = ['Feature', 'SHAP Value', 'Direction']
                    st.dataframe(contrib_df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ ML models not trained yet.")

    # ── Recommendations Tab ──
    with tabs[6]:
        section_header("💡 Personalized Recommendations")
        student_dict = {
            "attendance_percentage": student.attendance_percentage,
            "study_hours_per_day": student.study_hours_per_day,
            "assignment_completion_rate": student.assignment_completion_rate,
            "previous_gpa": student.previous_gpa,
            "participation_score": student.participation_score,
            "internal_marks": student.internal_marks,
            "midterm_score": student.midterm_score,
        }
        risk_factors = get_risk_factors(student_dict)
        recommendations = generate_recommendations(student_dict, risk_factors)

        if risk_factors:
            section_header("⚠️ Risk Factors Identified")
            for factor, value, severity in risk_factors:
                color = COLORS["danger"] if severity == "critical" else COLORS["warning"]
                st.markdown(f"""
                <div style="background:rgba({','.join(str(int(color[i:i+2],16)) for i in (1,3,5))},0.1);
                     border-left:3px solid {color};padding:10px 14px;border-radius:8px;margin:6px 0;">
                    <strong>{factor}</strong>: {value}
                </div>
                """, unsafe_allow_html=True)

        for rec in recommendations:
            priority_colors = {"High": COLORS["danger"], "Medium": COLORS["warning"], "Low": COLORS["success"]}
            color = priority_colors.get(rec["priority"], COLORS["info"])
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(30,30,63,0.8),rgba(45,45,94,0.8));
                 border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:16px;margin:8px 0;">
                <div style="font-size:16px;margin-bottom:6px;">
                    {rec['icon']} <strong>{rec['area']}</strong>
                    <span style="float:right;font-size:11px;color:{color};font-weight:600;
                          text-transform:uppercase;">{rec['priority']} Priority</span>
                </div>
                <div style="color:#94a3b8;font-size:13px;">{rec['recommendation']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Interventions Tab ──
    with tabs[7]:
        section_header("🚨 Intervention History")
        try:
            interventions = DataService.get_student_interventions(sid)
            if interventions:
                for intv in interventions:
                    status_colors = {
                        "Pending": "#f59e0b", "Contacted": "#3b82f6",
                        "Intervention Started": "#a78bfa", "Monitoring": "#06b6d4",
                        "Resolved": "#10b981",
                    }
                    s_color = status_colors.get(intv.status, "#94a3b8")
                    st.markdown(f"""
                    <div class="profile-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <strong>Intervention #{intv.id}</strong>
                            <span style="color:{s_color};font-weight:600;">{intv.status}</span>
                        </div>
                        <div style="color:#94a3b8;font-size:13px;margin-top:6px;">
                            Risk: {intv.risk_level} | Predicted Score: {intv.predicted_score or 'N/A'}<br/>
                            Factor: {intv.main_risk_factor or 'N/A'}<br/>
                            Recommendation: {intv.recommendation or 'N/A'}<br/>
                            Notes: {intv.notes or 'N/A'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No interventions recorded for this student.")
        except Exception as e:
            st.error(f"Error loading interventions: {e}")
