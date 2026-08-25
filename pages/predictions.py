"""
AI Prediction Page — Run predictions on individual students or batches.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.ui_helpers import (
    inject_css, section_header, require_auth, kpi_card,
    risk_badge, PLOTLY_LAYOUT, COLORS
)
from database.services.data_service import DataService
from ml.predict import Predictor


def render():
    inject_css()
    if not require_auth():
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        🤖 AI Prediction
    </h1>
    """, unsafe_allow_html=True)

    if not Predictor.models_exist():
        st.warning("⚠️ ML models not trained yet. Go to **Model Performance** page to train the models.")
        return

    tab1, tab2 = st.tabs(["👤 Individual Prediction", "📋 Batch Prediction"])

    # ── Individual ──
    with tab1:
        section_header("Predict for a Student")
        sid = st.number_input("Enter Student ID", min_value=1, value=1, key="pred_sid")

        if st.button("🔮 Generate Prediction", key="gen_pred", type="primary"):
            student = DataService.get_student(sid)
            if not student:
                st.error(f"Student {sid} not found.")
            else:
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
                    st.markdown(f"### {student.student_name}")
                    st.markdown(f"{student.department} • Year {student.year}")

                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        kpi_card("⚠️", pred.get("risk_level", "N/A"), "Predicted Risk")
                    with c2:
                        kpi_card("📊", f"{pred.get('predicted_score', 0):.1f}", "Predicted Score")
                    with c3:
                        kpi_card("✅", pred.get("predicted_pass_fail", "N/A"), "Pass/Fail")
                    with c4:
                        kpi_card("📈", f"{pred.get('pass_probability', 0)*100:.1f}%", "Pass Probability")

                    # Risk probabilities
                    if "risk_probabilities" in pred:
                        rp = pred["risk_probabilities"]
                        fig = go.Figure(data=[go.Bar(
                            x=list(rp.keys()), y=list(rp.values()),
                            marker=dict(color=[COLORS["success"], COLORS["warning"], COLORS["danger"]]),
                            text=[f"{v*100:.1f}%" for v in rp.values()],
                            textposition="outside",
                        )])
                        fig.update_layout(
                            title="Risk Level Probabilities",
                            yaxis_title="Probability",
                            **PLOTLY_LAYOUT, height=350,
                        )
                        st.plotly_chart(fig, use_container_width=True)

    # ── Batch ──
    with tab2:
        section_header("Batch Prediction — All Students")
        if st.button("🚀 Run Batch Prediction", key="batch_pred", type="primary"):
            with st.spinner("Running predictions on all students..."):
                try:
                    df = DataService.get_all_students_as_df()
                    if df is None or len(df) == 0:
                        st.warning("No student data available.")
                    else:
                        predictor = Predictor()
                        result_df = predictor.predict_batch(df)

                        st.success(f"✅ Predictions generated for {len(result_df)} students!")

                        # Summary
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            kpi_card("🟢", (result_df['predicted_risk'] == 'Low').sum(), "Low Risk")
                        with c2:
                            kpi_card("🟡", (result_df['predicted_risk'] == 'Medium').sum(), "Medium Risk")
                        with c3:
                            kpi_card("🔴", (result_df['predicted_risk'] == 'High').sum(), "High Risk")

                        # Show results
                        display_cols = ['student_id', 'student_name', 'department', 'year',
                                       'attendance_percentage', 'final_score',
                                       'predicted_risk', 'predicted_score', 'predicted_pass_fail']
                        display_cols = [c for c in display_cols if c in result_df.columns]
                        st.dataframe(result_df[display_cols].head(50), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Prediction failed: {e}")
