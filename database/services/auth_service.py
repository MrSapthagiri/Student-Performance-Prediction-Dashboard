"""
Authentication service — wraps UserRepository for login/signup business logic.
"""

from database.connection import get_db
from database.repositories.user_repo import UserRepository


class AuthService:

    @staticmethod
    def signup(full_name: str, email: str, password: str, role: str = "Student"):
        db = get_db()
        try:
            existing = UserRepository.get_by_email(db, email)
            if existing:
                return None, "An account with this email already exists."
            if role == "Admin":
                return None, "Admin accounts cannot be created via signup."
            user = UserRepository.create(db, full_name, email, password, role)
            return user, None
        finally:
            db.close()

    @staticmethod
    def login(email: str, password: str):
        db = get_db()
        try:
            user = UserRepository.get_by_email(db, email)
            if not user:
                return None, "Invalid email or password."
            if not UserRepository.verify_password(password, user.password_hash):
                return None, "Invalid email or password."
            return {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
            }, None
        finally:
            db.close()

    @staticmethod
    def get_user(user_id: int):
        db = get_db()
        try:
            return UserRepository.get_by_id(db, user_id)
        finally:
            db.close()

    @staticmethod
    def update_profile(user_id: int, **kwargs):
        db = get_db()
        try:
            return UserRepository.update(db, user_id, **kwargs)
        finally:
            db.close()
