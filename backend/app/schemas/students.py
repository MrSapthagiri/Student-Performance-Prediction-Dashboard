from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class StudentBase(BaseModel):
    student_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    department: str
    course: Optional[str] = None
    year: int
    semester: int
    section: Optional[str] = None
    academic_year: Optional[str] = None
    previous_gpa: Optional[float] = None
    attendance_percentage: Optional[float] = None
    internal_marks: Optional[float] = None
    assignment_score: Optional[float] = None

class StudentCreate(StudentBase):
    user_id: Optional[int] = None

class StudentResponse(StudentBase):
    id: int
    user_id: Optional[int] = None
    risk_level: Optional[str] = None
    predicted_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
