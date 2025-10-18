# backend/src/domain/services/user_service.py
from ..repositories.user_repository import UserRepositoryInterface
from ..entities.user import User
import bcrypt
from typing import Optional

class UserAlreadyExists(Exception):
    pass

class UserService:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def register_user(self, email: str, password: str) -> User:
        # basic validations (can be extended)
        if not email or "@" not in email:
            raise ValueError("Invalid email")
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        existing = self.user_repo.get_user_by_email(email)
        if existing:
            raise UserAlreadyExists("Email already registered")

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = User(id=None, email=email, password_hash=hashed)
        return self.user_repo.create_user(user)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.user_repo.get_user_by_email(email)
        if not user:
            return None
        if bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return user
        return None
