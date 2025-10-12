from domain.repositories.user_repository import UserRepositoryInterface
from domain.entities.user import User
import bcrypt

class UserService:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def register_user(self, email: str, password: str) -> User:
        if self.user_repo.get_user_by_email(email):
            raise ValueError("Email already registered")
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(id=None, email=email, hashed_password=hashed)
        return self.user_repo.create_user(user)

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.user_repo.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
            return user
        return None
