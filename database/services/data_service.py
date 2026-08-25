"""
Data service — provides a unified interface for all entity operations.
"""

from database.connection import get_db
from database.repositories.student_repo import StudentRepository
from database.repositories.module_repo import ModuleRepository
from database.repositories.student_module_repo import StudentModuleRepository
from database.repositories.intervention_repo import InterventionRepository


class DataService:
    """Thin business-logic layer that manages DB sessions for Streamlit pages."""

    # ── Students ──────────────────────────────────────────────
    @staticmethod
    def get_students(**kwargs):
        db = get_db()
        try:
            return StudentRepository.get_all(db, **kwargs)
        finally:
            db.close()

    @staticmethod
    def get_student(student_id: int):
        db = get_db()
        try:
            return StudentRepository.get_by_student_id(db, student_id)
        finally:
            db.close()

    @staticmethod
    def create_student(data: dict):
        db = get_db()
        try:
            return StudentRepository.create(db, data)
        finally:
            db.close()

    @staticmethod
    def update_student(student_id: int, data: dict):
        db = get_db()
        try:
            return StudentRepository.update(db, student_id, data)
        finally:
            db.close()

    @staticmethod
    def delete_student(student_id: int):
        db = get_db()
        try:
            return StudentRepository.soft_delete(db, student_id)
        finally:
            db.close()

    @staticmethod
    def get_student_stats():
        db = get_db()
        try:
            return StudentRepository.get_stats(db)
        finally:
            db.close()

    @staticmethod
    def get_department_stats():
        db = get_db()
        try:
            return StudentRepository.get_department_stats(db)
        finally:
            db.close()

    @staticmethod
    def get_risk_distribution():
        db = get_db()
        try:
            return StudentRepository.get_risk_distribution(db)
        finally:
            db.close()

    @staticmethod
    def get_grade_distribution():
        db = get_db()
        try:
            return StudentRepository.get_grade_distribution(db)
        finally:
            db.close()

    @staticmethod
    def get_departments():
        db = get_db()
        try:
            return StudentRepository.get_departments(db)
        finally:
            db.close()

    @staticmethod
    def get_next_student_id():
        db = get_db()
        try:
            return StudentRepository.get_next_student_id(db)
        finally:
            db.close()

    # ── Modules ───────────────────────────────────────────────
    @staticmethod
    def get_modules(**kwargs):
        db = get_db()
        try:
            return ModuleRepository.get_all(db, **kwargs)
        finally:
            db.close()

    @staticmethod
    def get_module(module_id: int):
        db = get_db()
        try:
            return ModuleRepository.get_by_module_id(db, module_id)
        finally:
            db.close()

    @staticmethod
    def create_module(data: dict):
        db = get_db()
        try:
            return ModuleRepository.create(db, data)
        finally:
            db.close()

    @staticmethod
    def update_module(module_id: int, data: dict):
        db = get_db()
        try:
            return ModuleRepository.update(db, module_id, data)
        finally:
            db.close()

    @staticmethod
    def delete_module(module_id: int):
        db = get_db()
        try:
            return ModuleRepository.soft_delete(db, module_id)
        finally:
            db.close()

    @staticmethod
    def get_module_count():
        db = get_db()
        try:
            return ModuleRepository.count(db)
        finally:
            db.close()

    @staticmethod
    def get_next_module_id():
        db = get_db()
        try:
            return ModuleRepository.get_next_module_id(db)
        finally:
            db.close()

    @staticmethod
    def get_module_stats(module_id: int):
        db = get_db()
        try:
            return ModuleRepository.get_module_stats(db, module_id)
        finally:
            db.close()

    # ── Student Modules (Academic Records / Attendance) ───────
    @staticmethod
    def get_student_modules(**kwargs):
        db = get_db()
        try:
            return StudentModuleRepository.get_all(db, **kwargs)
        finally:
            db.close()

    @staticmethod
    def get_student_module_record(record_id: int):
        db = get_db()
        try:
            return StudentModuleRepository.get_by_id(db, record_id)
        finally:
            db.close()

    @staticmethod
    def get_records_for_student(student_id: int):
        db = get_db()
        try:
            return StudentModuleRepository.get_by_student(db, student_id)
        finally:
            db.close()

    @staticmethod
    def get_records_for_module(module_id: int):
        db = get_db()
        try:
            return StudentModuleRepository.get_by_module(db, module_id)
        finally:
            db.close()

    @staticmethod
    def create_student_module(data: dict):
        db = get_db()
        try:
            return StudentModuleRepository.create(db, data)
        finally:
            db.close()

    @staticmethod
    def update_student_module(record_id: int, data: dict):
        db = get_db()
        try:
            return StudentModuleRepository.update(db, record_id, data)
        finally:
            db.close()

    @staticmethod
    def delete_student_module(record_id: int):
        db = get_db()
        try:
            return StudentModuleRepository.delete(db, record_id)
        finally:
            db.close()

    # ── Interventions ─────────────────────────────────────────
    @staticmethod
    def get_interventions(**kwargs):
        db = get_db()
        try:
            return InterventionRepository.get_all(db, **kwargs)
        finally:
            db.close()

    @staticmethod
    def get_intervention(intervention_id: int):
        db = get_db()
        try:
            return InterventionRepository.get_by_id(db, intervention_id)
        finally:
            db.close()

    @staticmethod
    def get_student_interventions(student_id: int):
        db = get_db()
        try:
            return InterventionRepository.get_by_student(db, student_id)
        finally:
            db.close()

    @staticmethod
    def create_intervention(data: dict):
        db = get_db()
        try:
            return InterventionRepository.create(db, data)
        finally:
            db.close()

    @staticmethod
    def update_intervention_status(intervention_id: int, status: str, notes: str = None):
        db = get_db()
        try:
            return InterventionRepository.update_status(db, intervention_id, status, notes)
        finally:
            db.close()

    @staticmethod
    def delete_intervention(intervention_id: int):
        db = get_db()
        try:
            return InterventionRepository.delete(db, intervention_id)
        finally:
            db.close()

    @staticmethod
    def get_intervention_status_counts():
        db = get_db()
        try:
            return InterventionRepository.get_status_counts(db)
        finally:
            db.close()

    # ── Bulk helpers ──────────────────────────────────────────
    @staticmethod
    def get_all_students_as_df():
        """Return all active students as a pandas DataFrame (for ML)."""
        import pandas as pd
        db = get_db()
        try:
            from database.models import Student
            from sqlalchemy import text
            result = db.execute(
                text("SELECT * FROM students WHERE is_active = true")
            )
            cols = result.keys()
            rows = result.fetchall()
            return pd.DataFrame(rows, columns=cols)
        finally:
            db.close()

    @staticmethod
    def get_all_student_modules_as_df():
        import pandas as pd
        db = get_db()
        try:
            from sqlalchemy import text
            result = db.execute(text("SELECT * FROM student_modules"))
            cols = result.keys()
            rows = result.fetchall()
            return pd.DataFrame(rows, columns=cols)
        finally:
            db.close()
