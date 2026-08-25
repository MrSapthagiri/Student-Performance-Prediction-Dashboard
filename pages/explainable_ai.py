"""
Explainable AI Page — Global and per-student SHAP explanations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.ui_helpers import (
    inject_css, section_header, require_auth,
    kpi_card, PLOTLY_LAYOUT, COLORS
)
from database.services.data_service import DataService
from ml.predict import Predictor
from ml.explain import ModelExplainer


def render():
    inject_css()
    if not require_auth():
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        🧠 Explainable AI (SHAP)
    </h1>
    """, unsafe_allow_html=True)

    if not Predictor.models_exist():
        st.warning("⚠️ ML models not trained yet.")
        return

    tab1, tab2 = st.tabs(["🌍 Global Feature Importance", "👤 Individual Explanation"])

    # Global
    with tab1:
        section_header("Global Feature Importance")
        st.markdown("Shows which features are most important across all students for risk prediction.")

        if st.button("📊 Calculate Global Importance", key="global_imp", type="primary"):
            with st.spinner("Computing SHAP values across all students..."):
                try:
                    df = DataService.get_all_students_as_df()
                    if df is not None and len(df) > 0:
                        # Use a sample for speed
                        sample = df.sample(min(200, len(df)), random_state=42)
                        explainer = ModelExplainer()
                        result = explainer.get_global_importance(sample)

                        if "error" in result:
                            st.error(result["error"])
                        else:
                            importance = result["feature_importance"]
                            features = list(importance.keys())
                            values = list(importance.values())

                            fig = go.Figure(data=[go.Bar(
                                x=values, y=features, orientation='h',
                                marker=dict(
                                    color=values,
                                    colorscale='Viridis',
                                ),
                                text=[f"{v:.4f}" for v in values],
                                textposition="outside",
                            )])
                            fig.update_layout(
                                title="Mean |SHAP Value| (Feature Importance)",
                                xaxis_title="Mean |SHAP Value|",
                                **PLOTLY_LAYOUT, height=500,
                                yaxis=dict(autorange="reversed"),
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            # Table
                            imp_df = pd.DataFrame({
                                "Feature": features,
                                "Importance": values,
                            })
                            st.dataframe(imp_df, use_container_width=True, hide_index=True)
                    else:
                        st.warning("No student data available.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Individual
    with tab2:
        section_header("Individual Student Explanation")
        sid = st.number_input("Student ID", min_value=1, value=1, key="shap_sid")

        if st.button("🔮 Explain Prediction", key="explain_pred", type="primary"):
            student = DataService.get_student(sid)
            if not student:
                st.error(f"Student {sid} not found.")
            else:
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
                    st.error(explanation["error"])
                else:
                    st.markdown(f"### {student.student_name}")
                    st.markdown(f"**Predicted Risk:** {explanation['predicted_risk']}")

                    contribs = explanation.get("contributions", [])[:12]
                    if contribs:
                        features = [c['feature'] for c in contribs]
                        values = [c['shap_value'] for c in contribs]
                        colors = [COLORS["danger"] if v > 0 else COLORS["success"] for v in values]

                        # Bar chart
                        fig = go.Figure(data=[go.Bar(
                            x=values, y=features, orientation='h',
                            marker=dict(color=colors),
                            text=[f"{v:+.4f}" for v in values],
                            textposition="outside",
                        )])
                        fig.update_layout(
                            title="Why did the AI make this prediction?",
                            xaxis_title="SHAP Value (impact on risk)",
                            **PLOTLY_LAYOUT, height=450,
                            yaxis=dict(autorange="reversed"),
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Waterfall chart
                        section_header("Waterfall Chart")
                        fig2 = go.Figure(go.Waterfall(
                            name="SHAP",
                            orientation="h",
                            measure=["relative"] * len(contribs) + ["total"],
                            y=[c['feature'] for c in contribs] + ["Prediction"],
                            x=[c['shap_value'] for c in contribs] + [sum(c['shap_value'] for c in contribs)],
                            connector=dict(line=dict(color="rgba(99,102,241,0.3)")),
                            increasing=dict(marker=dict(color=COLORS["danger"])),
                            decreasing=dict(marker=dict(color=COLORS["success"])),
                            totals=dict(marker=dict(color=COLORS["primary"])),
                        ))
                        fig2.update_layout(
                            title="Feature Contribution Waterfall",
                            **PLOTLY_LAYOUT, height=450,
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                        # Table
                        section_header("Contribution Details")
                        cdf = pd.DataFrame(contribs)[['feature', 'shap_value', 'direction', 'input_value']]
                        cdf.columns = ['Feature', 'SHAP Value', 'Direction', 'Scaled Input']
                        st.dataframe(cdf, use_container_width=True, hide_index=True)
