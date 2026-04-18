# 📊 Relatório do Sistema — ROC Planejamento de Inteligência v3

**Data:** 11 de Novembro de 2025  
**Versão:** 3.0  
**Status:** MVP em Produção  
**Ambiente:** Python 3.10+ | Streamlit | FastAPI | SQLite

---

## 📋 Sumário Executivo

O **ROC Planejamento de Inteligência** é uma plataforma web integrada para estruturação sistemática de operações de OSINT (Open Source Intelligence) seguindo a metodologia clássica de 10 fases de planejamento de inteligência.

### Objetivos Alcançados ✅
- ✅ Interface intuitiva para planejamento estruturado
- ✅ Persistência robusta de dados (SQLite com modelos SQLAlchemy)
- ✅ Geração de relatórios (PDF + HTML)
- ✅ Conformidade LGPD e auditoria completa
- ✅ Upload seguro de evidências com hash
- ✅ API RESTful totalmente documentada

---

## 🏗 Arquitetura do Sistema

### 1. **Camada de Apresentação (Frontend)**

**Tecnologia:** Streamlit 1.39.0

**Responsabilidades:**
- Interface SPA (Single Page Application) com navegação por sidebar
- 13 etapas interativas de coleta de dados
- Validação de entrada em tempo real
- Session state para manutenção de estado
- Chamadas HTTP assíncronas para backend via `httpx`

**Fluxo de Dados:**
```
Usuário → Streamlit UI → httpx.Client → FastAPI Backend → Resposta JSON → Streamlit UI
```

**Componentes Principais:**
- **Barra lateral:** Seletor de etapas (steps)
- **Formulários dinâmicos:** Inputs contextualmente relevantes
- **Preview section:** KPIs, Gantt, exportação
- **Validação:** Feedback imediato via `st.success()`, `st.error()`, `st.warning()`

**Variáveis de Ambiente:**
- `API_URL`: URL do backend (padrão: `http://localhost:8000`)

---

### 2. **Camada de Aplicação (Backend)**

**Tecnologia:** FastAPI 0.115.0 + Uvicorn 0.30.6

**Responsabilidades:**
- Definição e validação de schemas (Pydantic)
- Lógica de negócio (validação LGPD, geração de relatórios)
- Autenticação/Autorização (API Key opcional)
- Gerenciamento de uploads e hashing
- Auditoria de ações

**Middleware Implementado:**
```python
@app.middleware("http")
async def api_key_guard(request: Request, call_next):
    # Validação de X-API-Key se REQUIRE_API_KEY=true
```

**Endpoints Implementados:**

| Método | Rota | Função | Autenticação |
|--------|------|--------|---|
| `GET` | `/health` | Health check | Não |
| `POST` | `/plans` | Criar plano | Opcional |
| `GET` | `/plans` | Listar planos | Opcional |
| `GET` | `/plans/{id}` | Obter plano | Opcional |
| `POST` | `/plans/{id}/lgpd_check` | Validar LGPD | Opcional |
| `GET` | `/export/pdf/{id}` | Exportar PDF | Opcional |
| `GET` | `/export/html/{id}` | Exportar HTML | Opcional |
| `POST` | `/evidence/upload` | Upload de arquivo | Opcional |

---

### 3. **Camada de Dados (Persistência)**

**Tecnologia:** SQLite + SQLAlchemy 2.0.35

**Modelos:**

#### Tabela: `plans`
```sql
CREATE TABLE plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) DEFAULT 'Plano de Inteligência',
    subject TEXT NOT NULL,           -- JSON: {what, who, where}
    time_window TEXT NOT NULL,       -- JSON: {start, end}
    user TEXT NOT NULL,              -- JSON: {principal, others, depth, secrecy}
    purpose TEXT NOT NULL,
    deadline TEXT NOT NULL,          -- JSON: {date, urgency}
    aspects_essential TEXT NOT NULL, -- JSON array
    aspects_known TEXT NOT NULL,     -- JSON array
    aspects_to_know TEXT NOT NULL,   -- JSON array
    pirs TEXT DEFAULT '[]',          -- JSON array: [{aspect_ref, question, priority, justification}]
    collection TEXT DEFAULT '[]',    -- JSON array: [{pir_index, source, method, frequency, owner, sla_hours}]
    extraordinary TEXT,              -- JSON array
    security TEXT,                   -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: `evidences`
```sql
CREATE TABLE evidences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    sha256 VARCHAR(64) NOT NULL,     -- Hash SHA-256 do arquivo
    size INTEGER NOT NULL,            -- Tamanho em bytes
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: `audit_logs` (Criada dinamicamente)
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER,
    action TEXT,                     -- create_plan, export_pdf, upload_evidence, etc.
    detail TEXT,                     -- Descrição contextual
    actor TEXT,                       -- Usuário (padrão: 'analyst')
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Características:**
- ✅ JSON nativo para campos complexos (aspects, PIRs, coleta)
- ✅ Timestamps automáticos (created_at, updated_at)
- ✅ Integridade referencial (plan_id em evidences e audit_logs)
- ✅ Índices em plan_id para performance

