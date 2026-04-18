from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .db.database import SessionLocal, engine, Base
from .db.migrate import run_schema_migrations
from .models.models import Plan, Evidence, User, PlanVersion
from .schemas.schemas import (
    PlanCreate, PlanUpdate, PlanRead, EvidenceRead, PlanVersionRead,
    TokenOut, UserRead, UserCreate,
)
from .services.audit import log as audit_log
from .services.lgpd import lgpd_check
from .services.pdf import generate_plan_pdf
from .services.error_handler import setup_exception_handlers
from .services.backup import create_backup, restore_backup, list_backups, cleanup_old_backups, get_backup_stats
from .services.field_crypto import decrypt_field, encrypt_field
from .services.auth_jwt import (
    create_access_token, decode_token, hash_password, verify_password,
    JWT_SECRET,
)
from .auth_policy import auth_required_mode
import json, os, hashlib, base64, datetime, sys, re, secrets
from pathlib import Path

# Adicionar diretório raiz ao path para importar security_utils
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from security.security_utils import (
    sanitize_html_text, sanitize_filename, safe_path_join,
    sanitize_log_detail, validate_api_key
)

Base.metadata.create_all(bind=engine)
run_schema_migrations(engine)

app = FastAPI(title="OSINT Planning API v3")

# Configurar exception handlers globais
setup_exception_handlers(app)

# Validação segura de API Key
REQUIRE_API_KEY = os.environ.get("REQUIRE_API_KEY", "false").lower() == "true"
# Padrão false para compatibilidade; use true em produção para proteger backups
REQUIRE_API_KEY_FOR_BACKUP = os.environ.get("REQUIRE_API_KEY_FOR_BACKUP", "false").lower() == "true"
API_KEY = os.environ.get("API_KEY")

# Formato esperado para nome de backup (previne path traversal)
# .db = SQLite | .dump = PostgreSQL (pg_dump -Fc) | .sql = SQL plano (opcional)
BACKUP_FILENAME_PATTERN = re.compile(r"^plans_backup_\d{8}_\d{6}\.(db|dump|sql)$")

# Diretório e retenção de exports (para limpeza automática)
EXPORTS_DIR = os.environ.get("EXPORTS_DIR", "exports")
EXPORTS_RETENTION_HOURS = int(os.environ.get("EXPORTS_RETENTION_HOURS", "24"))  # 24h padrão

# Validar API key se necessário (backup pode exigir mesmo quando geral não exige)
if REQUIRE_API_KEY or REQUIRE_API_KEY_FOR_BACKUP:
    is_valid, error_msg = validate_api_key(API_KEY, require_key=(REQUIRE_API_KEY or REQUIRE_API_KEY_FOR_BACKUP))
    if not is_valid:
        raise ValueError(f"Configuração de segurança inválida: {error_msg}")
elif not API_KEY:
    # Se não requerida e não configurada, usar None (não valor padrão inseguro)
    API_KEY = None
else:
    # Se configurada mas não requerida, validar formato
    is_valid, error_msg = validate_api_key(API_KEY, require_key=False)
    if not is_valid and error_msg:
        import logging
        logging.warning(f"Aviso de segurança: {error_msg}")

# Configuração de Upload
# Tamanho máximo de arquivo (padrão: 50MB)
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB em bytes

# Tipos de arquivo permitidos (extensões)
ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif",  # Documentos e imagens
    ".txt", ".md", ".csv",  # Texto
    ".doc", ".docx", ".xls", ".xlsx",  # Office
    ".zip", ".rar", ".7z",  # Arquivos compactados
    ".json", ".xml",  # Dados estruturados
}

# MIME types permitidos (validação adicional)
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png", "image/jpeg", "image/jpg", "image/gif",
    "text/plain", "text/markdown", "text/csv",
    "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/zip", "application/x-rar-compressed", "application/x-7z-compressed",
    "application/json", "application/xml", "text/xml",
}

# Configuração Rate Limiting
# Permite desabilitar via variável de ambiente RATE_LIMIT_ENABLED=false
RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() == "true"

# Sempre criar o limiter, mas com limites muito altos se desabilitado
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Se desabilitado, definir limites muito altos (efetivamente sem limite)
if not RATE_LIMIT_ENABLED:
    # Override dos limites para valores muito altos quando desabilitado
    # Isso permite que o código funcione sem mudanças, mas sem limitar
    pass  # Os decoradores @limiter.limit() ainda funcionam, mas podem ser ignorados em dev

