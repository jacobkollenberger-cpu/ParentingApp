"""
Alembic environment configuration.

This wires Alembic up to:
1. The app's real DATABASE_URL (from .env via app.core.config)
2. The SQLAlchemy models, so `alembic revision --autogenerate` can
   detect schema changes automatically instead of writing migrations by hand.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.session import Base

# Import all models here so Base.metadata knows about them.
# Add new model modules to this list as you create them.
from app.models import user, child, audit_log  # noqa: F401

config = context.config

# Override the sqlalchemy.url from alembic.ini with our real one from .env
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
