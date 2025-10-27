from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from domain.services.user_service import UserService, UserAlreadyExists
from src.domain.services.jwt_service import JWTService
from domain.repositories.user_repository import UserRepositoryInterface
from infrastructure.db.postgres_repository import PostgresUserRepository
from api.dependencies import get_current_user
from domain.entities.user import User
from api.dependencies import get_db
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

class MeResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: str | None

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user_repo: UserRepositoryInterface = PostgresUserRepository(db)
    svc = UserService(user_repo)
    try:
        user = svc.register_user(request.email, request.password)
        return RegisterResponse(id=user.id, email=user.email)
    except UserAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        # log in real app; keep response generic for tests
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user_repo: UserRepositoryInterface = PostgresUserRepository(db)
    service = UserService(user_repo)
    user = service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = JWTService.create_token(user.id)
    return LoginResponse(access_token=token)

@router.get("/", summary="auth root / health")
async def auth_root():
    return {"message": "Auth router is mounted (use /auth/register for registration)"}

@router.get("/me", response_model=MeResponse)
def me(current_user = Depends(get_current_user)):
    # current_user is domain.entities.user.User
    return MeResponse(id=current_user.id, email=current_user.email, created_at=current_user.created_at.isoformat() if current_user.created_at else None)