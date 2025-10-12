# backend/src/tests/test_seed_db.py
import os
import sqlalchemy
from sqlalchemy import text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:root12345@localhost:5432/finance_db"
)

def test_categories_seeded():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT count(*) FROM categories"))
        count = res.scalar()
        assert count > 0, "Categories table should have at least one row"
