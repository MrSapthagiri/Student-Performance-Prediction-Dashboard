"""
SHAP-based Explainable AI for the Student Success ML pipeline.
Generates per-student explanations for model predictions.
"""

import os
import joblib
import numpy as np
import pandas as pd
import shap

from ml.preprocessing import DataPreprocessor

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')


class ModelExplainer:
    """Generates SHAP explanations for model predictions."""

    def __init__(self):
        self.preprocessor = None
        self.risk_model = None
        self.explainer = None
        self.feature_names = None
        self._loaded = False

    def load(self):
        """Load model and create SHAP explainer."""
        try:
            self.preprocessor = DataPreprocessor.load(
                os.path.join(MODELS_DIR, 'preprocessor.pkl')
            )
            self.risk_model = joblib.load(
                os.path.join(MODELS_DIR, 'risk_classifier.pkl')
            )
            self.feature_names = self.preprocessor.all_feature_names
            # Use TreeExplainer for tree-based models, KernelExplainer as fallback
            try:
                self.explainer = shap.TreeExplainer(self.risk_model)
            except Exception:
                # Fallback to KernelExplainer with a background sample
                self.explainer = None
            self._loaded = True
            return True
        except Exception as e:
            print(f"Failed to load explainer: {e}")
            return False

    def explain_student(self, student_data: dict) -> dict:
        """Generate SHAP explanation for a single student."""
        if not self._loaded:
            if not self.load():
                return {"error": "Could not load explainer models."}

        df = pd.DataFrame([student_data])
        try:
            X = self.preprocessor.transform(df)
        except Exception as e:
            return {"error": f"Preprocessing failed: {e}"}

        if self.explainer is None:
            return {"error": "SHAP explainer not available for this model type."}

        try:
            shap_values = self.explainer.shap_values(X)
        except Exception as e:
            return {"error": f"SHAP computation failed: {e}"}

        # Determine predicted class
        prediction = self.risk_model.predict(X)[0]
        risk_labels = ['Low', 'Medium', 'High']
        predicted_label = risk_labels[int(prediction)]

        # Get SHAP values for the predicted class
        if isinstance(shap_values, list):
            # Multi-class: shap_values is a list of arrays (one per class)
            sv = shap_values[int(prediction)][0]
        else:
            # Binary or single output
            if shap_values.ndim == 3:
                sv = shap_values[0, :, int(prediction)]
            else:
                sv = shap_values[0]

        # Build feature contribution table
        contributions = []
        for i, fname in enumerate(self.feature_names):
            contributions.append({
                "feature": fname,
                "shap_value": round(float(sv[i]), 4),
                "abs_value": abs(float(sv[i])),
                "direction": "positive" if sv[i] > 0 else "negative",
                "input_value": round(float(X[0][i]), 4),
            })

        # Sort by absolute contribution
        contributions.sort(key=lambda x: x['abs_value'], reverse=True)

        # Feature importance (global)
        try:
            base_value = float(self.explainer.expected_value[int(prediction)]) \
                if isinstance(self.explainer.expected_value, (list, np.ndarray)) \
                else float(self.explainer.expected_value)
        except Exception:
            base_value = 0.0

        return {
            "predicted_risk": predicted_label,
            "base_value": base_value,
            "contributions": contributions,
            "shap_values": sv.tolist(),
            "feature_names": self.feature_names,
            "input_values": X[0].tolist(),
        }

    def get_global_importance(self, df: pd.DataFrame) -> dict:
        """Get global feature importance from SHAP values across all students."""
        if not self._loaded:
            if not self.load():
                return {"error": "Could not load explainer models."}

        try:
            X = self.preprocessor.transform(df)
        except Exception as e:
            return {"error": f"Preprocessing failed: {e}"}

        if self.explainer is None:
            return {"error": "SHAP explainer not available."}

        try:
            shap_values = self.explainer.shap_values(X)
        except Exception as e:
            return {"error": f"SHAP computation failed: {e}"}

        # Average absolute SHAP values across all classes and samples
        if isinstance(shap_values, list):
            all_sv = np.array(shap_values)
            mean_abs = np.mean(np.abs(all_sv), axis=(0, 1))
        else:
            mean_abs = np.mean(np.abs(shap_values), axis=0)
            if mean_abs.ndim > 1:
                mean_abs = np.mean(mean_abs, axis=-1)

        importance = {
            self.feature_names[i]: round(float(mean_abs[i]), 4)
            for i in range(len(self.feature_names))
        }

        # Sort by importance
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

        return {"feature_importance": importance}
