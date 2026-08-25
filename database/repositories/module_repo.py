"""
Repository for Module CRUD operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from database.models import Module, StudentModule


class ModuleRepository:

    @staticmethod
    def create(db: Session, data: dict) -> Module:
        module = Module(**data)
        db.add(module)
        db.commit()
        db.refresh(module)
        return module

    @staticmethod
    def get_by_module_id(db: Session, module_id: int):
        return db.query(Module).filter(
            Module.module_id == module_id, Module.is_active == True
        ).first()

    @staticmethod
    def get_by_code(db: Session, code: str):
        return db.query(Module).filter(
            Module.module_code == code, Module.is_active == True
        ).first()

    @staticmethod
    def get_all(db: Session, offset: int = 0, limit: int = 50,
                search: str = None, department: str = None,
                semester: int = None, sort_by: str = "module_id",
                sort_order: str = "asc"):
        query = db.query(Module).filter(Module.is_active == True)

        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Module.module_name.ilike(pattern),
                    Module.module_code.ilike(pattern),
                )
            )
        if department and department != "All":
            query = query.filter(Module.department == department)
        if semester and semester != 0:
            query = query.filter(Module.semester == semester)

        sort_col = getattr(Module, sort_by, Module.module_id)
        if sort_order == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())

        total = query.count()
        modules = query.offset(offset).limit(limit).all()
        return modules, total

    @staticmethod
    def update(db: Session, module_id: int, data: dict):
        module = db.query(Module).filter(
            Module.module_id == module_id, Module.is_active == True
        ).first()
        if not module:
            return None
        for key, value in data.items():
            if hasattr(module, key):
                setattr(module, key, value)
        db.commit()
        db.refresh(module)
        return module

    @staticmethod
    def soft_delete(db: Session, module_id: int):
        module = db.query(Module).filter(Module.module_id == module_id).first()
        if module:
            module.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session, active_only: bool = True):
        query = db.query(func.count(Module.id))
        if active_only:
            query = query.filter(Module.is_active == True)
        return query.scalar()

    @staticmethod
    def get_next_module_id(db: Session):
        max_id = db.query(func.max(Module.module_id)).scalar()
        return (max_id or 0) + 1

    @staticmethod
    def get_module_stats(db: Session, module_id: int):
        """Get aggregate stats for a specific module."""
        records = db.query(StudentModule).filter(
            StudentModule.module_id == module_id
        ).all()
        if not records:
            return {"enrolled": 0, "avg_marks": 0, "highest": 0, "lowest": 0,
                    "pass_rate": 0, "fail_rate": 0, "avg_attendance": 0}
        totals = [r.total_marks for r in records if r.total_marks is not None]
        attends = [r.attendance_percentage for r in records if r.attendance_percentage is not None]
        passed = sum(1 for r in records if r.result == "Pass")
        n = len(records)
        return {
            "enrolled": n,
            "avg_marks": round(sum(totals) / len(totals), 2) if totals else 0,
            "highest": round(max(totals), 2) if totals else 0,
            "lowest": round(min(totals), 2) if totals else 0,
            "pass_rate": round(passed / n * 100, 2) if n else 0,
            "fail_rate": round((n - passed) / n * 100, 2) if n else 0,
            "avg_attendance": round(sum(attends) / len(attends), 2) if attends else 0,
        }