---

### 4. **Serviços de Negócio**

#### **audit.py** — Auditoria
```python
def log(db, action, detail="", plan_id=None, actor="analyst"):
    # Registra todas as ações em audit_logs
```

**Ações Registradas:**
- `create_plan` → Quando plano é criado
- `lgpd_check` → Quando validação LGPD é executada
- `export_pdf` → Quando PDF é gerado
- `export_html` → Quando HTML é gerado
- `upload_evidence` → Quando arquivo é enviado

#### **lgpd.py** — Validação de Conformidade
```python
def lgpd_check(plan: dict) -> dict:
```

**Regras Implementadas:**
1. **Sigilo vs. Segurança:** Planos com sigilo "restrito", "confidencial" ou "secreto" **DEVEM** ter medidas de segurança definidas
2. **Medidas Obrigatórias:** Deve incluir pelo menos uma de: "controle de acesso", "criptografia", "trilha de auditoria"
3. **Faixa de Tempo Válida:** data_início ≤ data_fim
4. **Aspectos Coerentes:** Se aspectos_essenciais estão preenchidos, aspectos_a_conhecer **DEVE** estar preenchido

**Retorno:**
```json
{
  "ok": true/false,
  "issues": ["Lista de problemas encontrados"]
}
```

#### **pdf.py** — Geração de Relatórios PDF
```python
def generate_plan_pdf(plan: dict, outfile: str):
```

**Características:**
- Cabeçalho estilizado com data/hora
- Seções estruturadas (Identificação, Aspectos, PIRs, Coleta, Medidas)
- Suporte a logotipo customizado (via env `REPORT_LOGO_PATH`)
- Paginação automática para planos grandes
- Font: Helvetica com cores corporativas

**Saída:** `exports/plan_{plan_id}.pdf`

---

## 🔄 Fluxo de Dados — Caso de Uso Completo

### Cenário: Criar e Exportar um Plano de Inteligência

```
┌─────────────────┐
│   Usuário       │
│  (Streamlit)    │
└────────┬────────┘
         │
         │ 1. Preenche 13 etapas
         ▼
┌─────────────────────────────────────┐
│ Session State (st.session_state)    │
│ - plan: {title, subject, ...}       │
└────────┬────────────────────────────┘
         │
         │ 2. Clica "Salvar Plano"
         ▼
┌─────────────────────────────────────┐
│ Streamlit (Frontend)                │
│ httpx.Client.post("/plans", json)   │
└────────┬────────────────────────────┘
         │
         │ 3. HTTP POST
         ▼
┌──────────────────────────────────────┐
│ FastAPI Backend                      │
│ @app.post("/plans")                  │
│ create_plan(PlanCreate)              │
└────────┬─────────────────────────────┘
         │
         │ 4. Validação Pydantic
         ▼
┌──────────────────────────────────────┐
│ SQLAlchemy ORM                       │
│ Plan(title, subject_json, ...)       │
│ db.add(plan)                         │
│ db.commit()                          │
└────────┬─────────────────────────────┘
         │
         │ 5. Commit para SQLite
         ▼
┌──────────────────────────────────────┐
│ SQLite Database                      │
│ INSERT INTO plans (...)              │
│ VALUES (...)                         │
└────────┬─────────────────────────────┘
         │
         │ 6. ID retornado
         ▼
┌──────────────────────────────────────┐
│ audit.log()                          │
│ INSERT INTO audit_logs               │
│ action="create_plan"                 │
└────────┬─────────────────────────────┘
         │
         │ 7. Response JSON {id, title, ...}
         ▼
┌────────────────────────────┐
│ Streamlit                  │
│ st.success(f"ID: {id}")    │
│ Salva em session_state     │
└────────────────────────────┘
         │
         │ 8. Usuário clica "Exportar PDF"
         ▼
┌──────────────────────────────────────┐
│ FastAPI Backend                      │
│ @app.get("/export/pdf/{plan_id}")    │
│ export_pdf(plan_id)                  │
└────────┬─────────────────────────────┘
         │
         │ 9. Busca plano no SQLite
         ▼
┌──────────────────────────────────────┐
│ db.get(Plan, plan_id)                │
│ plan = {id, title, ...}              │
└────────┬─────────────────────────────┘
         │
         │ 10. Generate PDF
         ▼
┌──────────────────────────────────────┐
│ pdf.generate_plan_pdf()              │
│ Cria: exports/plan_{id}.pdf          │
└────────┬─────────────────────────────┘
         │
         │ 11. Auditoria
         ▼
┌──────────────────────────────────────┐
│ audit.log(action="export_pdf")       │
└────────┬─────────────────────────────┘
         │
         │ 12. Resposta: {file: path}
         ▼
┌────────────────────────────┐
│ Streamlit                  │
│ st.success("PDF gerado") ✅ │
└────────────────────────────┘
```

