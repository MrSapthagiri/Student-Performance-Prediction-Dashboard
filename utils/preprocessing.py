import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple


DATASET_PATH = Path(__file__).resolve().parents[1] / "dataset" / "student_performance.csv"

TARGET_COLUMN = "Performance"


def validate_and_clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Validate, clean, and standardize the student performance dataset."""
    if df is None or df.empty:
        raise ValueError("The uploaded dataset is empty.")

    cleaned = df.copy()
    cleaned.columns = [col.strip() for col in cleaned.columns]

    required_columns = [
        "Student_ID",
        "Gender",
        "Age",
        "Class",
        "Attendance",
        "Study_Hours",
        "Assignments_Completed",
        "Quiz_Score",
        "Midterm_Marks",
        "Final_Exam_Marks",
        "Internet_Access",
        "Parental_Education",
        "Extra_Curricular",
        "Sleep_Hours",
        "Previous_Grade",
        "Performance",
    ]

    for column in required_columns:
        if column not in cleaned.columns:
            cleaned[column] = np.nan

    cleaned = cleaned.drop_duplicates(subset=["Student_ID"], keep="first")

    numeric_columns = [
        "Age",
        "Attendance",
        "Study_Hours",
        "Assignments_Completed",
        "Quiz_Score",
        "Midterm_Marks",
        "Final_Exam_Marks",
        "Sleep_Hours",
    ]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned["Age"] = cleaned["Age"].fillna(cleaned["Age"].median())
    cleaned["Attendance"] = cleaned["Attendance"].fillna(cleaned["Attendance"].median())
    cleaned["Study_Hours"] = cleaned["Study_Hours"].fillna(cleaned["Study_Hours"].median())
    cleaned["Assignments_Completed"] = cleaned["Assignments_Completed"].fillna(cleaned["Assignments_Completed"].median())
    cleaned["Quiz_Score"] = cleaned["Quiz_Score"].fillna(cleaned["Quiz_Score"].median())
    cleaned["Midterm_Marks"] = cleaned["Midterm_Marks"].fillna(cleaned["Midterm_Marks"].median())
    cleaned["Final_Exam_Marks"] = cleaned["Final_Exam_Marks"].fillna(cleaned["Final_Exam_Marks"].median())
    cleaned["Sleep_Hours"] = cleaned["Sleep_Hours"].fillna(cleaned["Sleep_Hours"].median())

    for column in ["Gender", "Internet_Access", "Parental_Education", "Extra_Curricular", "Previous_Grade", "Performance"]:
        cleaned[column] = cleaned[column].fillna("Unknown")

    cleaned["Class"] = cleaned["Class"].astype(str)
    cleaned["Performance"] = cleaned["Performance"].str.strip().str.title()
    cleaned["Performance"] = cleaned["Performance"].replace({"Excellent": "Excellent", "Good": "Good", "Average": "Average", "Poor": "Poor"})
    cleaned["Performance"] = cleaned["Performance"].fillna("Average")

    cleaned["Student_ID"] = cleaned["Student_ID"].astype(str)
    cleaned["Attendance"] = cleaned["Attendance"].clip(lower=0, upper=100)
    cleaned["Study_Hours"] = cleaned["Study_Hours"].clip(lower=0, upper=24)
    cleaned["Sleep_Hours"] = cleaned["Sleep_Hours"].clip(lower=0, upper=24)

    return cleaned.reset_index(drop=True)


def build_preprocessor(df: pd.DataFrame) -> Dict[str, Any]:
    """Create a feature metadata dictionary used by training and prediction."""
    feature_columns = [
        "Gender",
        "Age",
        "Class",
        "Attendance",
        "Study_Hours",
        "Assignments_Completed",
        "Quiz_Score",
        "Midterm_Marks",
        "Final_Exam_Marks",
        "Internet_Access",
        "Parental_Education",
        "Extra_Curricular",
        "Sleep_Hours",
        "Previous_Grade",
    ]

    return {
        "feature_columns": feature_columns,
        "target_column": TARGET_COLUMN,
        "categorical_columns": [
            "Gender",
            "Class",
            "Internet_Access",
            "Parental_Education",
            "Extra_Curricular",
            "Previous_Grade",
        ],
    }


def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    cleaned = validate_and_clean_dataset(df)
    preprocessor = build_preprocessor(cleaned)
    features = cleaned[preprocessor["feature_columns"]].copy()
    target = cleaned[TARGET_COLUMN]

    for column in preprocessor["categorical_columns"]:
        features[column] = features[column].astype(str)

    return features, target


def load_default_dataset() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        raise FileNotFoundError("The default dataset file was not found.")
    return pd.read_csv(DATASET_PATH)
