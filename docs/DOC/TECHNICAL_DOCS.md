# 🔧 Documentação Técnica — ROC Planejamento de Inteligência

**Última atualização:** 11 de Novembro de 2025

---

## 📑 Índice

1. [Stack Tecnológico](#stack-tecnológico)
2. [Instalação Detalhada](#instalação-detalhada)
3. [Configuração](#configuração)
4. [API REST — Referência Completa](#api-rest--referência-completa)
5. [Estrutura de Código](#estrutura-de-código)
6. [Boas Práticas](#boas-práticas)
7. [Troubleshooting](#troubleshooting)

---

## Stack Tecnológico

### Frontend
- **Streamlit 1.39.0:** Framework web interativo com estado reativo
- **httpx 0.27.2:** Cliente HTTP assíncrono
- **pandas:** Manipulação de DataFrames (Gantt chart)

### Backend
- **FastAPI 0.115.0:** Framework REST moderno com validação automática
- **Uvicorn 0.30.6:** Servidor ASGI de alta performance
- **Pydantic 2.9.2:** Validação de dados e serialização
- **SQLAlchemy 2.0.35:** ORM para acesso ao banco

### Persistência
- **SQLite:** Banco de dados embarcado (dev/MVP)

### Utilidades
- **ReportLab 4.2.5:** Geração de PDF programático
- **python-multipart 0.0.12:** Parsing de multipart/form-data

### Testing
- **pytest:** Framework de testes

---

## Instalação Detalhada

### Pré-requisitos
```bash
python --version  # 3.10+
pip --version     # 20.0+
```

### Passo 1: Clonar Repositório
```bash
cd /Users/rikardocroce/Library/CloudStorage/OneDrive-Personal/# ROC project Dsvn/BYIP/intel_planning_osint_mvp_v3
```

### Passo 2: Criar Virtual Environment
```bash
# macOS/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Passo 3: Instalar Dependências Backend
```bash
cd backend
pip install -r requirements.txt
```

Verificar:
```bash
pip list | grep -E "fastapi|sqlalchemy|pydantic"
```

### Passo 4: Instalar Dependências Frontend
```bash
cd ../app
pip install -r requirements.txt
```

Verificar:
```bash
pip list | grep -E "streamlit|httpx|pandas"
```

### Passo 5: Verificar Instalação
```bash
# Backend
python -c "import fastapi; print(fastapi.__version__)"

# Frontend
python -c "import streamlit; print(streamlit.__version__)"
```

---

## Configuração

### Variáveis de Ambiente

#### Backend (`.env` ou `export`)

```bash
# Segurança
REQUIRE_API_KEY=false
API_KEY=sua_chave_secreta_aqui

# Relatórios
REPORT_LOGO_PATH=/caminho/para/logo.png

# Banco de Dados (futuro)
DATABASE_URL=sqlite:///./test.db

# Debug
DEBUG=false
LOG_LEVEL=INFO
```

#### Frontend (`.streamlit/config.toml`)

```toml
[server]
port = 8501
headless = true
runOnSave = true

[client]
toolbarMode = "minimal"

[logger]
level = "info"
```

### Estrutura de Diretórios

```
project/
├── backend/
│   ├── app.db              # Banco SQLite (criado automaticamente)
│   ├── exports/            # PDFs gerados
│   ├── uploads/            # Arquivos de evidência
│   └── app/
│       ├── __pycache__/
│       ├── db/
│       │   └── database.py
│       ├── models/
│       │   └── models.py
│       ├── schemas/
│       │   └── schemas.py
│       ├── services/
│       │   ├── audit.py
│       │   ├── lgpd.py
│       │   └── pdf.py
│       └── main.py
├── app/
│   └── streamlit_app.py
├── tests/
│   ├── test_api.py
│   └── __init__.py
├── README.md
└── SYSTEM_REPORT.md
```

---

## API REST — Referência Completa

### Base URL
```
http://localhost:8000
```

### Headers Obrigatórios (se API Key ativada)
```http
X-API-Key: sua_chave_aqui
Content-Type: application/json
```

### 1. Health Check

**GET `/health`**

```bash
curl http://localhost:8000/health
```

**Response (200):**
```json
{"status": "ok"}
```

---

### 2. Criar Plano

**POST `/plans`**

**Request Body:**
```json
{
  "title": "Planejamento de Inteligência",
  "subject": {
    "what": "O quê?",
    "who": "Quem?",
    "where": "Onde?"
  },
  "time_window": {
    "start": "2025-11-01",
    "end": "2025-11-30"
  },
  "user": {
    "principal": "João Silva",
    "others": "Equipe X",
    "depth": "executivo",
    "secrecy": "publico"
  },
  "purpose": "Objetivo do conhecimento",
  "deadline": {
    "date": "2025-11-30",
    "urgency": "media"
  },
  "aspects_essential": ["Aspecto 1", "Aspecto 2"],
  "aspects_known": ["Conhecido 1"],
  "aspects_to_know": ["A conhecer 1"],
  "pirs": [
    {
      "aspect_ref": 0,
      "question": "Pergunta?",
      "priority": "alta",
      "justification": "Por quê?"
    }
  ],
  "collection": [
    {
      "pir_index": 0,
      "source": "Google",
      "method": "Busca",
      "frequency": "unico",
      "owner": "Analista",
      "sla_hours": 24
    }
  ],
  "extraordinary": ["Medida 1"],
  "security": ["Segurança 1"]
}
```

**Response (200):**
```json
{
  "id": 1,
  "title": "Planejamento de Inteligência",
  "subject": {...},
  "...": "...",
  "evidences": []
}
```

---

### 3. Listar Planos

**GET `/plans`**

```bash
curl http://localhost:8000/plans
```

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "...",
    "...": "..."
  },
  {
    "id": 2,
    "...": "..."
  }
]
```

---

### 4. Obter Plano Específico

**GET `/plans/{plan_id}`**

```bash
curl http://localhost:8000/plans/1
```

**Response (200):**
```json
{
  "id": 1,
  "title": "...",
  "evidences": [
    {
      "id": 1,
      "filename": "arquivo.pdf",
      "sha256": "abc123...",
      "size": 256000
    }
  ]
}
```

**Response (404):**
```json
{"detail": "Plan not found"}
```

---

### 5. Validar LGPD

**POST `/plans/{plan_id}/lgpd_check`**

```bash
curl -X POST http://localhost:8000/plans/1/lgpd_check
```

**Response (200):**
```json
{
  "ok": true,
  "issues": []
}
```

**Response (200) — Com problemas:**
```json
{
  "ok": false,
  "issues": [
    "Plano com sigilo elevado requer medidas de segurança definidas.",
    "Faixa de tempo inválida: início posterior ao fim."
  ]
}
```

---

### 6. Exportar PDF

**GET `/export/pdf/{plan_id}`**

```bash
curl http://localhost:8000/export/pdf/1 > plan.pdf
```

**Response (200):**
```json
{
  "file": "exports/plan_1.pdf"
}
```

**Arquivo gerado:** `backend/exports/plan_1.pdf`

---

### 7. Exportar HTML

**GET `/export/html/{plan_id}`**

```bash
curl http://localhost:8000/export/html/1 > plan.html
```

**Response (200):**
```json
{
  "file": "exports/plan_1.html"
}
```

**Arquivo gerado:** `backend/exports/plan_1.html`

---

### 8. Upload de Evidência

**POST `/evidence/upload`** (multipart/form-data)

```bash
curl -X POST \
  -F "file=@/caminho/para/arquivo.pdf" \
  -F "plan_id=1" \
  http://localhost:8000/evidence/upload
```

**Response (200):**
```json
{
  "id": 1,
  "filename": "arquivo.pdf",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "size": 1024
}
```

---

## Estrutura de Código

### Fluxo Frontend → Backend

```
streamlit_app.py (279 linhas)
│
├─ Session state initialization
│  └─ plan = {title, subject, time_window, ...}
│
├─ Sidebar navigation (13 steps)
│
├─ Step handlers
│  ├─ if current == "Assunto": → input subject
│  ├─ if current == "Faixa de Tempo": → input time_window
│  ├─ ...
│  └─ if current == "Revisão & Export":
│     └─ Buttons: save, lgpd_check, export_pdf, export_html, upload
│
└─ httpx.Client calls
   └─ POST /plans
   └─ POST /plans/{id}/lgpd_check
   └─ GET /export/pdf/{id}
   └─ GET /export/html/{id}
   └─ POST /evidence/upload
```

### Fluxo Backend (FastAPI)

```
main.py (226 linhas)
│
├─ Middleware (API Key guard)
│
├─ Models (SQLAlchemy)
│  ├─ Plan(title, subject, time_window, ...)
│  └─ Evidence(plan_id, filename, sha256, ...)
│
├─ Schemas (Pydantic)
│  ├─ PlanCreate / PlanRead
│  ├─ Subject, TimeWindow, UserInfo, ...
│  └─ EvidenceRead
│
├─ Services
│  ├─ audit.log() → audit_logs table
│  ├─ lgpd_check() → validates plan
│  └─ generate_plan_pdf() → exports/plan_{id}.pdf
│
└─ Routes
   ├─ POST /plans (create)
   ├─ GET /plans (list)
   ├─ GET /plans/{id} (read)
   ├─ POST /plans/{id}/lgpd_check (validate)
   ├─ GET /export/pdf/{id} (export)
   ├─ GET /export/html/{id} (export)
   ├─ POST /evidence/upload (upload)
   └─ GET /health (check)
```

### Persistência (SQLite)

```
SQLite (app.db)
│
├─ plans
│  ├─ id (PK)
│  ├─ title
│  ├─ subject (JSON)
│  ├─ time_window (JSON)
│  ├─ user (JSON)
│  ├─ purpose
│  ├─ deadline (JSON)
│  ├─ aspects_* (JSON arrays)
│  ├─ pirs (JSON array)
│  ├─ collection (JSON array)
│  ├─ extraordinary (JSON array)
│  ├─ security (JSON array)
│  ├─ created_at
│  └─ updated_at
│
├─ evidences
│  ├─ id (PK)
│  ├─ plan_id (FK)
│  ├─ filename
│  ├─ sha256
│  ├─ size
│  └─ created_at
│
└─ audit_logs (dynamic)
   ├─ id (PK)
   ├─ plan_id (FK)
   ├─ action
   ├─ detail
   ├─ actor
   └─ created_at
```

---

## Boas Práticas

### 1. Configuração de Segurança para Produção

```python
# backend/app/main.py

# Adicionar CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-dominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar Rate Limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/plans")
@limiter.limit("10/minute")
async def create_plan(...):
    ...
```

### 2. Logging Estruturado

```python
# backend/app/main.py

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/plans")
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating plan: {payload.title}")
    plan = Plan(...)
    logger.info(f"Plan {plan.id} created successfully")
    return _to_read(plan)
```

### 3. Validação de Entrada

```python
# Usar Pydantic automaticamente
class PlanCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    subject: Subject
    # Validação automática de tipos e limites
```

### 4. Tratamento de Erros

```python
@app.get("/plans/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    return _to_read(plan)
```

### 5. Índices no Banco

```python
# models.py
class Evidence(Base):
    __tablename__ = "evidences"
    plan_id = Column(Integer, nullable=False, index=True)
    # Index melhora queries by plan_id
```

---

## Troubleshooting

### ❌ Problema: "Connection refused" ao conectar com backend

**Solução:**
```bash
# Verificar se backend está rodando
lsof -i :8000

# Se não, iniciar:
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### ❌ Problema: "ModuleNotFoundError: No module named 'fastapi'"

**Solução:**
```bash
source venv/bin/activate
cd backend
pip install -r requirements.txt
```

### ❌ Problema: SQLite "database is locked"

**Solução:**
```bash
# Fechar outras conexões
# Ou usar WAL mode:
```python
# database.py
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    json_serializer=json.dumps,
    json_deserializer=json.loads,
    echo=False,
)
```

### ❌ Problema: "PermissionError" ao fazer upload

**Solução:**
```bash
# Criar diretórios
mkdir -p backend/uploads backend/exports

# Ou deixar código criar (já faz):
os.makedirs("uploads", exist_ok=True)
```

### ❌ Problema: PDF vazio ou com caracteres estranhos

**Solução:**
```python
# pdf.py já usa ensure_ascii=False
json.dumps(data, ensure_ascii=False)
```

---

## Checklist de Deploy

- [ ] PostgreSQL configurado (se não SQLite)
- [ ] Variáveis de ambiente (.env) preenchidas
- [ ] API Key ativada (`REQUIRE_API_KEY=true`)
- [ ] CORS configurado
- [ ] HTTPS/SSL ativado
- [ ] Backups automáticos do banco
- [ ] Logs centralizados (e.g., CloudWatch)
- [ ] Monitoramento de uptime
- [ ] Rate limiting ativado
- [ ] Testes passando (pytest)
- [ ] Documentação atualizada
- [ ] V1 da API versionada (`/api/v1/plans`)

---

## Contribuindo

### 1. Fork do repositório
```bash
git clone https://seu-fork/intel_planning_osint_mvp_v3.git
```

### 2. Branch para feature
```bash
git checkout -b feature/nova-funcionalidade
```

### 3. Commits descritivos
```bash
git commit -m "feat: adiciona validação de email"
```

### 4. Push e Pull Request
```bash
git push origin feature/nova-funcionalidade
```

---

**Documentação técnica concluída. Para dúvidas, consulte SYSTEM_REPORT.md ou README.md.**
