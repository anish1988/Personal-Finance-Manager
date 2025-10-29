# backend/src/tests/test_me_integration.py
import sys, os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.db.models import Base
from src.main import app  # or adjust import path to your main app
from domain.services.jwt_service import JWTService
from infrastructure.db.models import User as UserModel

# in-memory sqlite
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides = getattr(app, "dependency_overrides", {})
from api.dependencies import get_db as real_get_db  # to ensure name exists
app.dependency_overrides[real_get_db] = override_get_db

client = TestClient(app)

def create_user_in_db(db, email, password_hash):
    u = UserModel(email=email, password_hash=password_hash)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def test_me_endpoint():
    db = TestingSessionLocal()
    u = create_user_in_db(db, "me@example.com", "hashed_dummy")
    token = JWTService.create_token(u.id)
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@example.com"

def test_me_invalid_token():
    resp = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401
