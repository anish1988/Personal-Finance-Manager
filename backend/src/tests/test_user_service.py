# backend/src/tests/test_user_service.py
import pytest
from domain.entities.user import User
from domain.repositories.user_repository import UserRepositoryInterface
from domain.services.user_service import UserService, UserAlreadyExists

class FakeUserRepo(UserRepositoryInterface):
    def __init__(self):
        self.users = []

    def create_user(self, user: User) -> User:
        user.id = len(self.users) + 1
        self.users.append(user)
        return user

    def get_user_by_email(self, email: str):
        for u in self.users:
            if u.email == email:
                return u
        return None

def test_register_user_success():
    repo = FakeUserRepo()
    svc = UserService(repo)
    user = svc.register_user("alice@example.com", "strongpassword")
    assert user.id == 1
    assert user.email == "alice@example.com"
    assert user.password_hash != "strongpassword"
    assert len(user.password_hash) > 0

def test_register_duplicate_raises():
    repo = FakeUserRepo()
    svc = UserService(repo)
    svc.register_user("bob@example.com", "strongpassword")
    with pytest.raises(UserAlreadyExists):
        svc.register_user("bob@example.com", "anotherpassword")

def test_register_invalid_password():
    repo = FakeUserRepo()
    svc = UserService(repo)
    with pytest.raises(ValueError):
        svc.register_user("carol@example.com", "short")
