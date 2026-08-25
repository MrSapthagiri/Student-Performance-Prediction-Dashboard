from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    module_code = Column(String, unique=True, index=True)
    module_name = Column(String)
    department = Column(String)
    semester = Column(Integer)
    credits = Column(Integer)
    faculty = Column(String, nullable=True)
    maximum_marks = Column(Float, default=100.0)
    passing_marks = Column(Float, default=40.0)
    academic_year = Column(String, nullable=True)

    # Relationships
    student_mappings = relationship("StudentModule", back_populates="module")

class StudentModule(Base):
    __tablename__ = "student_modules"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    module_id = Column(Integer, ForeignKey("modules.id"))
    
    # Marks and Performance
    internal_marks = Column(Float, nullable=True)
    assignment_marks = Column(Float, nullable=True)
    quiz_marks = Column(Float, nullable=True)
    attendance = Column(Float, nullable=True)
    practical_marks = Column(Float, nullable=True)
    theory_marks = Column(Float, nullable=True)
    final_exam_marks = Column(Float, nullable=True)
    total_marks = Column(Float, nullable=True)
    
    grade = Column(String, nullable=True)
    result = Column(String, nullable=True) # Pass / Fail
    semester = Column(Integer, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="modules")
    module = relationship("Module", back_populates="student_mappings")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    predicted_score = Column(Float)
    pass_probability = Column(Float)
    risk_level = Column(String) # LOW, MEDIUM, HIGH
    confidence = Column(Float)
    shap_explanation = Column(Text, nullable=True) # JSON string of SHAP values
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="predictions")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    recommendation_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="recommendations")

class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)
    risk_level = Column(String)
    main_risk_factor = Column(String)
    recommended_action = Column(Text)
    status = Column(String, default="Pending") # Pending, Contacted, Intervention Started, Monitoring, Resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="interventions")
    module = relationship("Module")
