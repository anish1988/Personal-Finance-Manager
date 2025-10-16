import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:root12345@db:5432/finance_db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", 12))

settings = Settings()
