import pytest
from domain.services.user_service import UserService
from domain.repositories.user_repository import UserRepositoryInterface
from domain.entities.user import User

class FakeUserRepo(UserRepositoryInterface):
    def __init__(self):
        self.users = []

    def create_user(self, user: User) -> User:
        user.id = len(self.users) + 1
        self.users.append(user)
        return user

    def get_user_by_email(self, email: str) -> User | None:
        for u in self.users:
            if u.email == email:
                return u
        return None

def test_register_user():
    repo = FakeUserRepo()
    service = UserService(repo)
    user = service.register_user("test@example.com", "password123")
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.hashed_password != "password123"  # ensure hashed
