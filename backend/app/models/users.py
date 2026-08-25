from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Enum, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.database import Base

class RoleEnum(str, enum.Enum):
    admin = "Admin"
    faculty = "Faculty"
    student = "Student"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=RoleEnum.student.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False)

