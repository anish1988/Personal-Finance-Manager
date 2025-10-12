from __future__ import with_statement
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ------------------ Set sys.path so we can import models ------------------
# /app is the root of your project in Docker
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src')))
# Add backend/src to sys.path
sys.path.append("/app/backend/src")
# ------------------------------------------------------------------------

# Alembic Config object
config = context.config

# Set up logging from alembic.ini
fileConfig(config.config_file_name)

# Allow DATABASE_URL environment variable to override ini
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# ------------------ Import your SQLAlchemy Base ------------------
from backend.src.infrastructure.db.models import Base  # This path is relative to sys.path above
target_metadata = Base.metadata
# ------------------------------------------------------------------

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with connection.begin():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
