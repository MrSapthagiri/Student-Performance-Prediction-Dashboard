"""
Prediction module — loads saved models and makes predictions on new data.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

from ml.preprocessing import DataPreprocessor

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
RISK_LABELS = ['Low', 'Medium', 'High']


class Predictor:
    """Load trained models and predict for new student data."""

    def __init__(self):
        self.preprocessor = None
        self.risk_model = None
        self.score_model = None
        self.pass_model = None
        self.metadata = None
        self._loaded = False

    def load_models(self):
        """Load all saved models and preprocessor."""
        try:
            self.preprocessor = DataPreprocessor.load(
                os.path.join(MODELS_DIR, 'preprocessor.pkl')
            )
            self.risk_model = joblib.load(
                os.path.join(MODELS_DIR, 'risk_classifier.pkl')
            )
            self.score_model = joblib.load(
                os.path.join(MODELS_DIR, 'score_regressor.pkl')
            )
            self.pass_model = joblib.load(
                os.path.join(MODELS_DIR, 'pass_classifier.pkl')
            )
            meta_path = os.path.join(MODELS_DIR, 'model_metadata.json')
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    self.metadata = json.load(f)
            self._loaded = True
            return True
        except FileNotFoundError as e:
            print(f"Model files not found: {e}")
            return False

    def predict_student(self, student_data: dict) -> dict:
        """Make predictions for a single student."""
        if not self._loaded:
            if not self.load_models():
                return {"error": "Models not trained. Please train models first."}

        df = pd.DataFrame([student_data])
        try:
            X = self.preprocessor.transform(df)
        except Exception as e:
            return {"error": f"Preprocessing failed: {e}"}

        result = {}

        # Risk prediction
        risk_pred = self.risk_model.predict(X)[0]
        result['risk_level'] = RISK_LABELS[int(risk_pred)]
        if hasattr(self.risk_model, 'predict_proba'):
            proba = self.risk_model.predict_proba(X)[0]
            result['risk_probabilities'] = {
                RISK_LABELS[i]: round(float(p), 4) for i, p in enumerate(proba)
            }

        # Score prediction
        score_pred = self.score_model.predict(X)[0]
        result['predicted_score'] = round(float(np.clip(score_pred, 0, 100)), 2)

        # Pass/Fail prediction
        pass_pred = self.pass_model.predict(X)[0]
        result['predicted_pass_fail'] = "Pass" if pass_pred == 1 else "Fail"
        if hasattr(self.pass_model, 'predict_proba'):
            pass_proba = self.pass_model.predict_proba(X)[0]
            result['pass_probability'] = round(float(pass_proba[1]), 4)

        return result

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Make predictions for a batch of students."""
        if not self._loaded:
            if not self.load_models():
                return df

        try:
            X = self.preprocessor.transform(df)
        except Exception as e:
            print(f"Batch preprocessing failed: {e}")
            return df

        df = df.copy()
        risk_preds = self.risk_model.predict(X)
        df['predicted_risk'] = [RISK_LABELS[int(r)] for r in risk_preds]

        score_preds = self.score_model.predict(X)
        df['predicted_score'] = np.clip(np.round(score_preds, 2), 0, 100)

        pass_preds = self.pass_model.predict(X)
        df['predicted_pass_fail'] = ['Pass' if p == 1 else 'Fail' for p in pass_preds]

        return df

    def get_metadata(self):
        if self.metadata is None:
            meta_path = os.path.join(MODELS_DIR, 'model_metadata.json')
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    self.metadata = json.load(f)
        return self.metadata

    @staticmethod
    def models_exist():
        required = ['risk_classifier.pkl', 'score_regressor.pkl',
                     'pass_classifier.pkl', 'preprocessor.pkl']
        return all(
            os.path.exists(os.path.join(MODELS_DIR, f)) for f in required
        )
