from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Optional link to user account
    student_id = Column(String, unique=True, index=True) # E.g., Register Number
    name = Column(String)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    department = Column(String)
    course = Column(String, nullable=True)
    year = Column(Integer)
    semester = Column(Integer)
    section = Column(String, nullable=True)
    academic_year = Column(String, nullable=True)

    # Base academic details (can be updated from Excel)
    previous_gpa = Column(Float, nullable=True)
    attendance_percentage = Column(Float, nullable=True)
    internal_marks = Column(Float, nullable=True)
    assignment_score = Column(Float, nullable=True)

    # Risk and Predictions
    risk_level = Column(String, nullable=True) # LOW, MEDIUM, HIGH
    predicted_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    modules = relationship("StudentModule", back_populates="student")
    predictions = relationship("Prediction", back_populates="student")
    recommendations = relationship("Recommendation", back_populates="student")
    interventions = relationship("Intervention", back_populates="student")
