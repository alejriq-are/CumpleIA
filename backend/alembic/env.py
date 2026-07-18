import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

import app.db.models  # noqa: F401 — registra los modelos en Base.metadata
from alembic import context
from app.core.config import get_settings
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
settings = get_settings()

# URL síncrona para migraciones (psycopg2); asyncpg es para la app en runtime
_sync_url = settings.database_url.replace("+asyncpg", "")
# En entorno de test mostramos el SQL ejecutado para facilitar el diagnóstico
_echo_sql = os.environ.get("ENVIRONMENT") == "test"


def run_migrations_offline() -> None:
    context.configure(
        url=_sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(_sync_url, poolclass=pool.NullPool, echo=_echo_sql)
    with connectable.connect() as connection:
        do_run_migrations(connection)
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
