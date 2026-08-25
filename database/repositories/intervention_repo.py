"""
Repository for Intervention CRUD operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Intervention


VALID_STATUSES = ["Pending", "Contacted", "Intervention Started", "Monitoring", "Resolved"]


class InterventionRepository:

    @staticmethod
    def create(db: Session, data: dict) -> Intervention:
        intervention = Intervention(**data)
        db.add(intervention)
        db.commit()
        db.refresh(intervention)
        return intervention

    @staticmethod
    def get_by_id(db: Session, intervention_id: int):
        return db.query(Intervention).filter(Intervention.id == intervention_id).first()

    @staticmethod
    def get_by_student(db: Session, student_id: int):
        return db.query(Intervention).filter(
            Intervention.student_id == student_id
        ).order_by(Intervention.created_at.desc()).all()

    @staticmethod
    def get_all(db: Session, offset: int = 0, limit: int = 50,
                status: str = None, risk_level: str = None):
        query = db.query(Intervention)
        if status and status != "All":
            query = query.filter(Intervention.status == status)
        if risk_level and risk_level != "All":
            query = query.filter(Intervention.risk_level == risk_level)
        query = query.order_by(Intervention.created_at.desc())
        total = query.count()
        records = query.offset(offset).limit(limit).all()
        return records, total

    @staticmethod
    def update_status(db: Session, intervention_id: int, status: str, notes: str = None):
        intervention = db.query(Intervention).filter(
            Intervention.id == intervention_id
        ).first()
        if not intervention:
            return None
        if status in VALID_STATUSES:
            intervention.status = status
        if notes is not None:
            intervention.notes = notes
        db.commit()
        db.refresh(intervention)
        return intervention

    @staticmethod
    def update(db: Session, intervention_id: int, data: dict):
        intervention = db.query(Intervention).filter(
            Intervention.id == intervention_id
        ).first()
        if not intervention:
            return None
        for key, value in data.items():
            if hasattr(intervention, key):
                setattr(intervention, key, value)
        db.commit()
        db.refresh(intervention)
        return intervention

    @staticmethod
    def delete(db: Session, intervention_id: int):
        intervention = db.query(Intervention).filter(
            Intervention.id == intervention_id
        ).first()
        if intervention:
            db.delete(intervention)
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session, status: str = None):
        query = db.query(func.count(Intervention.id))
        if status:
            query = query.filter(Intervention.status == status)
        return query.scalar()

    @staticmethod
    def get_status_counts(db: Session):
        results = db.query(
            Intervention.status, func.count(Intervention.id)
        ).group_by(Intervention.status).all()
        return {r[0]: r[1] for r in results}
