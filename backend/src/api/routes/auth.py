from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...domain.services.user_service import UserService
from ...domain.services.jwt_service import JWTService
from ...domain.repositories.user_repository import UserRepositoryInterface
from src.infrastructure.db.postgres_repository import PostgresUserRepository
from ...domain.entities.user import User
from src.api.dependencies import get_db
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user_repo: UserRepositoryInterface = PostgresUserRepository(db)
    service = UserService(user_repo)
    try:
        user = service.register_user(request.email, request.password)
        return RegisterResponse(id=user.id, email=user.email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=LoginResponse)

@router.get("/", summary="auth root / health")
async def auth_root():
    return {"message": "Auth router is mounted (use /auth/register for registration)"}


def login(request: LoginRequest, db: Session = Depends(get_db)):
    user_repo: UserRepositoryInterface = PostgresUserRepository(db)
    service = UserService(user_repo)
    user = service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = JWTService.create_token(user.id)
    return LoginResponse(access_token=token)