---

## 🔐 Segurança Implementada

### 1. Autenticação (API Key)
```python
# Opcional via variáveis de ambiente
REQUIRE_API_KEY = os.environ.get("REQUIRE_API_KEY", "false").lower() == "true"
API_KEY = os.environ.get("API_KEY", "devkey")

# Middleware valida X-API-Key em cada requisição
```

**Uso:**
```bash
curl -H "X-API-Key: sua_chave" http://localhost:8000/plans
```

### 2. Validação LGPD
- Conformidade com nível de sigilo
- Verificação de medidas de segurança obrigatórias
- Validação de integridade de dados

### 3. Hashing de Evidências
```python
sha256 = hashlib.sha256(content).hexdigest()
# Arquivo: uploads/{filename}
# BD: evidences.sha256 = {hash}
```

### 4. Auditoria Completa
- Rastreamento de todas as ações
- Actor, timestamp, action, detail
- Investigação forense de modificações

### 5. CORS (Futuro)
```python
# Recomendado para produção:
from fastapi.middleware.cors import CORSMiddleware
```

---

## 📊 KPIs e Métricas

### Calculados em Preview:

1. **Aspectos Essenciais (total_ess)**
   - Contador de items em `aspects_essential[]`

2. **Aspectos Conhecidos (total_known)**
   - Contador de items em `aspects_known[]`

3. **Aspectos a Conhecer (total_to_know)**
   - Contador de items em `aspects_to_know[]`

4. **PIRs (total_pirs)**
   - Contador de items em `pirs[]`

5. **Tarefas de Coleta (total_tasks)**
   - Contador de items em `collection[]`

6. **Coverage**
   ```
   Coverage = (Conhecidos / Essenciais) * 100%
   ```
   Indica % de cobertura de conhecimento já disponível

7. **Linkage**
   ```
   Linkage = (Tarefas / PIRs) * 100%
   ```
   Indica % de PIRs com tarefas de coleta associadas

### Exemplo:
```
Essenciais: 5
Conhecidos: 3
A Conhecer: 2
PIRs: 6
Tarefas: 4

Coverage = 3/5 * 100 = 60%
Linkage = 4/6 * 100 = 67%
```

---

## 📅 Gantt Chart (Simplificado)

**Localização:** Seção Preview

**Dados:**
- Tarefa: `PIR#{pir_index} - {source}`
- Início: `deadline_date - sla_hours`
- Fim: `deadline_date`

**Exemplo:**
```
| Tarefa              | Início        | Fim           |
|---------------------|---------------|---------------|
| PIR0 - Google       | 2025-11-10    | 2025-11-11    |
| PIR1 - LinkedIn     | 2025-11-09    | 2025-11-11    |
```

---

## 🧪 Estratégia de Testes

**Framework:** pytest (conforme `pytest.ini`)

**Cobertura Esperada:**

### Testes Unitários (`tests/test_api.py`)
- ✅ `/health` — Health check
- ✅ `POST /plans` — Criar plano válido/inválido
- ✅ `GET /plans` — Listar planos
- ✅ `GET /plans/{id}` — Obter plano específico
- ✅ `POST /plans/{id}/lgpd_check` — Validação LGPD
- ✅ `GET /export/pdf/{id}` — Geração de PDF
- ✅ `GET /export/html/{id}` — Geração de HTML
- ✅ `POST /evidence/upload` — Upload de arquivo

### Testes de Integração
- API Key validation (com/sem `REQUIRE_API_KEY`)
- Session state management (Streamlit)
- httpx client error handling

### Testes de Carga (Futuro)
- 100+ planos simultâneos
- Upload de arquivos >100MB
- Concorrência de requisições

---

## 📈 Performance e Escalabilidade

### Análise Atual:

| Métrica | Valor | Status |
|---------|-------|--------|
| Banco de dados | SQLite | ⚠️ Dev/MVP |
| Conexões | SessionLocal() | ✅ Pool básico |
| Timeout HTTP | 10-60s | ✅ Configurável |
| Tamanho máx. upload | ~1GB (RAM) | ⚠️ Limitar em prod |
| Serialização JSON | Nativa | ✅ Eficiente |

### Recomendações para Produção:

1. **Banco de Dados Escalável**
   ```python
   # Trocar SQLite por PostgreSQL
   DATABASE_URL = "postgresql://user:pass@host/dbname"
   ```

