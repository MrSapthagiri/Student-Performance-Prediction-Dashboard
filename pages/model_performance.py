"""
Model Performance Page — View metrics and trigger retraining.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from utils.ui_helpers import (
    inject_css, section_header, require_auth, require_role,
    kpi_card, show_success, show_error, PLOTLY_LAYOUT, COLORS
)
from ml.predict import Predictor
from ml.train import run_training


MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')


def render():
    inject_css()
    if not require_role("Admin", "Faculty"):
        return

    st.markdown("""
    <h1 style="font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        🧪 Model Performance
    </h1>
    """, unsafe_allow_html=True)

    # Training controls
    if st.session_state.get("user_role") == "Admin":
        if st.button("🚀 Train / Retrain Models", type="primary", key="train_btn"):
            with st.spinner("Training models... This may take a moment."):
                try:
                    metadata = run_training()
                    if metadata:
                        show_success("Models trained successfully!")
                        st.rerun()
                    else:
                        show_error("Training failed. Check data files.")
                except Exception as e:
                    show_error(f"Training error: {e}")

    # Load metadata
    meta_path = os.path.join(MODELS_DIR, 'model_metadata.json')
    if not os.path.exists(meta_path):
        st.warning("⚠️ No trained models found. Click 'Train / Retrain Models' to begin.")
        return

    with open(meta_path) as f:
        metadata = json.load(f)

    # Model info
    section_header("📋 Model Information")
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("🎯", metadata.get("best_risk_model", "N/A"), "Best Risk Model")
    with c2: kpi_card("📈", metadata.get("best_score_model", "N/A"), "Best Score Model")
    with c3: kpi_card("✅", metadata.get("best_pass_model", "N/A"), "Best Pass Model")
    with c4: kpi_card("🔢", metadata.get("feature_count", 0), "Features Used")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c5, c6, c7 = st.columns(3)
    with c5: kpi_card("📊", metadata.get("dataset_size", 0), "Dataset Size")
    with c6: kpi_card("📅", metadata.get("training_date", "N/A")[:10], "Training Date")
    with c7: kpi_card("🏷️", metadata.get("model_version", "1.0"), "Model Version")

    results = metadata.get("results", {})

    # ── Risk Classification ──
    if "risk_classification" in results:
        section_header("🎯 Risk Classification Models")
        risk_data = results["risk_classification"]
        rows = []
        for model_name, metrics in risk_data.items():
            rows.append({
                "Model": model_name,
                "Accuracy": f"{metrics.get('accuracy', 0):.4f}",
                "Precision": f"{metrics.get('precision_weighted', 0):.4f}",
                "Recall": f"{metrics.get('recall_weighted', 0):.4f}",
                "F1 Score": f"{metrics.get('f1_weighted', 0):.4f}",
                "ROC-AUC": f"{metrics.get('roc_auc', 0):.4f}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Comparison chart
        fig = go.Figure()
        metric_names = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted', 'roc_auc']
        display_names = ['Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC']
        for i, (model_name, metrics) in enumerate(risk_data.items()):
            fig.add_trace(go.Bar(
                name=model_name,
                x=display_names,
                y=[metrics.get(m, 0) for m in metric_names],
                marker_color=COLORS["palette"][i % len(COLORS["palette"])],
            ))
        fig.update_layout(
            title="Risk Classification: Model Comparison",
            barmode='group', yaxis_title="Score",
            **PLOTLY_LAYOUT, height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Score Prediction ──
    if "score_prediction" in results:
        section_header("📈 Score Prediction Models")
        score_data = results["score_prediction"]
        rows = []
        for model_name, metrics in score_data.items():
            rows.append({
                "Model": model_name,
                "MAE": f"{metrics.get('mae', 0):.4f}",
                "RMSE": f"{metrics.get('rmse', 0):.4f}",
                "R²": f"{metrics.get('r2', 0):.4f}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Pass/Fail Classification ──
    if "pass_fail_classification" in results:
        section_header("✅ Pass/Fail Classification Models")
        pass_data = results["pass_fail_classification"]
        rows = []
        for model_name, metrics in pass_data.items():
            rows.append({
                "Model": model_name,
                "Accuracy": f"{metrics.get('accuracy', 0):.4f}",
                "Precision": f"{metrics.get('precision_weighted', 0):.4f}",
                "Recall": f"{metrics.get('recall_weighted', 0):.4f}",
                "F1 Score": f"{metrics.get('f1_weighted', 0):.4f}",
                "ROC-AUC": f"{metrics.get('roc_auc', 0):.4f}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Feature list
    section_header("📝 Features Used")
    features = metadata.get("feature_names", [])
    if features:
        cols = st.columns(3)
        for i, f in enumerate(features):
            cols[i % 3].markdown(f"• `{f}`")
