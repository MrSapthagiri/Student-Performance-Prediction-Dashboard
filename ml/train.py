"""
Model training for the Student Success ML pipeline.
Trains Logistic Regression, Decision Tree, Random Forest, and XGBoost.
Selects the best model based on validation metrics.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor

from ml.preprocessing import DataPreprocessor, prepare_targets, FEATURE_COLUMNS
from ml.evaluate import evaluate_classifier, evaluate_regressor


MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)


def train_risk_classifier(X_train, X_test, y_train, y_test):
    """Train and compare risk classifiers. Returns best model + all metrics."""
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
        "XGBoost": XGBClassifier(n_estimators=100, max_depth=8, learning_rate=0.1,
                                  random_state=42, use_label_encoder=False,
                                  eval_metric='mlogloss'),
    }

    results = {}
    best_model = None
    best_f1 = -1

    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)
        metrics = evaluate_classifier(model, X_test, y_test, name)
        results[name] = metrics

        if metrics['f1_weighted'] > best_f1:
            best_f1 = metrics['f1_weighted']
            best_model = (name, model)

    return best_model, results


def train_score_regressor(X_train, X_test, y_train, y_test):
    """Train and compare score regressors. Returns best model + metrics."""
    models = {
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
        "XGBoost Regressor": XGBRegressor(n_estimators=100, max_depth=8, learning_rate=0.1, random_state=42),
    }

    results = {}
    best_model = None
    best_r2 = -999

    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)
        metrics = evaluate_regressor(model, X_test, y_test, name)
        results[name] = metrics

        if metrics['r2'] > best_r2:
            best_r2 = metrics['r2']
            best_model = (name, model)

    return best_model, results


def train_pass_classifier(X_train, X_test, y_train, y_test):
    """Train pass/fail binary classifier."""
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
        "XGBoost": XGBClassifier(n_estimators=100, max_depth=8, learning_rate=0.1,
                                  random_state=42, use_label_encoder=False,
                                  eval_metric='logloss'),
    }

    results = {}
    best_model = None
    best_f1 = -1

    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)
        metrics = evaluate_classifier(model, X_test, y_test, name, binary=True)
        results[name] = metrics

        if metrics['f1_weighted'] > best_f1:
            best_f1 = metrics['f1_weighted']
            best_model = (name, model)

    return best_model, results


def run_training(df: pd.DataFrame = None):
    """Execute the full training pipeline."""
    print("=" * 60)
    print("  ML Training Pipeline")
    print("=" * 60)

    # Load data if not provided
    if df is None:
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'students.csv')
        if not os.path.exists(data_path):
            print("❌ students.csv not found. Run generate_dataset.py first.")
            return None
        df = pd.read_csv(data_path)

    print(f"\n📊 Dataset: {len(df)} samples, {len(df.columns)} columns")

    # Preprocessing
    print("\n🔧 Preprocessing...")
    preprocessor = DataPreprocessor()
    X, feature_names = preprocessor.fit_transform(df)
    targets = prepare_targets(df)

    # Train-test split
    X_train, X_test, idx_train, idx_test = train_test_split(
        X, np.arange(len(X)), test_size=0.2, random_state=42
    )

    all_results = {}

    # 1. Risk Classifier
    print("\n🎯 Training Risk Classifiers...")
    y_risk_train = targets['risk'][idx_train]
    y_risk_test = targets['risk'][idx_test]
    best_risk, risk_results = train_risk_classifier(X_train, X_test, y_risk_train, y_risk_test)
    all_results['risk_classification'] = risk_results
    print(f"  ✅ Best Risk Classifier: {best_risk[0]} (F1={risk_results[best_risk[0]]['f1_weighted']:.4f})")

    # 2. Score Regressor
    print("\n📈 Training Score Regressors...")
    y_score_train = targets['score'][idx_train]
    y_score_test = targets['score'][idx_test]
    best_score, score_results = train_score_regressor(X_train, X_test, y_score_train, y_score_test)
    all_results['score_prediction'] = score_results
    print(f"  ✅ Best Score Regressor: {best_score[0]} (R²={score_results[best_score[0]]['r2']:.4f})")

    # 3. Pass/Fail Classifier
    print("\n✅ Training Pass/Fail Classifiers...")
    y_pass_train = targets['pass_fail'][idx_train]
    y_pass_test = targets['pass_fail'][idx_test]
    best_pass, pass_results = train_pass_classifier(X_train, X_test, y_pass_train, y_pass_test)
    all_results['pass_fail_classification'] = pass_results
    print(f"  ✅ Best Pass/Fail Classifier: {best_pass[0]} (F1={pass_results[best_pass[0]]['f1_weighted']:.4f})")

    # Save models
    print("\n💾 Saving models...")
    joblib.dump(best_risk[1], os.path.join(MODELS_DIR, 'risk_classifier.pkl'))
    joblib.dump(best_score[1], os.path.join(MODELS_DIR, 'score_regressor.pkl'))
    joblib.dump(best_pass[1], os.path.join(MODELS_DIR, 'pass_classifier.pkl'))
    preprocessor.save(os.path.join(MODELS_DIR, 'preprocessor.pkl'))

    # Save metadata
    metadata = {
        "training_date": datetime.now().isoformat(),
        "dataset_size": len(df),
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "best_risk_model": best_risk[0],
        "best_score_model": best_score[0],
        "best_pass_model": best_pass[0],
        "model_version": "1.0",
        "results": {}
    }
    # Convert numpy types to Python types for JSON
    for task_name, task_results in all_results.items():
        metadata['results'][task_name] = {}
        for model_name, metrics in task_results.items():
            metadata['results'][task_name][model_name] = {
                k: float(v) if isinstance(v, (np.floating, float)) else v
                for k, v in metrics.items()
            }

    with open(os.path.join(MODELS_DIR, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2, default=str)

    print("  ✅ Models saved to models/")
    print(f"\n{'=' * 60}")
    print("  Training complete!")
    print(f"{'=' * 60}")

    return metadata
