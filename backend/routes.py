import json
from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import StudentRecord, PredictionHistory
from utils.preprocessing import validate_and_clean_dataset

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "model" / "decision_tree_model.pkl"
METRICS_PATH = ROOT_DIR / "model" / "metrics.json"
DATASET_PATH = ROOT_DIR / "dataset" / "student_performance.csv"

bp = Blueprint("main", __name__)


def _load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model file is missing. Train the model first.")
    return joblib.load(MODEL_PATH)


def _build_payload(payload: dict) -> pd.DataFrame:
    record = {
        "Gender": payload.get("Gender", "Unknown"),
        "Age": payload.get("Age", 0),
        "Class": payload.get("Class", "Unknown"),
        "Attendance": payload.get("Attendance", 0),
        "Study_Hours": payload.get("Study_Hours", 0),
        "Assignments_Completed": payload.get("Assignments_Completed", 0),
        "Quiz_Score": payload.get("Quiz_Score", 0),
        "Midterm_Marks": payload.get("Midterm_Marks", 0),
        "Final_Exam_Marks": payload.get("Final_Exam_Marks", 0),
        "Internet_Access": payload.get("Internet_Access", "Unknown"),
        "Parental_Education": payload.get("Parental_Education", "Unknown"),
        "Extra_Curricular": payload.get("Extra_Curricular", "Unknown"),
        "Sleep_Hours": payload.get("Sleep_Hours", 0),
        "Previous_Grade": payload.get("Previous_Grade", "Unknown"),
    }
    return pd.DataFrame([record])


def _recommendation(prediction: str) -> str:
    mapping = {
        "Excellent": "Keep your momentum and challenge yourself with advanced coursework.",
        "Good": "Maintain your schedule and continue strengthening weak areas.",
        "Average": "Focus on attendance, homework, and targeted revision to improve outcomes.",
        "Poor": "Seek tutoring support and improve study habits immediately.",
    }
    return mapping.get(prediction, "Stay consistent and seek help when needed.")


def _risk_level(prediction: str) -> str:
    if prediction == "Poor":
        return "High"
    if prediction == "Average":
        return "Moderate"
    return "Low"


def _load_dataset_metrics() -> dict:
    if not DATASET_PATH.exists():
        return {}

    df = validate_and_clean_dataset(pd.read_csv(DATASET_PATH))
    performance_counts = df["Performance"].value_counts().to_dict()
    metrics = {
        "total_students": int(len(df)),
        "average_marks": round(float(df[["Midterm_Marks", "Final_Exam_Marks"]].mean().mean()), 1),
        "attendance_percentage": round(float(df["Attendance"].mean()), 1),
        "average_study_hours": round(float(df["Study_Hours"].mean()), 1),
        "average_assignment_completion": round(float(df["Assignments_Completed"].mean()), 1),
        "pass_percentage": round(float((df["Performance"].isin(["Excellent", "Good"]).sum() / len(df)) * 100), 1),
        "fail_percentage": round(float((df["Performance"].isin(["Average", "Poor"]).sum() / len(df)) * 100), 1),
        "top_performers": int(performance_counts.get("Excellent", 0)),
        "excellent": int(performance_counts.get("Excellent", 0)),
        "good": int(performance_counts.get("Good", 0)),
        "average": int(performance_counts.get("Average", 0)),
        "poor": int(performance_counts.get("Poor", 0)),
    }
    return metrics


def register_routes(app):
    app.register_blueprint(bp)


