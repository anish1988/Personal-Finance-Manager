# backend/src/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# IMPORTANT: Don't import the FastAPI app at top-level here.
# We will import it after creating the DB/tables to avoid race conditions.

# Import application DB models Base (adjust path to match your project)
from infrastructure.db.models import Base

# Use an in-memory SQLite that is shared between connections via StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables once before any tests run (session-scoped)
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # ensure models are registered
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# DB session fixture per test
@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# Create TestClient only after DB is ready and override get_db
@pytest.fixture()
def client(db_session):
    # Import app and the real dependency inside the fixture (after tables exist)
    from main import app  # import app from backend/src/main.py
    from api.dependencies import get_db as real_get_db

    # override dependency so endpoints use the test session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[real_get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # cleanup override
    app.dependency_overrides.pop(real_get_db, None)
