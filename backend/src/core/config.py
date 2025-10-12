import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:user1234@db:5432/finance_db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", 12))

settings = Settings()