@bp.route("/api/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json(silent=True) or {}
        if not payload:
            return jsonify({"error": "Request body is required"}), 400

        X_input = _build_payload(payload)
        X_input = X_input[[
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
        ]]

        model = _load_model()
        prediction = model.predict(X_input)[0]
        probabilities = model.predict_proba(X_input)[0]
        confidence_score = round(float(max(probabilities)) * 100, 2)
        recommendation = _recommendation(prediction)
        risk_level = _risk_level(prediction)

        db: Session = SessionLocal()
        try:
            history = PredictionHistory(
                student_id=payload.get("Student_ID", "Unknown"),
                prediction=prediction,
                confidence_score=confidence_score,
                risk_level=risk_level,
                recommendation=recommendation,
                created_at=datetime.utcnow(),
            )
            db.add(history)
            db.commit()
        finally:
            db.close()

        return jsonify({
            "predicted_performance": prediction,
            "confidence_score": confidence_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@bp.route("/api/history", methods=["GET"])
def history():
    db: Session = SessionLocal()
    try:
        rows = db.query(PredictionHistory).order_by(PredictionHistory.created_at.desc()).all()
        return jsonify([
            {
                "id": row.id,
                "student_id": row.student_id,
                "prediction": row.prediction,
                "confidence_score": row.confidence_score,
                "risk_level": row.risk_level,
                "recommendation": row.recommendation,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ])
    finally:
        db.close()


@bp.route("/api/metrics", methods=["GET"])
def metrics():
    data_metrics = _load_dataset_metrics()
    if METRICS_PATH.exists():
        with open(METRICS_PATH, "r", encoding="utf-8") as handle:
            training_metrics = json.load(handle)
            training_metrics.update(data_metrics)
            return jsonify(training_metrics)
    return jsonify(data_metrics)


@bp.route("/api/students", methods=["GET"])
def students():
    db: Session = SessionLocal()
    try:
        rows = db.query(StudentRecord).all()
        if rows:
            return jsonify([
                {
                    "Student_ID": row.student_id,
                    "Gender": row.gender,
                    "Age": row.age,
                    "Class": row.class_name,
                    "Attendance": row.attendance,
                    "Study_Hours": row.study_hours,
                    "Assignments_Completed": row.assignments_completed,
                    "Quiz_Score": row.quiz_score,
                    "Midterm_Marks": row.midterm_marks,
                    "Final_Exam_Marks": row.final_exam_marks,
                    "Internet_Access": row.internet_access,
                    "Parental_Education": row.parental_education,
                    "Extra_Curricular": row.extra_curricular,
                    "Sleep_Hours": row.sleep_hours,
                    "Previous_Grade": row.previous_grade,
                    "Performance": row.performance,
                }
                for row in rows
            ])
        return jsonify([])
    finally:
        db.close()

@bp.route("/api/students", methods=["POST"])
def add_student():
    payload = request.get_json(silent=True) or {}
    if not payload:
        return jsonify({"error": "Request body is required"}), 400

    db: Session = SessionLocal()
    try:
        new_student = StudentRecord(
            student_id=str(payload.get("Student_ID", "Unknown")),
            gender=str(payload.get("Gender", "Unknown")),
            age=int(payload.get("Age", 0)) if payload.get("Age") else None,
            class_name=str(payload.get("Class", "Unknown")),
            attendance=float(payload.get("Attendance", 0)) if payload.get("Attendance") is not None else None,
            study_hours=float(payload.get("Study_Hours", 0)) if payload.get("Study_Hours") is not None else None,
            assignments_completed=float(payload.get("Assignments_Completed", 0)) if payload.get("Assignments_Completed") is not None else None,
            quiz_score=float(payload.get("Quiz_Score", 0)) if payload.get("Quiz_Score") is not None else None,
            midterm_marks=float(payload.get("Midterm_Marks", 0)) if payload.get("Midterm_Marks") is not None else None,
            final_exam_marks=float(payload.get("Final_Exam_Marks", 0)) if payload.get("Final_Exam_Marks") is not None else None,
            internet_access=str(payload.get("Internet_Access", "Unknown")),
            parental_education=str(payload.get("Parental_Education", "Unknown")),
            extra_curricular=str(payload.get("Extra_Curricular", "Unknown")),
            sleep_hours=float(payload.get("Sleep_Hours", 0)) if payload.get("Sleep_Hours") is not None else None,
            previous_grade=str(payload.get("Previous_Grade", "Unknown")),
            performance=str(payload.get("Performance", "Average")),
        )
        db.add(new_student)
        db.commit()
        return jsonify({"message": "Student added successfully"}), 201
    except Exception as exc:
        db.rollback()
        return jsonify({"error": str(exc)}), 500
    finally:
        db.close()

@bp.route("/api/students/<student_id>", methods=["PUT"])
def update_student(student_id):
    payload = request.get_json(silent=True) or {}
    db: Session = SessionLocal()
    try:
        student = db.query(StudentRecord).filter(StudentRecord.student_id == student_id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        if "Gender" in payload: student.gender = str(payload["Gender"])
        if "Age" in payload: student.age = int(payload["Age"])
        if "Class" in payload: student.class_name = str(payload["Class"])
        if "Attendance" in payload: student.attendance = float(payload["Attendance"])
        if "Study_Hours" in payload: student.study_hours = float(payload["Study_Hours"])
        if "Assignments_Completed" in payload: student.assignments_completed = float(payload["Assignments_Completed"])
        if "Quiz_Score" in payload: student.quiz_score = float(payload["Quiz_Score"])
        if "Midterm_Marks" in payload: student.midterm_marks = float(payload["Midterm_Marks"])
        if "Final_Exam_Marks" in payload: student.final_exam_marks = float(payload["Final_Exam_Marks"])
        if "Internet_Access" in payload: student.internet_access = str(payload["Internet_Access"])
        if "Parental_Education" in payload: student.parental_education = str(payload["Parental_Education"])
        if "Extra_Curricular" in payload: student.extra_curricular = str(payload["Extra_Curricular"])
        if "Sleep_Hours" in payload: student.sleep_hours = float(payload["Sleep_Hours"])
        if "Previous_Grade" in payload: student.previous_grade = str(payload["Previous_Grade"])
        if "Performance" in payload: student.performance = str(payload["Performance"])
            
        db.commit()
        return jsonify({"message": "Student updated successfully"}), 200
    except Exception as exc:
        db.rollback()
        return jsonify({"error": str(exc)}), 500
    finally:
        db.close()

@bp.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    db: Session = SessionLocal()
    try:
        student = db.query(StudentRecord).filter(StudentRecord.student_id == student_id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        db.delete(student)
        db.commit()
        return jsonify({"message": "Student deleted successfully"}), 200
    except Exception as exc:
        db.rollback()
        return jsonify({"error": str(exc)}), 500
    finally:
        db.close()



@bp.route("/api/upload", methods=["POST"])
def upload_dataset():
    try:
        uploaded_file = request.files.get("file")
        if not uploaded_file:
            return jsonify({"error": "No file uploaded"}), 400

        df = pd.read_csv(uploaded_file)
        cleaned = validate_and_clean_dataset(df)
        cleaned.to_csv(DATASET_PATH, index=False)

        db: Session = SessionLocal()
        try:
            db.query(StudentRecord).delete()
            for _, row in cleaned.iterrows():
                db.add(StudentRecord(
                    student_id=str(row.get("Student_ID", "Unknown")),
                    gender=str(row.get("Gender", "Unknown")),
                    age=int(row.get("Age", 0)) if pd.notna(row.get("Age")) else None,
                    class_name=str(row.get("Class", "Unknown")),
                    attendance=float(row.get("Attendance", 0)) if pd.notna(row.get("Attendance")) else None,
                    study_hours=float(row.get("Study_Hours", 0)) if pd.notna(row.get("Study_Hours")) else None,
                    assignments_completed=float(row.get("Assignments_Completed", 0)) if pd.notna(row.get("Assignments_Completed")) else None,
                    quiz_score=float(row.get("Quiz_Score", 0)) if pd.notna(row.get("Quiz_Score")) else None,
                    midterm_marks=float(row.get("Midterm_Marks", 0)) if pd.notna(row.get("Midterm_Marks")) else None,
                    final_exam_marks=float(row.get("Final_Exam_Marks", 0)) if pd.notna(row.get("Final_Exam_Marks")) else None,
                    internet_access=str(row.get("Internet_Access", "Unknown")),
                    parental_education=str(row.get("Parental_Education", "Unknown")),
                    extra_curricular=str(row.get("Extra_Curricular", "Unknown")),
                    sleep_hours=float(row.get("Sleep_Hours", 0)) if pd.notna(row.get("Sleep_Hours")) else None,
                    previous_grade=str(row.get("Previous_Grade", "Unknown")),
                    performance=str(row.get("Performance", "Average")),
                ))
            db.commit()
        finally:
            db.close()

        return jsonify({
            "message": "Dataset uploaded and processed successfully",
            "rows": len(cleaned),
            "columns": cleaned.columns.tolist(),
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

USERS_FILE = ROOT_DIR / "users.json"

def _load_users():
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_users(users_data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, indent=4)

@bp.route("/api/signup", methods=["POST"])
def signup():
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    password = payload.get("password")
    name = payload.get("name", "User")
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
        
    users = _load_users()
    if email in users:
        return jsonify({"error": "User already exists"}), 400
        
    users[email] = {
        "name": name,
        "password": password # In a real app, hash this!
    }
    _save_users(users)
    return jsonify({"message": "User created successfully", "user": {"email": email, "name": name}}), 201

@bp.route("/api/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    password = payload.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
        
    users = _load_users()
    if email not in users or users[email]["password"] != password:
        return jsonify({"error": "Invalid email or password"}), 401
        
    return jsonify({"message": "Login successful", "user": {"email": email, "name": users[email]["name"]}}), 200
