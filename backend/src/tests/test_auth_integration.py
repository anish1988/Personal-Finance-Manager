# backend/src/tests/test_auth_integration.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app  # your FastAPI app
from api.dependencies import get_db
from infrastructure.db.models import Base  # SQLAlchemy Base for your models

# -----------------------------
# Setup in-memory SQLite DB
# -----------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables for testing
Base.metadata.create_all(bind=engine)

# -----------------------------
# Override get_db dependency
# -----------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# -----------------------------
# TestClient fixture
# -----------------------------
@pytest.fixture(scope="function")
def client():
    yield TestClient(app)
    # Clear DB after each test if needed
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# -----------------------------
# Test cases
# -----------------------------
def test_register_endpoint_success(client):
    payload = {"email": "integ@example.com", "password": "strongpassword"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data

def test_register_endpoint_duplicate(client):
    payload = {"email": "dup@example.com", "password": "strongpassword"}
    # First registration succeeds
    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    # Duplicate registration fails
    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 409
    assert "Email already registered" in r2.json()["detail"]

def test_login_success(client):
    payload = {"email": "login@example.com", "password": "strongpassword"}
    # register first
    client.post("/auth/register", json=payload)

    login_payload = {"email": payload["email"], "password": payload["password"]}
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    payload = {"email": "wrongpass@example.com", "password": "strongpassword"}
    # register first
    client.post("/auth/register", json=payload)

    # wrong password
    login_payload = {"email": payload["email"], "password": "wrongpassword"}
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
