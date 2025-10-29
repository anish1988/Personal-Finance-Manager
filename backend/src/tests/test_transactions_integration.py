import sys, os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.db.models import Base, User as UserModel, Transaction
from src.main import app  # adjust import path if necessary
from domain.services.jwt_service import JWTService
from datetime import date

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a fake user in DB and override get_current_user
def create_user_and_token():
    db = TestingSessionLocal()
    u = UserModel(email="txuser@example.com", password_hash="hashed")
    db.add(u)
    db.commit()
    db.refresh(u)
    token = JWTService.create_token(u.id)
    return u, token

u, token = create_user_and_token()

# override dependencies
from api.dependencies import get_db as real_get_db
app.dependency_overrides[real_get_db] = override_get_db

client = TestClient(app)

def test_create_and_list_transaction():
    payload = {
        "tx_date": "2025-10-01",
        "amount": 150.5,
        "currency": "INR",
        "transaction_type": "expense",
        "description": "Grocery store",
        "category_id": None
    }
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post("/transactions", json=payload, headers=headers)
    assert r.status_code == 201
    data = r.json()
    assert data["amount"] == 150.5

    # list
    r2 = client.get("/transactions", headers=headers)
    assert r2.status_code == 200
    arr = r2.json()
    assert len(arr) >= 1
