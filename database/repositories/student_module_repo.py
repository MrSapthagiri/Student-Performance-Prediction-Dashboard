"""
Repository for StudentModule (academic records / attendance) CRUD operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import StudentModule


class StudentModuleRepository:

    @staticmethod
    def create(db: Session, data: dict) -> StudentModule:
        sm = StudentModule(**data)
        db.add(sm)
        db.commit()
        db.refresh(sm)
        return sm

    @staticmethod
    def get_by_id(db: Session, record_id: int):
        return db.query(StudentModule).filter(StudentModule.id == record_id).first()

    @staticmethod
    def get_by_student(db: Session, student_id: int):
        return db.query(StudentModule).filter(
            StudentModule.student_id == student_id
        ).all()

    @staticmethod
    def get_by_module(db: Session, module_id: int):
        return db.query(StudentModule).filter(
            StudentModule.module_id == module_id
        ).all()

    @staticmethod
    def get_by_student_and_module(db: Session, student_id: int, module_id: int):
        return db.query(StudentModule).filter(
            StudentModule.student_id == student_id,
            StudentModule.module_id == module_id,
        ).first()

    @staticmethod
    def get_all(db: Session, offset: int = 0, limit: int = 50,
                student_id: int = None, module_id: int = None):
        query = db.query(StudentModule)
        if student_id:
            query = query.filter(StudentModule.student_id == student_id)
        if module_id:
            query = query.filter(StudentModule.module_id == module_id)
        total = query.count()
        records = query.offset(offset).limit(limit).all()
        return records, total

    @staticmethod
    def update(db: Session, record_id: int, data: dict):
        sm = db.query(StudentModule).filter(StudentModule.id == record_id).first()
        if not sm:
            return None
        for key, value in data.items():
            if hasattr(sm, key):
                setattr(sm, key, value)
        # Auto-calculate total and grade
        if any(k in data for k in ['internal_marks', 'assignment_marks', 'quiz_marks', 'midterm_marks', 'final_exam_marks']):
            internal = sm.internal_marks or 0
            assignment = sm.assignment_marks or 0
            quiz = sm.quiz_marks or 0
            midterm = sm.midterm_marks or 0
            final_exam = sm.final_exam_marks or 0
            total = round(
                (internal / 40) * 20 + (assignment / 25) * 10 + (quiz / 20) * 10 +
                (midterm / 50) * 25 + (final_exam / 75) * 35, 2
            )
            sm.total_marks = total
            if total >= 90: sm.grade = "O"
            elif total >= 80: sm.grade = "A+"
            elif total >= 70: sm.grade = "A"
            elif total >= 60: sm.grade = "B+"
            elif total >= 50: sm.grade = "B"
            elif total >= 40: sm.grade = "C"
            else: sm.grade = "F"
            sm.result = "Pass" if total >= 40 else "Fail"
        db.commit()
        db.refresh(sm)
        return sm

    @staticmethod
    def delete(db: Session, record_id: int):
        sm = db.query(StudentModule).filter(StudentModule.id == record_id).first()
        if sm:
            db.delete(sm)
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session):
        return db.query(func.count(StudentModule.id)).scalar()