# Configuração CORS
# Permite configuração via variável de ambiente CORS_ORIGINS
# Formato: "http://localhost:8501,http://localhost:3000,https://exemplo.com"
# Se não definido, usa localhost por padrão (desenvolvimento)
CORS_ORIGINS_ENV = os.environ.get("CORS_ORIGINS", "")
if CORS_ORIGINS_ENV:
    # Split por vírgula e remove espaços
    allowed_origins = [origin.strip() for origin in CORS_ORIGINS_ENV.split(",")]
else:
    # Padrão para desenvolvimento: localhost em portas comuns
    allowed_origins = [
        "http://localhost:8501",  # Streamlit padrão
        "http://localhost:8502",  # Streamlit alternativo
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8502",
        "http://localhost:3000",  # React/Next.js comum
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
    expose_headers=["Content-Disposition"],
)


def _public_paths() -> set[str]:
    p = {"/health", "/auth/token", "/openapi.json"}
    if os.environ.get("ALLOW_REGISTRATION", "").lower() == "true":
        p.add("/auth/register")
    return p


def _is_public_request(path: str) -> bool:
    if path in _public_paths():
        return True
    if path.startswith("/docs") or path.startswith("/redoc"):
        return True
    if path.startswith("/public/plans/by-token/") and os.environ.get("ENABLE_PUBLIC_SHARE", "").lower() == "true":
        return True
    return False


def _bootstrap_initial_admin(db: Session) -> None:
    email = os.environ.get("INITIAL_ADMIN_EMAIL", "").strip()
    password = os.environ.get("INITIAL_ADMIN_PASSWORD", "").strip()
    if not email or not password:
        return
    if db.query(User).count() > 0:
        return
    u = User(
        email=email,
        hashed_password=hash_password(password),
        role="admin",
        is_active=1,
    )
    db.add(u)
    db.commit()


@app.on_event("startup")
def _on_startup_validate_and_bootstrap():
    mode = auth_required_mode()
    if mode in ("jwt", "api_key_or_jwt"):
        if not JWT_SECRET or len(JWT_SECRET) < 16:
            raise RuntimeError(
                "AUTH_REQUIRED exige JWT: defina JWT_SECRET com pelo menos 16 caracteres."
            )
    db = SessionLocal()
    try:
        _bootstrap_initial_admin(db)
    finally:
        db.close()


@app.middleware("http")
async def unified_auth_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization") or ""
    token: str | None = None
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
    payload = decode_token(token) if token else None
    request.state.jwt_payload = payload
    if payload and "sub" in payload:
        try:
            request.state.jwt_user_id = int(payload["sub"])
            request.state.jwt_role = str(payload.get("role", "viewer"))
        except (TypeError, ValueError):
            request.state.jwt_user_id = None
            request.state.jwt_role = None
    else:
        request.state.jwt_user_id = None
        request.state.jwt_role = None

    path = request.url.path
    if _is_public_request(path):
        return await call_next(request)

    # Backups: só protege se REQUIRE_API_KEY ou REQUIRE_API_KEY_FOR_BACKUP (comportamento legado)
    if path.startswith("/backup/"):
        needs_backup_credential = REQUIRE_API_KEY or REQUIRE_API_KEY_FOR_BACKUP
        if not needs_backup_credential:
            return await call_next(request)
        admin_jwt = getattr(request.state, "jwt_role", None) == "admin"
        key_ok = bool(API_KEY) and request.headers.get("X-API-Key") == API_KEY
        if admin_jwt or key_ok:
            return await call_next(request)
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    mode = auth_required_mode()
    api_ok = bool(API_KEY) and request.headers.get("X-API-Key") == API_KEY
    jwt_ok = bool(payload)

    if mode == "none":
        return await call_next(request)
    if mode == "api_key":
        if not API_KEY:
            return JSONResponse({"detail": "API key not configured"}, status_code=500)
        if not api_ok:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)
    if mode == "jwt":
        if not jwt_ok:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)
    if mode == "api_key_or_jwt":
        if not (api_ok or jwt_ok):
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)

    return await call_next(request)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _purpose_plain(plan: Plan) -> str:
    return decrypt_field(plan.purpose)


