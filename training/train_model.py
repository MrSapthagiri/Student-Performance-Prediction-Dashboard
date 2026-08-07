import json
import os
import joblib
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT_DIR))

from utils.preprocessing import load_default_dataset, prepare_features

MODEL_DIR = ROOT_DIR / "model"
MODEL_DIR.mkdir(exist_ok=True)


def train_and_save_model(data: pd.DataFrame | None = None) -> dict:
    if data is None:
        data = load_default_dataset()

    X, y = prepare_features(data)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    categorical_features = [
        "Gender",
        "Class",
        "Internet_Access",
        "Parental_Education",
        "Extra_Curricular",
        "Previous_Grade",
    ]
    numeric_features = [
        "Age",
        "Attendance",
        "Study_Hours",
        "Assignments_Completed",
        "Quiz_Score",
        "Midterm_Marks",
        "Final_Exam_Marks",
        "Sleep_Hours",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("classifier", DecisionTreeClassifier(max_depth=5, random_state=42)),
        ]
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, average="weighted", zero_division=0)
    recall = recall_score(y_test, predictions, average="weighted", zero_division=0)
    f1 = f1_score(y_test, predictions, average="weighted", zero_division=0)
    try:
        roc_auc = roc_auc_score(y_test, model.predict_proba(X_test), multi_class="ovr")
    except Exception:
        roc_auc = 0.0

    joblib.dump(model, MODEL_DIR / "decision_tree_model.pkl")
    joblib.dump({"feature_columns": X.columns.tolist()}, MODEL_DIR / "scaler.pkl")
    joblib.dump({"classes": sorted(y.unique())}, MODEL_DIR / "label_encoder.pkl")

    metrics = {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "classification_report": classification_report(y_test, predictions, output_dict=True),
    }

    with open(MODEL_DIR / "metrics.json", "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)

    return metrics


if __name__ == "__main__":
    train_and_save_model()
    print("Model training completed successfully.")
