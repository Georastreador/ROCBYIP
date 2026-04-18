"""
Backup e restauração: SQLite (cópia de ficheiro) ou PostgreSQL (pg_dump / pg_restore).

PostgreSQL requer ferramentas cliente no PATH: pg_dump e pg_restore (pacote PostgreSQL).
"""
import os
import shutil
import sqlite3
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKUP_DIR = os.environ.get("BACKUP_DIR", os.path.join(BACKEND_DIR, "backups"))
RETENTION_DAYS = int(os.environ.get("BACKUP_RETENTION_DAYS", "30"))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BACKEND_DIR, "plans.db"))

Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)


def _get_engine() -> Engine:
    from ..db.database import engine

    return engine


def _is_sqlite() -> bool:
    return _get_engine().dialect.name == "sqlite"


def _libpq_database_url() -> str:
    """
    URL no formato aceite por pg_dump/pg_restore (libpq), sem o prefixo +psycopg2.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise ValueError("DATABASE_URL não definido")
    if url.startswith("postgresql+psycopg2://"):
        return "postgresql://" + url[len("postgresql+psycopg2://") :]
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return url
    raise ValueError("DATABASE_URL não é PostgreSQL")


def create_backup(db_path: str = None) -> str:
    """Cria backup. SQLite: cópia .db. PostgreSQL: formato custom .dump via pg_dump."""
    if _is_sqlite():
        return _create_backup_sqlite(db_path)
    return _create_backup_postgres()


def _create_backup_sqlite(db_path: str = None) -> str:
    if db_path is None:
        db_path = DB_PATH

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"plans_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        conn = sqlite3.connect(db_path)
        conn.close()

        shutil.copy2(db_path, backup_path)

        if not verify_backup(backup_path):
            raise ValueError("Falha na verificação de integridade do backup SQLite")

        logger.info(f"Backup SQLite criado: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Erro ao criar backup SQLite: {str(e)}")
        raise


def _create_backup_postgres() -> str:
    dsn = _libpq_database_url()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"plans_backup_{timestamp}.dump"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        result = subprocess.run(
            ["pg_dump", "-Fc", "--no-owner", "--no-acl", "-f", backup_path, dsn],
            capture_output=True,
            text=True,
            timeout=3600,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(f"pg_dump falhou: {err}")

        if not verify_backup(backup_path):
            raise ValueError("Falha na verificação do ficheiro de backup PostgreSQL")

        logger.info(f"Backup PostgreSQL criado: {backup_path}")
        return backup_path
    except FileNotFoundError:
        raise RuntimeError(
            "Comando pg_dump não encontrado. Instale o cliente PostgreSQL "
            "(pg_dump) no servidor ou use backup nativo do fornecedor (ex.: Supabase)."
        ) from None


def verify_backup(backup_path: str) -> bool:
    if backup_path.endswith(".db"):
        return _verify_sqlite_backup(backup_path)
    if backup_path.endswith(".dump"):
        return _verify_postgres_dump(backup_path)
    if backup_path.endswith(".sql"):
        return os.path.isfile(backup_path) and os.path.getsize(backup_path) > 0
    return False


def _verify_sqlite_backup(backup_path: str) -> bool:
    try:
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        if result and result[0] == "ok":
            logger.info(f"Integridade SQLite OK: {backup_path}")
            return True
        logger.error(f"integrity_check falhou: {backup_path}")
        return False
    except Exception as e:
        logger.error(f"Erro ao verificar backup SQLite: {str(e)}")
        return False


def _verify_postgres_dump(backup_path: str) -> bool:
    if not os.path.isfile(backup_path) or os.path.getsize(backup_path) < 64:
        return False
    try:
        r = subprocess.run(
            ["pg_restore", "--list", backup_path],
            capture_output=True,
            timeout=120,
        )
        if r.returncode == 0:
            return True
    except FileNotFoundError:
        logger.warning("pg_restore não encontrado; validação limitada ao tamanho do ficheiro")
    return os.path.getsize(backup_path) > 64


def restore_backup(backup_path: str, target_db_path: str = None) -> bool:
    """Restaura backup. SQLite: copia ficheiro. PostgreSQL: pg_restore (substitui objetos)."""
    if _is_sqlite():
        return _restore_backup_sqlite(backup_path, target_db_path)
    return _restore_backup_postgres(backup_path)


def _restore_backup_sqlite(backup_path: str, target_db_path: str = None) -> bool:
    if target_db_path is None:
        target_db_path = DB_PATH

    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup não encontrado: {backup_path}")

    if not verify_backup(backup_path):
        raise ValueError(f"Backup corrompido ou inválido: {backup_path}")

    try:
        if os.path.exists(target_db_path):
            safety_backup = f"{target_db_path}.safety_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(target_db_path, safety_backup)
            logger.info(f"Backup de segurança antes da restauração: {safety_backup}")

        shutil.copy2(backup_path, target_db_path)

        if verify_backup(target_db_path):
            logger.info(f"SQLite restaurado: {backup_path} -> {target_db_path}")
            return True
        logger.error("Falha no integrity_check após restauração SQLite")
        return False
    except Exception as e:
        logger.error(f"Erro ao restaurar SQLite: {str(e)}")
        raise


def _restore_backup_postgres(backup_path: str) -> bool:
    if not backup_path.endswith(".dump"):
        raise ValueError("Para PostgreSQL, use ficheiro .dump gerado por pg_dump -Fc")

    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup não encontrado: {backup_path}")

    if not verify_backup(backup_path):
        raise ValueError(f"Backup inválido: {backup_path}")

    dsn = _libpq_database_url()

    try:
        result = subprocess.run(
            [
                "pg_restore",
                "--clean",
                "--if-exists",
                "--no-owner",
                "--no-acl",
                "-d",
                dsn,
                backup_path,
            ],
            capture_output=True,
            text=True,
            timeout=3600,
        )
        err_full = ((result.stderr or "") + (result.stdout or "")).strip()
        if result.returncode != 0:
            logger.warning(f"pg_restore exit={result.returncode}: {err_full[:4000]}")
            if result.returncode > 1 or "fatal" in err_full.lower():
                return False
        logger.info(f"PostgreSQL restaurado a partir de: {backup_path}")
        return True
    except FileNotFoundError:
        raise RuntimeError(
            "Comando pg_restore não encontrado. Instale o cliente PostgreSQL."
        ) from None


def cleanup_old_backups(retention_days: int = None) -> int:
    if retention_days is None:
        retention_days = RETENTION_DAYS

    if not os.path.exists(BACKUP_DIR):
        return 0

    cutoff_date = datetime.now() - timedelta(days=retention_days)
    removed_count = 0

    try:
        for filename in os.listdir(BACKUP_DIR):
            if not filename.startswith("plans_backup_"):
                continue
            if not filename.endswith((".db", ".dump", ".sql")):
                continue

            file_path = os.path.join(BACKUP_DIR, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

            if file_time < cutoff_date:
                os.remove(file_path)
                removed_count += 1
                logger.info(f"Backup antigo removido: {filename}")

        logger.info(f"Limpeza concluída: {removed_count} backup(s) removido(s)")
        return removed_count
    except Exception as e:
        logger.error(f"Erro na limpeza de backups: {str(e)}")
        return removed_count


def list_backups() -> list:
    if not os.path.exists(BACKUP_DIR):
        return []

    backups = []
    try:
        for filename in os.listdir(BACKUP_DIR):
            if not filename.startswith("plans_backup_"):
                continue
            if not filename.endswith((".db", ".dump", ".sql")):
                continue

            file_path = os.path.join(BACKUP_DIR, filename)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

            backups.append(
                {
                    "filename": filename,
                    "path": file_path,
                    "size": file_size,
                    "created_at": file_time.isoformat(),
                    "age_days": (datetime.now() - file_time).days,
                }
            )

        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups
    except Exception as e:
        logger.error(f"Erro ao listar backups: {str(e)}")
        return []


def get_backup_stats() -> dict:
    backups = list_backups()

    if not backups:
        return {
            "total_backups": 0,
            "total_size": 0,
            "total_size_mb": 0,
            "oldest_backup": None,
            "newest_backup": None,
            "retention_days": RETENTION_DAYS,
        }

    total_size = sum(b["size"] for b in backups)

    return {
        "total_backups": len(backups),
        "total_size": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "oldest_backup": backups[-1]["created_at"] if backups else None,
        "newest_backup": backups[0]["created_at"] if backups else None,
        "retention_days": RETENTION_DAYS,
    }
