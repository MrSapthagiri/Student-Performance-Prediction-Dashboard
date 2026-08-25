"""
Repository for Student CRUD operations with pagination, filtering, and soft-delete.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database.models import Student


class StudentRepository:

    @staticmethod
    def create(db: Session, data: dict) -> Student:
        student = Student(**data)
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def get_by_student_id(db: Session, student_id: int):
        return db.query(Student).filter(
            Student.student_id == student_id, Student.is_active == True
        ).first()

    @staticmethod
    def get_by_id(db: Session, pk: int):
        return db.query(Student).filter(
            Student.id == pk, Student.is_active == True
        ).first()

    @staticmethod
    def get_all(db: Session, offset: int = 0, limit: int = 50,
                search: str = None, department: str = None,
                year: int = None, semester: int = None,
                risk_level: str = None, sort_by: str = "student_id",
                sort_order: str = "asc"):
        query = db.query(Student).filter(Student.is_active == True)

        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Student.student_name.ilike(pattern),
                    Student.register_number.ilike(pattern),
                    Student.email.ilike(pattern),
                    Student.student_id.cast(String).ilike(pattern),
                )
            )

        if department and department != "All":
            query = query.filter(Student.department == department)
        if year and year != 0:
            query = query.filter(Student.year == year)
        if semester and semester != 0:
            query = query.filter(Student.semester == semester)
        if risk_level and risk_level != "All":
            query = query.filter(Student.risk_level == risk_level)

        # Sort
        sort_col = getattr(Student, sort_by, Student.student_id)
        if sort_order == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())

        total = query.count()
        students = query.offset(offset).limit(limit).all()
        return students, total

    @staticmethod
    def update(db: Session, student_id: int, data: dict):
        student = db.query(Student).filter(
            Student.student_id == student_id, Student.is_active == True
        ).first()
        if not student:
            return None
        for key, value in data.items():
            if hasattr(student, key):
                setattr(student, key, value)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def soft_delete(db: Session, student_id: int):
        student = db.query(Student).filter(
            Student.student_id == student_id
        ).first()
        if student:
            student.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def hard_delete(db: Session, student_id: int):
        student = db.query(Student).filter(
            Student.student_id == student_id
        ).first()
        if student:
            db.delete(student)
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session, active_only: bool = True):
        query = db.query(func.count(Student.id))
        if active_only:
            query = query.filter(Student.is_active == True)
        return query.scalar()

    @staticmethod
    def get_departments(db: Session):
        results = db.query(Student.department).filter(
            Student.is_active == True
        ).distinct().order_by(Student.department).all()
        return [r[0] for r in results]

    @staticmethod
    def get_stats(db: Session):
        """Get aggregate statistics for dashboard."""
        from sqlalchemy import func as f
        active = db.query(Student).filter(Student.is_active == True)
        total = active.count()
        if total == 0:
            return {
                "total": 0, "avg_attendance": 0, "avg_performance": 0,
                "pass_rate": 0, "high_risk": 0, "medium_risk": 0, "low_risk": 0,
            }
        avg_att = active.with_entities(f.avg(Student.attendance_percentage)).scalar() or 0
        avg_perf = active.with_entities(f.avg(Student.final_score)).scalar() or 0
        pass_count = active.filter(Student.pass_fail == "Pass").count()
        high = active.filter(Student.risk_level == "High").count()
        medium = active.filter(Student.risk_level == "Medium").count()
        low = active.filter(Student.risk_level == "Low").count()
        return {
            "total": total,
            "avg_attendance": round(avg_att, 2),
            "avg_performance": round(avg_perf, 2),
            "pass_rate": round(pass_count / total * 100, 2) if total else 0,
            "high_risk": high,
            "medium_risk": medium,
            "low_risk": low,
        }

    @staticmethod
    def get_department_stats(db: Session):
        """Get per-department aggregated stats."""
        from sqlalchemy import func as f
        results = db.query(
            Student.department,
            f.count(Student.id).label("count"),
            f.avg(Student.final_score).label("avg_score"),
            f.avg(Student.attendance_percentage).label("avg_attendance"),
        ).filter(Student.is_active == True).group_by(Student.department).all()
        return [
            {"department": r.department, "count": r.count,
             "avg_score": round(r.avg_score, 2), "avg_attendance": round(r.avg_attendance, 2)}
            for r in results
        ]

    @staticmethod
    def get_risk_distribution(db: Session):
        from sqlalchemy import func as f
        results = db.query(
            Student.risk_level, f.count(Student.id)
        ).filter(Student.is_active == True).group_by(Student.risk_level).all()
        return {r[0]: r[1] for r in results}

    @staticmethod
    def get_grade_distribution(db: Session):
        from sqlalchemy import func as f
        results = db.query(
            Student.grade, f.count(Student.id)
        ).filter(Student.is_active == True).group_by(Student.grade).all()
        return {r[0]: r[1] for r in results}

    @staticmethod
    def get_next_student_id(db: Session):
        from sqlalchemy import func as f
        max_id = db.query(f.max(Student.student_id)).scalar()
        return (max_id or 0) + 1
