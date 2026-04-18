"""
Configuração SQLAlchemy: PostgreSQL (produção) ou SQLite (desenvolvimento local).

Produção (Supabase, Railway, etc.):
  export DATABASE_URL="postgresql://user:pass@host:5432/dbname?sslmode=require"

Nota: o pooler de transações do Supabase (porta 6543) pode não funcionar com pg_dump;
use a URL direta à instância (porta 5432) nos scripts de backup, se necessário.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def _normalize_postgres_url(url: str) -> str:
    """Converte postgres:// ou postgresql:// para o driver SQLAlchemy psycopg2."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return "postgresql+psycopg2://" + url[len("postgresql://") :]
    return url


def _build_engine():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        url = "sqlite:///./plans.db"

    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
        )

    url = _normalize_postgres_url(url)
    pool_size = int(os.environ.get("DB_POOL_SIZE", "5"))
    max_overflow = int(os.environ.get("DB_MAX_OVERFLOW", "10"))
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
    )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
