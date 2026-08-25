"""
SQLAlchemy ORM models for Student Success AI.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(300), nullable=False)
    role = Column(String(20), nullable=False, default="Student")  # Admin, Faculty, Student
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, unique=True, nullable=False, index=True)
    register_number = Column(String(50), unique=True, nullable=False)
    student_name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    phone = Column(String(20))
    gender = Column(String(10))
    department = Column(String(100), nullable=False, index=True)
    course = Column(String(200))
    year = Column(Integer)
    semester = Column(Integer)
    section = Column(String(5))
    academic_year = Column(String(20))

    # Academic
    previous_gpa = Column(Float)
    previous_percentage = Column(Float)
    internal_marks = Column(Float)
    assignment_score = Column(Float)
    quiz_score = Column(Float)
    midterm_score = Column(Float)
    final_exam_score = Column(Float)

    # Attendance
    classes_held = Column(Integer)
    classes_attended = Column(Integer)
    attendance_percentage = Column(Float)

    # Learning behaviour
    study_hours_per_day = Column(Float)
    assignment_completion_rate = Column(Float)
    online_learning_hours = Column(Float)
    library_usage = Column(Integer)
    participation_score = Column(Float)

    # Outcome
    final_score = Column(Float)
    grade = Column(String(5))
    pass_fail = Column(String(10))
    risk_level = Column(String(10))

    # Soft delete
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    module_records = relationship("StudentModule", back_populates="student", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.student_id}: {self.student_name}>"


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(Integer, unique=True, nullable=False, index=True)
    module_code = Column(String(30), unique=True, nullable=False)
    module_name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    semester = Column(Integer)
    credits = Column(Integer)
    max_marks = Column(Integer, default=100)
    pass_marks = Column(Integer, default=40)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_records = relationship("StudentModule", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module {self.module_code}: {self.module_name}>"


class StudentModule(Base):
    __tablename__ = "student_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.module_id", ondelete="CASCADE"), nullable=False, index=True)

    attendance_percentage = Column(Float)
    internal_marks = Column(Float)
    assignment_marks = Column(Float)
    quiz_marks = Column(Float)
    midterm_marks = Column(Float)
    final_exam_marks = Column(Float)
    total_marks = Column(Float)
    grade = Column(String(5))
    result = Column(String(10))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="module_records")
    module = relationship("Module", back_populates="student_records")

    def __repr__(self):
        return f"<StudentModule student={self.student_id} module={self.module_id}>"


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.module_id", ondelete="SET NULL"), nullable=True)

    risk_level = Column(String(10))
    predicted_score = Column(Float)
    main_risk_factor = Column(Text)
    recommendation = Column(Text)
    status = Column(String(30), default="Pending")  # Pending, Contacted, Intervention Started, Monitoring, Resolved
    notes = Column(Text)
    assigned_to = Column(String(200))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="interventions")

    def __repr__(self):
        return f"<Intervention student={self.student_id} status={self.status}>"
