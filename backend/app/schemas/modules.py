from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ModuleBase(BaseModel):
    module_code: str
    module_name: str
    department: str
    semester: int
    credits: int
    faculty: Optional[str] = None
    maximum_marks: float = 100.0
    passing_marks: float = 40.0
    academic_year: Optional[str] = None

class ModuleCreate(ModuleBase):
    pass

class ModuleResponse(ModuleBase):
    id: int

    class Config:
        from_attributes = True

class StudentModuleBase(BaseModel):
    student_id: int
    module_id: int
    internal_marks: Optional[float] = None
    assignment_marks: Optional[float] = None
    quiz_marks: Optional[float] = None
    attendance: Optional[float] = None
    practical_marks: Optional[float] = None
    theory_marks: Optional[float] = None
    final_exam_marks: Optional[float] = None
    total_marks: Optional[float] = None
    grade: Optional[str] = None
    result: Optional[str] = None
    semester: Optional[int] = None

class StudentModuleCreate(StudentModuleBase):
    pass

class StudentModuleResponse(StudentModuleBase):
    id: int

    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    id: int
    student_id: int
    predicted_score: float
    pass_probability: float
    risk_level: str
    confidence: float
    shap_explanation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    id: int
    student_id: int
    recommendation_text: str
    created_at: datetime

    class Config:
        from_attributes = True

class InterventionBase(BaseModel):
    student_id: int
    module_id: Optional[int] = None
    risk_level: str
    main_risk_factor: str
    recommended_action: str
    status: str = "Pending"

class InterventionCreate(InterventionBase):
    pass

class InterventionResponse(InterventionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
