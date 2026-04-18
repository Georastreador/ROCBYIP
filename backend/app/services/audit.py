from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
from pathlib import Path

# Adicionar diretório raiz ao path para importar security_utils
current_dir = Path(__file__).parent
# Caminho: backend/app/services/audit.py -> raiz do projeto
root_dir = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from security.security_utils import sanitize_log_detail, sanitize_text


def _ensure_audit_table(db: Session) -> None:
    dialect = db.get_bind().dialect.name
    if dialect == "postgresql":
        ddl = """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            plan_id INTEGER,
            action TEXT,
            detail TEXT,
            actor TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """
    else:
        ddl = """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            action TEXT,
            detail TEXT,
            actor TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    db.execute(text(ddl))


def log(db: Session, action: str, detail: str = "", plan_id: int | None = None, actor: str = "analyst"):
    # Sanitizar inputs antes de inserir no banco
    safe_action = sanitize_text(action, max_length=100)
    safe_detail = sanitize_log_detail(detail)
    safe_actor = sanitize_text(actor, max_length=100)

    _ensure_audit_table(db)
    db.execute(
        text(
            "INSERT INTO audit_logs (plan_id, action, detail, actor) VALUES (:pid,:a,:d,:actor)"
        ),
        {"pid": plan_id, "a": safe_action, "d": safe_detail, "actor": safe_actor},
    )
    db.commit()
