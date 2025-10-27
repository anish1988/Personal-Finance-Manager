# backend/src/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from src.config.settings import settings
from infrastructure.db.models import Base
from domain.services.jwt_service import JWTService, TokenError
from infrastructure.db.postgres_repository import PostgresUserRepository
from domain.entities.user import User as DomainUser

# DB session setup (same as before)
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                     db = Depends(get_db)) -> DomainUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization credentials")
    token = credentials.credentials
    try:
        user_id = JWTService.decode_token(token)
    except TokenError as te:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(te))
    # fetch user from DB
    user_repo = PostgresUserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
