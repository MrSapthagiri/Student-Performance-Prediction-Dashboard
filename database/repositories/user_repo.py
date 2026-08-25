"""
Repository for User CRUD operations.
"""

from sqlalchemy.orm import Session
from database.models import User
import bcrypt


class UserRepository:

    @staticmethod
    def create(db: Session, full_name: str, email: str, password: str, role: str = "Student") -> User:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(full_name=full_name, email=email, password_hash=hashed, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email, User.is_active == True).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def update(db: Session, user_id: int, **kwargs):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        for key, value in kwargs.items():
            if key == "password":
                setattr(user, "password_hash", bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
            elif hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_all(db: Session):
        return db.query(User).filter(User.is_active == True).all()
