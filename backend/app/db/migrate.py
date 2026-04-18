"""
Migrações leves para bases já existentes (sem Alembic).
Inspeção do schema fora de transações longas para evitar bloqueios (SQLite).
"""
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError


def _add_column(engine: Engine, ddl: str, dialect: str) -> None:
    with engine.begin() as conn:
        try:
            conn.execute(text(ddl))
        except OperationalError as e:
            msg = str(e).lower()
            if dialect == "postgresql":
                if "already exists" not in msg and "duplicate" not in msg:
                    raise
            else:
                if "duplicate column" not in msg:
                    raise


def run_schema_migrations(engine: Engine) -> None:
    dialect = engine.dialect.name
    insp = inspect(engine)
    tables = set(insp.get_table_names())

    if "users" not in tables:
        with engine.begin() as conn:
            if dialect == "postgresql":
                conn.execute(
                    text(
                        """
                        CREATE TABLE users (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            hashed_password VARCHAR(255) NOT NULL,
                            role VARCHAR(32) NOT NULL DEFAULT 'editor',
                            is_active INTEGER NOT NULL DEFAULT 1,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                )
            else:
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            hashed_password VARCHAR(255) NOT NULL,
                            role VARCHAR(32) NOT NULL DEFAULT 'editor',
                            is_active INTEGER NOT NULL DEFAULT 1,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                )

    insp = inspect(engine)
    tables = set(insp.get_table_names())

    if "plan_versions" not in tables and "plans" in tables:
        with engine.begin() as conn:
            if dialect == "postgresql":
                conn.execute(
                    text(
                        """
                        CREATE TABLE plan_versions (
                            id SERIAL PRIMARY KEY,
                            plan_id INTEGER NOT NULL REFERENCES plans(id),
                            snapshot TEXT NOT NULL,
                            label VARCHAR(200),
                            created_by_id INTEGER REFERENCES users(id),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                )
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_plan_versions_plan_id ON plan_versions(plan_id)"))
            else:
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS plan_versions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            plan_id INTEGER NOT NULL,
                            snapshot TEXT NOT NULL,
                            label VARCHAR(200),
                            created_by_id INTEGER,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                )
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_plan_versions_plan_id ON plan_versions(plan_id)"))

    if "plans" not in insp.get_table_names():
        return

    insp = inspect(engine)
    cols = {c["name"] for c in insp.get_columns("plans")}
    if "owner_id" not in cols:
        if dialect == "postgresql":
            _add_column(engine, "ALTER TABLE plans ADD COLUMN owner_id INTEGER", dialect)
        else:
            _add_column(engine, "ALTER TABLE plans ADD COLUMN owner_id INTEGER", dialect)
    if "share_token" not in cols:
        if dialect == "postgresql":
            _add_column(engine, "ALTER TABLE plans ADD COLUMN share_token VARCHAR(64)", dialect)
        else:
            _add_column(engine, "ALTER TABLE plans ADD COLUMN share_token VARCHAR(64)", dialect)
        try:
            with engine.begin() as conn:
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_plans_share_token ON plans(share_token)"))
        except OperationalError:
            pass
