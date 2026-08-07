from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class StudentRecord(Base):
    __tablename__ = "student_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), nullable=False)
    gender = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    class_name = Column(String(50), nullable=True)
    attendance = Column(Float, nullable=True)
    study_hours = Column(Float, nullable=True)
    assignments_completed = Column(Float, nullable=True)
    quiz_score = Column(Float, nullable=True)
    midterm_marks = Column(Float, nullable=True)
    final_exam_marks = Column(Float, nullable=True)
    internet_access = Column(String(20), nullable=True)
    parental_education = Column(String(100), nullable=True)
    extra_curricular = Column(String(20), nullable=True)
    sleep_hours = Column(Float, nullable=True)
    previous_grade = Column(String(20), nullable=True)
    performance = Column(String(20), nullable=True)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), nullable=True)
    prediction = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=True)
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
