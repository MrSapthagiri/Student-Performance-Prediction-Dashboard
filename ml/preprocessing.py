"""
Data preprocessing for the Student Success ML pipeline.
Handles missing values, scaling, and encoding.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import joblib
import os


# Features used for prediction (NO target-leaking columns like final_score, grade, pass_fail)
FEATURE_COLUMNS = [
    'previous_gpa',
    'previous_percentage',
    'internal_marks',
    'assignment_score',
    'quiz_score',
    'midterm_score',
    'attendance_percentage',
    'study_hours_per_day',
    'assignment_completion_rate',
    'online_learning_hours',
    'library_usage',
    'participation_score',
]

# Categorical features to encode
CATEGORICAL_FEATURES = ['department', 'gender']

# Target columns
TARGET_SCORE = 'final_score'
TARGET_RISK = 'risk_level'
TARGET_PASS = 'pass_fail'


class DataPreprocessor:
    """Handles all data preprocessing for training and prediction."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.imputer = SimpleImputer(strategy='median')
        self.feature_columns = FEATURE_COLUMNS.copy()
        self.is_fitted = False

    def fit_transform(self, df: pd.DataFrame):
        """Fit the preprocessor on training data and transform it."""
        df = df.copy()

        # Encode categorical features
        encoded_cols = []
        for col in CATEGORICAL_FEATURES:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
                encoded_cols.append(f'{col}_encoded')

        all_features = self.feature_columns + encoded_cols
        self.all_feature_names = all_features

        X = df[all_features].values

        # Impute missing values
        X = self.imputer.fit_transform(X)

        # Scale
        X = self.scaler.fit_transform(X)
        self.is_fitted = True

        return X, all_features

    def transform(self, df: pd.DataFrame):
        """Transform new data using the fitted preprocessor."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor not fitted. Call fit_transform first.")

        df = df.copy()

        encoded_cols = []
        for col in CATEGORICAL_FEATURES:
            if col in df.columns and col in self.label_encoders:
                le = self.label_encoders[col]
                # Handle unseen labels
                df[f'{col}_encoded'] = df[col].astype(str).apply(
                    lambda x: le.transform([x])[0] if x in le.classes_ else -1
                )
                encoded_cols.append(f'{col}_encoded')

        all_features = self.feature_columns + encoded_cols
        X = df[all_features].values
        X = self.imputer.transform(X)
        X = self.scaler.transform(X)
        return X

    def save(self, path: str):
        """Save the preprocessor to disk."""
        joblib.dump(self, path)

    @staticmethod
    def load(path: str):
        """Load a preprocessor from disk."""
        return joblib.load(path)


def prepare_targets(df: pd.DataFrame):
    """Prepare target variables from the dataframe."""
    targets = {}

    # Score prediction target
    if TARGET_SCORE in df.columns:
        targets['score'] = df[TARGET_SCORE].values

    # Risk classification target
    if TARGET_RISK in df.columns:
        risk_map = {'Low': 0, 'Medium': 1, 'High': 2}
        targets['risk'] = df[TARGET_RISK].map(risk_map).values
        targets['risk_labels'] = ['Low', 'Medium', 'High']

    # Pass/Fail binary target
    if TARGET_PASS in df.columns:
        targets['pass_fail'] = (df[TARGET_PASS] == 'Pass').astype(int).values

    return targets