2. **Limite de Upload**
   ```python
   @app.post("/evidence/upload")
   async def upload_evidence(..., file: UploadFile):
       # MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
       if len(content) > MAX_FILE_SIZE:
           raise HTTPException(413, "File too large")
   ```

3. **Connection Pool**
   ```python
   from sqlalchemy.pool import NullPool
   engine = create_engine(db_url, poolclass=NullPool)
   ```

4. **Caching**
   ```python
   from functools import lru_cache
   @lru_cache(maxsize=128)
   def get_plan_cached(plan_id):
       ...
   ```

5. **Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

---

## 🚀 Deployment

### Opção 1: Heroku

```bash
# requirements.txt (raiz)
# Procfile
web: gunicorn app.main:app
worker: streamlit run app/streamlit_app.py
```

### Opção 2: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r backend/requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Opção 3: AWS/GCP

- Backend: ECS/Cloud Run
- Frontend: Streamlit Cloud
- BD: RDS PostgreSQL
- Storage: S3/Cloud Storage

---

## 🐛 Problemas Conhecidos e Roadmap

### Problemas Conhecidos ⚠️

1. **SQLite em Produção**
   - Não recomendado para >100 usuários simultâneos
   - **Solução:** Migrar para PostgreSQL

2. **Upload de Grandes Arquivos**
   - Carregamento em memória (RAM)
   - **Solução:** Streaming com chunks

3. **CORS**
   - Não configurado (apenas localhost)
   - **Solução:** Adicionar middleware CORS

4. **Timeout de PDF Grande**
   - Planos com muitos dados → PDF lento
   - **Solução:** Async PDF generation com Celery

### Roadmap v4 📋

- [ ] Autenticação OAuth2 (Google, Microsoft)
- [ ] Dashboard de analytics
- [ ] Coleta automática via APIs (Twitter, LinkedIn, etc.)
- [ ] IA para sugestão de PIRs
- [ ] Versionamento de planos (Git-like)
- [ ] Integração com sistema de ticketing (Jira)
- [ ] Relatórios em Excel (.xlsx)
- [ ] Mobile app (React Native)

---

## 📝 Estrutura de Dados — Exemplo Completo

```json
{
  "id": 1,
  "title": "Inteligência sobre Concorrentes",
  "subject": {
    "what": "Estratégia de mercado da Empresa X",
    "who": "Tech Director",
    "where": "Brasil"
  },
  "time_window": {
    "start": "2025-11-01",
    "end": "2025-12-31"
  },
  "user": {
    "principal": "João Silva",
    "others": "Equipe de Inovação",
    "depth": "gerencial",
    "secrecy": "confidencial"
  },
  "purpose": "Identificar oportunidades de parceria ou ameaças competitivas",
  "deadline": {
    "date": "2025-11-30",
    "urgency": "alta"
  },
  "aspects_essential": [
    "Estrutura organizacional",
    "Portfólio de produtos",
    "Parcerias e clientes"
  ],
  "aspects_known": [
    "Portfólio público no site"
  ],
  "aspects_to_know": [
    "Estrutura interna recente",
    "Clientes não públicos"
  ],
  "pirs": [
    {
      "aspect_ref": 0,
      "question": "Qual é a estrutura organizacional atual?",
      "priority": "alta",
      "justification": "Essencial para compreender capacidades"
    }
  ],
  "collection": [
    {
      "pir_index": 0,
      "source": "LinkedIn",
      "method": "Scraping de perfis",
      "frequency": "semanal",
      "owner": "Analytics Team",
      "sla_hours": 24
    }
  ],
  "extraordinary": [
    "Entrevista com ex-funcionários"
  ],
  "security": [
    "Criptografia de transmissão",
    "Controle de acesso RBAC"
  ],
  "evidences": [
    {
      "id": 1,
      "filename": "org_chart.png",
      "sha256": "abc123...",
      "size": 256000
    }
  ]
}
```

---

## 📞 Contato e Suporte

**Equipe:** ROC Project Team  
**Email:** suporte@rocproject.io  
**Issues:** GitHub Issues (se aplicável)  
**Documentação API:** http://localhost:8000/docs (Swagger UI)

---

## 🎯 Conclusão

O **ROC Planejamento de Inteligência v3** é uma solução robusta e completa para estruturação de operações de OSINT, com:

✅ Arquitetura clara e escalável  
✅ Segurança e auditoria nativas  
✅ Conformidade LGPD  
✅ Geração de relatórios profissionais  
✅ API RESTful totalmente documentada  
✅ Pronto para expansão e customização  

Recomenda-se para **MVP** → **Produção** adicionar PostgreSQL, Redis cache e CORS middleware.

---

**Relatório gerado em:** 11/11/2025  
**Versão do sistema:** 3.0  
**Status:** ✅ Operacional
