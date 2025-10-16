from sqlalchemy.orm import Session
from ...domain.repositories.user_repository import UserRepositoryInterface
from ...domain.entities.user import User
from src.infrastructure.db.models import User as UserModel

class PostgresUserRepository(UserRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: User) -> User:
        db_user = UserModel(email=user.email, password_hash=user.password_hash)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        user.id = db_user.id
        user.created_at = db_user.created_at
        user.updated_at = db_user.updated_at
        return user

    def get_user_by_email(self, email: str) -> User | None:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not db_user:
            return None
        return User(
            id=db_user.id,
            email=db_user.email,
            password_hash=db_user.password_hash,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )

