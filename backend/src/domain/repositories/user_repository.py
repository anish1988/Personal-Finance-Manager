from abc import ABC, abstractmethod
from domain.entities.user import User

class UserRepositoryInterface(ABC):
    @abstractmethod
    def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User | None:
        pass