def _plan_accessible(request: Request, plan: Plan) -> bool:
    if auth_required_mode() in ("none", "api_key"):
        return True
    if not getattr(request.state, "jwt_payload", None):
        return True
    role = getattr(request.state, "jwt_role", None)
    uid = getattr(request.state, "jwt_user_id", None)
    if role == "admin" or uid is None:
        return True
    if plan.owner_id is None:
        return True
    return plan.owner_id == uid


def _plan_writable(request: Request, plan: Plan) -> bool:
    if auth_required_mode() in ("none", "api_key"):
        return True
    if not getattr(request.state, "jwt_payload", None):
        return True
    role = getattr(request.state, "jwt_role", None)
    uid = getattr(request.state, "jwt_user_id", None)
    if role == "admin":
        return True
    if role == "viewer":
        return False
    if plan.owner_id is None:
        return True
    return plan.owner_id == uid


def _plan_list_query(db: Session, request: Request):
    q = db.query(Plan)
    if auth_required_mode() in ("jwt", "api_key_or_jwt") and getattr(request.state, "jwt_payload", None):
        role = getattr(request.state, "jwt_role", None)
        uid = getattr(request.state, "jwt_user_id", None)
        if role != "admin" and uid is not None:
            q = q.filter(or_(Plan.owner_id == uid, Plan.owner_id.is_(None)))
    return q.order_by(Plan.id.desc())


@app.get("/health")
@limiter.limit("100/minute")  # Health check pode ser chamado frequentemente
def health(request: Request):
    return {"status": "ok"}


@app.post("/auth/token", response_model=TokenOut)
@limiter.limit("30/minute")
def auth_token(request: Request, db: Session = Depends(get_db), form: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form.username.strip().lower()).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    tok = create_access_token(user.id, user.role)
    audit_log(db, action="auth_token", detail=f"user={user.id}", plan_id=None, actor=user.email)
    return TokenOut(access_token=tok)


@app.post("/auth/register", response_model=UserRead)
@limiter.limit("10/hour")
def auth_register(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    if os.environ.get("ALLOW_REGISTRATION", "").lower() != "true":
        raise HTTPException(status_code=404, detail="Not found")
    email = payload.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="E-mail já registado")
    u = User(
        email=email,
        hashed_password=hash_password(payload.password),
        role=payload.role if payload.role in ("admin", "editor", "viewer") else "editor",
        is_active=1,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    audit_log(db, action="register", detail=f"user={u.id}", plan_id=None, actor=u.email)
    return UserRead(id=u.id, email=u.email, role=u.role)


@app.get("/auth/me", response_model=UserRead)
@limiter.limit("120/minute")
def auth_me(request: Request, db: Session = Depends(get_db)):
    uid = getattr(request.state, "jwt_user_id", None)
    if uid is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    u = db.get(User, uid)
    if not u or not u.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return UserRead(id=u.id, email=u.email, role=u.role)


def _to_read(plan: Plan, evidences: list[Evidence] | None = None) -> PlanRead:
    return PlanRead(
        id=plan.id,
        title=plan.title,
        subject=json.loads(plan.subject),
        time_window=json.loads(plan.time_window),
        user=json.loads(plan.user),
        purpose=_purpose_plain(plan),
        deadline=json.loads(plan.deadline),
        aspects_essential=json.loads(plan.aspects_essential),
        aspects_known=json.loads(plan.aspects_known),
        aspects_to_know=json.loads(plan.aspects_to_know),
        pirs=json.loads(plan.pirs or "[]"),
        collection=json.loads(plan.collection or "[]"),
        extraordinary=json.loads(plan.extraordinary or "[]"),
        security=json.loads(plan.security or "[]"),
        evidences=[EvidenceRead(id=e.id, filename=e.filename, sha256=e.sha256, size=e.size) for e in (evidences or [])],
        owner_id=getattr(plan, "owner_id", None),
    )

def _to_dict(plan: Plan) -> dict:
    return _to_read(plan).model_dump()

@app.post("/plans", response_model=PlanRead)
@limiter.limit("20/minute")  # Limite de criação de planos
def create_plan(request: Request, payload: PlanCreate, db: Session = Depends(get_db)):
    if getattr(request.state, "jwt_role", None) == "viewer":
        raise HTTPException(403, "Perfil leitor não pode criar planos")
    owner_id = getattr(request.state, "jwt_user_id", None)
    plan = Plan(
        title=payload.title,
        subject=json.dumps(payload.subject.model_dump(), ensure_ascii=False),
        time_window=json.dumps(payload.time_window.model_dump(), ensure_ascii=False),
        user=json.dumps(payload.user.model_dump(), ensure_ascii=False),
        purpose=encrypt_field(payload.purpose),
        deadline=json.dumps(payload.deadline.model_dump(), ensure_ascii=False),
        aspects_essential=json.dumps(payload.aspects_essential, ensure_ascii=False),
        aspects_known=json.dumps(payload.aspects_known, ensure_ascii=False),
        aspects_to_know=json.dumps(payload.aspects_to_know, ensure_ascii=False),
        pirs=json.dumps([p.model_dump() for p in payload.pirs], ensure_ascii=False),
        collection=json.dumps([c.model_dump() for c in payload.collection], ensure_ascii=False),
        extraordinary=json.dumps(payload.extraordinary, ensure_ascii=False),
        security=json.dumps(payload.security, ensure_ascii=False),
        owner_id=owner_id,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    safe_detail = sanitize_log_detail(f"Plan {plan.id} created")
    audit_log(db, action="create_plan", detail=safe_detail, plan_id=plan.id)
    return _to_read(plan, evidences=[])

@app.get("/plans/{plan_id}", response_model=PlanRead)
@limiter.limit("60/minute")  # Leitura pode ser mais frequente
def get_plan(request: Request, plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    if not _plan_accessible(request, plan):
        raise HTTPException(404, "Plan not found")
    evs = db.query(Evidence).filter(Evidence.plan_id==plan.id).all()
    return _to_read(plan, evidences=evs)


@app.put("/plans/{plan_id}", response_model=PlanRead)
@limiter.limit("20/minute")
def update_plan(request: Request, plan_id: int, payload: PlanUpdate, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    if not _plan_accessible(request, plan) or not _plan_writable(request, plan):
        raise HTTPException(404, "Plan not found")

    snapshot = json.dumps(_to_dict(plan), ensure_ascii=False)
    uid = getattr(request.state, "jwt_user_id", None)
    pv = PlanVersion(
        plan_id=plan.id,
        snapshot=snapshot,
        label=payload.version_label,
        created_by_id=uid,
    )
    db.add(pv)

    plan.title = payload.title
    plan.subject = json.dumps(payload.subject.model_dump(), ensure_ascii=False)
    plan.time_window = json.dumps(payload.time_window.model_dump(), ensure_ascii=False)
    plan.user = json.dumps(payload.user.model_dump(), ensure_ascii=False)
    plan.purpose = encrypt_field(payload.purpose)
    plan.deadline = json.dumps(payload.deadline.model_dump(), ensure_ascii=False)
    plan.aspects_essential = json.dumps(payload.aspects_essential, ensure_ascii=False)
    plan.aspects_known = json.dumps(payload.aspects_known, ensure_ascii=False)
    plan.aspects_to_know = json.dumps(payload.aspects_to_know, ensure_ascii=False)
    plan.pirs = json.dumps([p.model_dump() for p in payload.pirs], ensure_ascii=False)
    plan.collection = json.dumps([c.model_dump() for c in payload.collection], ensure_ascii=False)
    plan.extraordinary = json.dumps(payload.extraordinary, ensure_ascii=False)
    plan.security = json.dumps(payload.security, ensure_ascii=False)

    db.commit()
    db.refresh(plan)
    safe_detail = sanitize_log_detail(f"Plan {plan.id} updated (version journal)")
    audit_log(db, action="update_plan", detail=safe_detail, plan_id=plan.id)
    evs = db.query(Evidence).filter(Evidence.plan_id==plan.id).all()
    return _to_read(plan, evidences=evs)


@app.get("/plans/{plan_id}/versions", response_model=list[PlanVersionRead])
@limiter.limit("60/minute")
def list_plan_versions(request: Request, plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    if not _plan_accessible(request, plan):
        raise HTTPException(404, "Plan not found")
    rows = db.query(PlanVersion).filter(PlanVersion.plan_id == plan_id).order_by(PlanVersion.id.desc()).all()
    out = []
    for r in rows:
        ts = r.created_at.isoformat() if r.created_at else None
        out.append(
            PlanVersionRead(
                id=r.id, plan_id=r.plan_id, label=r.label, created_at=ts, created_by_id=r.created_by_id
            )
        )
    return out


@app.post("/plans/{plan_id}/share", response_model=dict)
@limiter.limit("10/minute")
def create_share_token(request: Request, plan_id: int, db: Session = Depends(get_db)):
    if os.environ.get("ENABLE_PUBLIC_SHARE", "").lower() != "true":
        raise HTTPException(404, "Not found")
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    if not _plan_writable(request, plan):
        raise HTTPException(403, "Forbidden")
    tok = secrets.token_urlsafe(24)
    plan.share_token = tok
    db.commit()
    return {"token": tok, "hint": "GET /public/plans/by-token/{token}"}


@app.get("/public/plans/by-token/{token}", response_model=PlanRead)
@limiter.limit("60/minute")
def get_plan_by_share_token(request: Request, token: str, db: Session = Depends(get_db)):
    if os.environ.get("ENABLE_PUBLIC_SHARE", "").lower() != "true":
        raise HTTPException(404, "Not found")
    plan = db.query(Plan).filter(Plan.share_token == token).first()
    if not plan:
        raise HTTPException(404, "Plan not found")
    evs = db.query(Evidence).filter(Evidence.plan_id==plan.id).all()
    return _to_read(plan, evidences=evs)


@app.get("/plans", response_model=list[PlanRead])
@limiter.limit("30/minute")  # Listagem pode ser moderada
def list_plans(request: Request, db: Session = Depends(get_db)):
    plans = _plan_list_query(db, request).all()
    result = []
    for p in plans:
        evs = db.query(Evidence).filter(Evidence.plan_id==p.id).all()
        result.append(_to_read(p, evidences=evs))
    return result

@app.post("/plans/{plan_id}/lgpd_check")
@limiter.limit("30/minute")  # Validação LGPD moderada
def check_lgpd(request: Request, plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    if not _plan_accessible(request, plan):
        raise HTTPException(404, "Plan not found")
    data = _to_dict(plan)
    result = lgpd_check(data)
    safe_detail = sanitize_log_detail(str(result))
    audit_log(db, action="lgpd_check", detail=safe_detail, plan_id=plan.id)
    return result

@app.get("/export/pdf/{plan_id}")
@limiter.limit("10/minute")  # Geração de PDF é mais pesada
def export_pdf(request: Request, plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    if not _plan_accessible(request, plan):
        raise HTTPException(404, "Plan not found")
    data = _to_dict(plan)
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    outfile = os.path.join(EXPORTS_DIR, f"plan_{plan.id}.pdf")
    _cleanup_old_exports()
    generate_plan_pdf(data, outfile)
    safe_detail = sanitize_log_detail(outfile)
    audit_log(db, action="export_pdf", detail=safe_detail, plan_id=plan.id)
    return FileResponse(outfile, media_type="application/pdf", filename=f"plan_{plan.id}.pdf")

@app.get("/export/html/{plan_id}")
@limiter.limit("20/minute")  # HTML é mais leve que PDF
def export_html(request: Request, plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    if not _plan_accessible(request, plan):
        raise HTTPException(404, "Plan not found")
    data = _to_dict(plan)
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    outfile = os.path.join(EXPORTS_DIR, f"plan_{plan.id}.html")
    _cleanup_old_exports()
    logo_path = os.environ.get("REPORT_LOGO_PATH")
    logo_html = ""
    if logo_path and os.path.exists(logo_path):
        # Usar context manager para abrir arquivo
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_html = f'<img src="data:image/png;base64,{b64}" style="height:60px;"/>'
    
    # Sanitizar todos os dados antes de inserir no HTML
    safe_title = sanitize_html_text(data.get('title', ''))
    safe_subject_what = sanitize_html_text(data.get('subject', {}).get('what', ''))
    safe_subject_who = sanitize_html_text(data.get('subject', {}).get('who', ''))
    safe_subject_where = sanitize_html_text(data.get('subject', {}).get('where', ''))
    safe_time_start = sanitize_html_text(data.get('time_window', {}).get('start', ''))
    safe_time_end = sanitize_html_text(data.get('time_window', {}).get('end', ''))
    safe_time_notes = sanitize_html_text(data.get('time_window', {}).get('research_notes', ''))
    safe_user_principal = sanitize_html_text(data.get('user', {}).get('principal', ''))
    safe_user_others = sanitize_html_text(data.get('user', {}).get('others', ''))
    safe_user_depth = sanitize_html_text(data.get('user', {}).get('depth', ''))
    safe_user_secrecy = sanitize_html_text(data.get('user', {}).get('secrecy', ''))
    safe_purpose = sanitize_html_text(data.get('purpose', ''))
    safe_deadline_date = sanitize_html_text(data.get('deadline', {}).get('date', ''))
    safe_deadline_urgency = sanitize_html_text(data.get('deadline', {}).get('urgency', ''))
    
    # Sanitizar arrays
    safe_aspects_essential = [sanitize_html_text(x) for x in data.get("aspects_essential", [])]
    safe_aspects_known = [sanitize_html_text(x) for x in data.get("aspects_known", [])]
    safe_aspects_to_know = [sanitize_html_text(x) for x in data.get("aspects_to_know", [])]
    safe_extraordinary = [sanitize_html_text(x) for x in data.get("extraordinary", [])]
    safe_security = [sanitize_html_text(x) for x in data.get("security", [])]
    
    # Sanitizar PIRs e Collection
    safe_pirs = []
    for p in data.get('pirs', []):
        safe_pirs.append({
            'aspect_ref': sanitize_html_text(p.get('aspect_ref', '-')),
            'question': sanitize_html_text(p.get('question', '')),
            'priority': sanitize_html_text(p.get('priority', ''))
        })
    
    safe_collection = []
    for t in data.get('collection', []):
        safe_collection.append({
            'pir_index': sanitize_html_text(str(t.get('pir_index', ''))),
            'source': sanitize_html_text(t.get('source', '')),
            'method': sanitize_html_text(t.get('method', '')),
            'frequency': sanitize_html_text(t.get('frequency', '')),
            'owner': sanitize_html_text(t.get('owner', '')),
            'sla_hours': sanitize_html_text(str(t.get('sla_hours', 0)))
        })
    
    html = f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8"/>
<title>Plano de Inteligência — {safe_title}</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;margin:24px;color:#0f172a;}}
header{{display:flex;align-items:center;gap:16px;border-bottom:2px solid #e2e8f0;padding-bottom:8px;margin-bottom:16px;}}
h1{{font-size:20px;margin:0;}}
.section{{margin:16px 0;}}
.card{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;margin:8px 0;}}
.table{{width:100%;border-collapse:collapse;font-size:14px;}}
.table th,.table td{{border:1px solid #e2e8f0;padding:8px;text-align:left;}}
.mono{{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;font-size:12px;}}
</style>
</head>
<body>
<header>
{logo_html}
<div>
<h1>Plano de Inteligência — 1ª Fase (Planejamento)</h1>
<div class="mono">{datetime.datetime.utcnow().isoformat()}Z</div>
</div>
</header>

<div class="section">
  <div class="card"><b>Título:</b> {safe_title}</div>
  <div class="card">
    <b>Assunto:</b><br/>
    O quê: <strong>{safe_subject_what}</strong><br/>
    Quem: <strong>{safe_subject_who}</strong><br/>
    Onde: <strong>{safe_subject_where}</strong>
  </div>
  <div class="card">
    <b>Faixa de Tempo (Pesquisa):</b><br/>
    Início: <strong>{safe_time_start}</strong><br/>
    Fim: <strong>{safe_time_end}</strong><br/>
    Notas: {safe_time_notes or '<em>(nenhuma anotação)</em>'}
  </div>
  <div class="card">
    <b>Usuário:</b><br/>
    Principal: <strong>{safe_user_principal}</strong><br/>
    Outros: {safe_user_others or '<em>(nenhum)</em>'}<br/>
    Profundidade: <strong>{safe_user_depth}</strong><br/>
    Sigilo: <strong>{safe_user_secrecy}</strong>
  </div>
  <div class="card"><b>Finalidade:</b> {safe_purpose}</div>
  <div class="card">
    <b>Prazo:</b><br/>
    Data Limite: <strong>{safe_deadline_date}</strong><br/>
    Urgência: <strong>{safe_deadline_urgency}</strong>
  </div>
</div>

<div class="section">
  <h3>Aspectos</h3>
  <div class="card"><b>Essenciais</b><br/>{"<br/>".join([f"• {x}" for x in safe_aspects_essential]) or "-"}</div>
  <div class="card"><b>Conhecidos</b><br/>{"<br/>".join([f"• {x}" for x in safe_aspects_known]) or "-"}</div>
  <div class="card"><b>A Conhecer</b><br/>{"<br/>".join([f"• {x}" for x in safe_aspects_to_know]) or "-"}</div>
</div>

<div class="section">
  <h3>PIRs</h3>
  <table class="table">
    <thead><tr><th>#</th><th>Aspecto Ref</th><th>Pergunta</th><th>Prioridade</th></tr></thead>
    <tbody>
    { "".join([f"<tr><td>{i}</td><td>{p['aspect_ref']}</td><td>{p['question']}</td><td>{p['priority']}</td></tr>" for i,p in enumerate(safe_pirs)]) or "<tr><td colspan='4'>-</td></tr>" }
    </tbody>
  </table>
</div>

<div class="section">
  <h3>Plano de Coleta</h3>
  <table class="table">
    <thead><tr><th>PIR #</th><th>Fonte</th><th>Método</th><th>Freq.</th><th>Owner</th><th>SLA (h)</th></tr></thead>
    <tbody>
    { "".join([f"<tr><td>{t['pir_index']}</td><td>{t['source']}</td><td>{t['method']}</td><td>{t['frequency']}</td><td>{t['owner']}</td><td>{t['sla_hours']}</td></tr>" for t in safe_collection]) or "<tr><td colspan='6'>-</td></tr>" }
    </tbody>
  </table>
</div>

<div class="section">
  <h3>Medidas</h3>
  <div class="card"><b>Extraordinárias</b><br/>{"<br/>".join([f"• {x}" for x in safe_extraordinary]) or "-"}</div>
  <div class="card"><b>Segurança</b><br/>{"<br/>".join([f"• {x}" for x in safe_security]) or "-"}</div>
</div>

</body>
</html>"""
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(html)
    safe_detail = sanitize_log_detail(outfile)
    audit_log(db, action="export_html", detail=safe_detail, plan_id=plan.id)
    return FileResponse(outfile, media_type="text/html", filename=f"plan_{plan.id}.html")

@app.post("/evidence/upload", response_model=EvidenceRead)
@limiter.limit("5/minute")  # Upload é mais restritivo (arquivos grandes)
async def upload_evidence(request: Request, plan_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if not _plan_accessible(request, plan) or not _plan_writable(request, plan):
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Validação de nome de arquivo
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Validação de extensão
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    
    # Validação de MIME type (se disponível)
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File MIME type not allowed: {file.content_type}"
        )
    
    # Ler arquivo em chunks para validar tamanho antes de carregar tudo na memória
    os.makedirs("uploads", exist_ok=True)
    content = b""
    chunk_size = 1024 * 1024  # 1MB por chunk
    
    try:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            
            # Verificar tamanho acumulado
            if len(content) + len(chunk) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.0f}MB"
                )
            
            content += chunk
        
        # Verificar tamanho final
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.0f}MB"
            )
        
        # Calcular hash SHA-256
        sha256 = hashlib.sha256(content).hexdigest()
        
        # Salvar arquivo
        # Sanitizar nome do arquivo para evitar path traversal
        safe_filename = sanitize_filename(file.filename)
        # Usar safe_path_join para garantir segurança
        try:
            path = safe_path_join("uploads", safe_filename)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Nome de arquivo inválido: {str(e)}"
            )
        
        # Se arquivo já existe com mesmo hash, não duplicar
        if os.path.exists(path):
            # Usar context manager para abrir arquivo
            with open(path, "rb") as f:
                existing_hash = hashlib.sha256(f.read()).hexdigest()
            if existing_hash == sha256:
                # Arquivo já existe, apenas criar referência no banco
                pass
            else:
                # Nome igual mas conteúdo diferente, adicionar sufixo
                base_name, ext = os.path.splitext(safe_filename)
                counter = 1
                while os.path.exists(path):
                    safe_filename = sanitize_filename(f"{base_name}_{counter}{ext}")
                    try:
                        path = safe_path_join("uploads", safe_filename)
                    except ValueError:
                        # Se ainda houver problema, usar hash como nome
                        safe_filename = f"file_{sha256[:16]}{ext}"
                        path = safe_path_join("uploads", safe_filename)
                        break
                    counter += 1
                    if counter > 1000:  # Limite de segurança
                        raise HTTPException(
                            status_code=500,
                            detail="Muitas tentativas de renomear arquivo"
                        )
        
        with open(path, "wb") as f:
            f.write(content)
        
        # Criar registro no banco
        ev = Evidence(plan_id=plan.id, filename=safe_filename, sha256=sha256, size=len(content))
        db.add(ev)
        db.commit()
        db.refresh(ev)
        safe_detail = sanitize_log_detail(f"{safe_filename} {sha256[:16]}... ({len(content)} bytes)")
        audit_log(db, action="upload_evidence", detail=safe_detail, plan_id=plan.id)
        
        return EvidenceRead(id=ev.id, filename=ev.filename, sha256=ev.sha256, size=ev.size)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log erro e retornar mensagem genérica (sanitizar detalhes)
        safe_filename_log = sanitize_filename(file.filename) if file.filename else "unknown"
        safe_detail = sanitize_log_detail(f"Error uploading {safe_filename_log}")
        audit_log(db, action="upload_error", detail=safe_detail, plan_id=plan.id)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while uploading the file. Please try again."
        )

def _cleanup_old_exports():
    """Remove exports antigos conforme política de retenção (previne preenchimento do disco)"""
    try:
        if not os.path.exists(EXPORTS_DIR):
            return
        cutoff = datetime.datetime.now() - datetime.timedelta(hours=EXPORTS_RETENTION_HOURS)
        for name in os.listdir(EXPORTS_DIR):
            path = os.path.join(EXPORTS_DIR, name)
            if os.path.isfile(path):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                if mtime < cutoff:
                    os.remove(path)
    except Exception:
        pass  # Não falhar export por erro na limpeza

# Endpoints de Backup e Recuperação
@app.post("/backup/create")
@limiter.limit("5/minute")
def create_backup_endpoint(request: Request, db: Session = Depends(get_db)):
    """Cria um backup do banco de dados"""
    try:
        backup_path = create_backup()
        audit_log(db, action="backup_create", detail=f"Backup created: {backup_path}")
        
        # Limpar backups antigos após criar novo
        cleanup_old_backups()
        
        return {
            "status": "success",
            "message": "Backup created successfully",
            "backup_path": backup_path,
            "created_at": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        audit_log(db, action="backup_error", detail=f"Error creating backup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating backup: {str(e)}")


@app.get("/backup/list")
@limiter.limit("30/minute")
def list_backups_endpoint(request: Request, db: Session = Depends(get_db)):
    """Lista todos os backups disponíveis"""
    try:
        backups = list_backups()
        stats = get_backup_stats()
        audit_log(db, action="backup_list", detail=f"Listed {len(backups)} backups")
        
        return {
            "backups": backups,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing backups: {str(e)}")


@app.post("/backup/restore/{backup_filename}")
@limiter.limit("3/minute")
def restore_backup_endpoint(request: Request, backup_filename: str, db: Session = Depends(get_db)):
    """Restaura um backup específico"""
    # Validação estrita do nome para prevenir path traversal
    if not BACKUP_FILENAME_PATTERN.match(backup_filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid backup filename. Expected: plans_backup_YYYYMMDD_HHMMSS.db|.dump|.sql",
        )

    try:
        from .services.backup import BACKUP_DIR
        backup_path = safe_path_join(BACKUP_DIR, backup_filename)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        success = restore_backup(backup_path)
        
        if success:
            audit_log(db, action="backup_restore", detail=f"Backup restored: {backup_filename}")
            return {
                "status": "success",
                "message": "Backup restored successfully",
                "backup_file": backup_filename,
                "restored_at": datetime.datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to restore backup")
    
    except HTTPException:
        raise
    except Exception as e:
        audit_log(db, action="backup_restore_error", detail=f"Error restoring backup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error restoring backup: {str(e)}")


@app.get("/backup/stats")
@limiter.limit("60/minute")
def backup_stats_endpoint(request: Request, db: Session = Depends(get_db)):
    """Retorna estatísticas dos backups"""
    try:
        stats = get_backup_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting backup stats: {str(e)}")
