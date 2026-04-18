# ROC Planejamento de Inteligência — MVP v3

Aplicação web para **planejamento sistemático de operações de inteligência** (OSINT) seguindo a metodologia de **Planejamento de Inteligência em 10 fases**.

Arquitetura: **Streamlit** (frontend) + **FastAPI** (backend) + **SQLite** (banco de dados).

📖 **Manual de Operação:** [**docs/MANUAL_DE_OPERACAO.md**](docs/MANUAL_DE_OPERACAO.md) — Guia passo a passo para criar e exportar planos de inteligência.

## 📋 Características Principais

### Frontend (Streamlit)
- ✅ Interface interativa com **13 etapas de planejamento** estruturadas
- ✅ Coleta de informações: Assunto, Tempo, Usuário, Finalidade, Prazo
- ✅ Análise de Aspectos: Essenciais, Conhecidos, A Conhecer
- ✅ Gerenciamento de **PIRs** (Priority Intelligence Requirements)
- ✅ Planejamento de **Tarefas de Coleta** com SLA
- ✅ Medidas Extraordinárias e de Segurança
- ✅ **Pré-visualização** com KPIs e Gantt simplificado
- ✅ Exportação em **PDF** e **HTML** (com logotipo personalizado)
- ✅ **Upload de evidências** com hash SHA-256

### Backend (FastAPI)
- ✅ API RESTful para gerenciar Planos de Inteligência
- ✅ Persistência em **SQLite**
- ✅ **Validação LGPD** automática (sigilo e medidas de segurança)
- ✅ **Auditoria** de todas as ações
- ✅ Geração de relatórios em **PDF** e **HTML**
- ✅ Gerenciamento de **evidências** (upload + hash)
- ✅ **Segurança** com API Key opcional (`REQUIRE_API_KEY`, `REQUIRE_API_KEY_FOR_BACKUP`, `API_KEY`)
- ✅ Health check (`/health`)

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.10+
- pip ou conda

### ⚡ Execução Rápida (One-Click para Usuários)

Se você é um **usuário não-técnico** e quer rodar a aplicação rapidamente:

#### macOS / Linux
```bash
# No Terminal, navegue até a pasta do projeto e execute:
./run_local.sh
```

✅ Isso iniciará automaticamente:
- Backend (FastAPI) na porta 8000
- Frontend (Streamlit) na porta 8501

Acesse: **http://localhost:8501**

**Para encerrar:** Pressione `Ctrl + C` no Terminal.

📖 **Guia completo:** Consulte o [Manual de Operação](docs/MANUAL_DE_OPERACAO.md).

---

### 1. Clonar e Preparar Ambiente

```bash
cd /Users/rikardocroce/Library/CloudStorage/OneDrive-Personal/# ROC project Dsvn/BYIP/intel_planning_osint_mvp_v3
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 2. Instalar Dependências

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../app
pip install -r requirements.txt
```

### 3. Iniciar o Backend (FastAPI)

```bash
cd backend
export REPORT_LOGO_PATH=/caminho/para/logo.png  # (opcional)
export REQUIRE_API_KEY=true  # (opcional)
export API_KEY=seu_token_secreto  # (opcional)

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: **http://localhost:8000**
- Documentação Swagger: **http://localhost:8000/docs**
- Documentação ReDoc: **http://localhost:8000/redoc**

### 4. Iniciar o Frontend (Streamlit) — Em outro terminal

```bash
cd app
streamlit run streamlit_app.py
```

Acesse: **http://localhost:8501**

## 📊 Estrutura do Projeto

```
.
├── README.md                          # Este arquivo
├── RUNNING.md                         # Instruções de execução
├── Makefile                           # Comandos auxiliares
├── pytest.ini                         # Configuração de testes
│
├── app/                               # Frontend (Streamlit)
│   ├── streamlit_app.py              # Aplicação principal
│   └── requirements.txt               # Dependências
│
├── backend/                           # Backend (FastAPI)
│   ├── requirements.txt               # Dependências
│   └── app/
│       ├── main.py                    # Aplicação FastAPI (rotas)
│       ├── db/
│       │   └── database.py            # Configuração SQLite + SessionLocal
│       ├── models/
│       │   └── models.py              # SQLAlchemy models (Plan, Evidence, AuditLog)
│       ├── schemas/
│       │   └── schemas.py             # Pydantic schemas (PlanCreate, PlanRead, etc.)
│       └── services/
│           ├── audit.py               # Logging de auditoria
│           ├── lgpd.py                # Validação de conformidade LGPD
│           └── pdf.py                 # Geração de relatórios PDF
│
└── tests/
    ├── __init__.py
    ├── test_api.py                    # Testes unitários da API
    └── ...
```

## � Preparar para subir ao GitHub

Antes de subir o projeto para o repositório remoto, verifique os itens abaixo e siga os comandos recomendados.

1) Verifique `.gitignore` (já fornecido) para não comitar arquivos sensíveis como `.env`, `backend/app.db`, `BYIP_BkUp/` e diretórios de ambiente/IDE.

2) Se ainda não há repositório Git local, inicialize e faça o primeiro commit:

```bash
# no diretório raiz do projeto
git init
git add .
git commit -m "chore: initial project import"
```

3) Conectar ao repositório remoto (substitua se necessário):

```bash
git remote add origin https://github.com/Georastreador/ROC_BYIP.git
git branch -M main
git push -u origin main
```

Observações importantes:
- Não faça push de arquivos sensíveis. Use `.env` e `backend/.env` locais e mantenha-os fora do repositório.
- Se sua organização usar branch diferente (ex.: `master`), ajuste os comandos acima.
- Para autenticar o push, use suas credenciais GitHub ou um token pessoal (PAT) com permissões adequadas.

Se preferir, crie um fork/branch para desenvolvimento colaborativo e abra Pull Requests para integrar mudanças ao repositório remoto principal.


## �🔌 API REST — Endpoints Principais

### Planos de Inteligência

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/plans` | Criar novo plano |
| `GET` | `/plans` | Listar todos os planos |
| `GET` | `/plans/{plan_id}` | Obter plano por ID |
| `POST` | `/plans/{plan_id}/lgpd_check` | Validar conformidade LGPD |

### Exportação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/export/pdf/{plan_id}` | Exportar plano em PDF |
| `GET` | `/export/html/{plan_id}` | Exportar plano em HTML |

### Evidências

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/evidence/upload` | Fazer upload de arquivo + calcular SHA-256 |

### Sistema

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check |

## 📝 Exemplo de Uso — Fluxo Completo

### 1. Acessar Streamlit
```bash
streamlit run app/streamlit_app.py
```

### 2. Preencher o Formulário (13 etapas)
- **Etapa 1 (Assunto):** Título, O quê?, Quem?, Onde?
- **Etapa 2 (Tempo):** Data início e fim
- **Etapa 3 (Usuário):** Usuário principal, nível de profundidade, sigilo
- **Etapa 4 (Finalidade):** Descrição do objetivo
- **Etapa 5 (Prazo):** Data limite + urgência
- **Etapas 6-10:** Aspectos (Essenciais, Conhecidos, A Conhecer), PIRs, Coleta
- **Etapas 11-12:** Medidas (Extraordinárias, Segurança)
- **Etapa 13 (Preview):** KPIs, Gantt e opções de export

### 3. Salvar Plano
Clique em **"Salvar Plano (API)"** → plano é persistido no banco e ID é exibido

### 4. Validar LGPD
Clique em **"Checar LGPD (API)"** → validação de conformidade é exibida em painel expansível

### 5. Exportar Relatório
Interface com abas para maior clareza:

#### Aba: Exportar
- **PDF:** 
  1. Clique em **"📥 Gerar PDF"** → arquivo é gerado no servidor
  2. Clique em **"⬇️ Baixar PDF"** → arquivo é baixado no seu computador
  
- **HTML:**
  1. Clique em **"📥 Gerar HTML"** → arquivo é gerado no servidor
  2. Clique em **"⬇️ Baixar HTML"** → arquivo é baixado no seu computador

✅ **Novo:** Downloads diretos no navegador (sem salvar no servidor)

### 6. Anexar Evidências
#### Aba: Evidências
- Após salvar o plano, faça upload de arquivos
- SHA-256 é calculado automaticamente
- Arquivo é vinculado ao plano

## 🔐 Segurança

### API Key (Opcional)
```bash
export REQUIRE_API_KEY=true
export API_KEY=seu_token_secreto
```

Incluir no header da requisição:
```bash
curl -H "X-API-Key: seu_token_secreto" http://localhost:8000/plans
```

### Validação LGPD
- ✅ Verifica nível de sigilo vs. medidas de segurança
- ✅ Valida faixa de tempo
- ✅ Exige aspectos a conhecer quando essenciais estão definidos

### Auditoria
- Todas as ações (create, read, export, upload) são registradas em `audit_logs`
- Actor, timestamp, action, detail e plan_id são rastreados

## 📦 Dependências

### Frontend (`app/requirements.txt`)
```
fastapi==0.115.0
uvicorn==0.30.6
pydantic==2.9.2
SQLAlchemy==2.0.35
reportlab==4.2.5
streamlit==1.39.0
httpx==0.27.2
python-multipart==0.0.12
```

### Backend (`backend/requirements.txt`)
- Mesmas dependências (projeto unificado)

## 🧪 Testes

```bash
pytest tests/ -v
```

## 🛠 Makefile — Comandos Auxiliares

```bash
make run-backend    # Inicia Backend (FastAPI)
make run-frontend   # Inicia Frontend (Streamlit)
make test          # Executa testes
make clean         # Remove cache e arquivos temporários
```

## 🌐 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `API_URL` | URL do backend (frontend) | `http://localhost:8000` |
| `REQUIRE_API_KEY` | Exigir API Key em todas as rotas | `false` |
| `REQUIRE_API_KEY_FOR_BACKUP` | Exigir API Key nas rotas de backup | `false` |
| `API_KEY` | Token de segurança (obrigatório se REQUIRE_API_KEY ou REQUIRE_API_KEY_FOR_BACKUP) | — |
| `REPORT_LOGO_PATH` | Caminho do logo (PDF/HTML) | ` ` (vazio) |
| `CORS_ORIGINS` | Origens permitidas (CORS) | `localhost:8501,8502,3000` (dev) |
| `RATE_LIMIT_ENABLED` | Habilitar rate limiting | `true` |
| `MAX_FILE_SIZE` | Tamanho máximo de upload (bytes) | `52428800` (50MB) |
| `DEBUG` | Modo debug (expõe detalhes de erros) | `false` |
| `BACKUP_DIR` | Diretório de backups | `backend/backups` |
| `BACKUP_RETENTION_DAYS` | Dias de retenção de backups | `30` |
| `EXPORTS_DIR` | Diretório de exports (PDF/HTML) | `exports` |
| `EXPORTS_RETENTION_HOURS` | Horas de retenção de exports | `24` |
| `DATABASE_PATH` | Caminho do banco de dados | `backend/plans.db` |
| `HOST` | Host do backend (run_local.sh) | `127.0.0.1` |

### Configuração CORS

Por padrão, a API permite requisições de `localhost` nas portas comuns (8501, 8502, 3000).

Para produção, configure origens específicas:

```bash
export CORS_ORIGINS="https://seu-dominio.com,https://app.seu-dominio.com"
```

**Formato:** URLs separadas por vírgula, sem espaços.

### Configuração Rate Limiting

A API possui rate limiting configurado para proteger contra abuso:

**Limites por Endpoint:**
- Health check: 100/minuto
- Criação de planos: 20/minuto
- Leitura de planos: 60/minuto
- Upload de evidências: 5/minuto
- Export PDF: 10/minuto
- Backup create: 5/minuto
- Backup restore: 3/minuto
- Backup list: 30/minuto

**Desabilitar (desenvolvimento):**
```bash
export RATE_LIMIT_ENABLED=false
```

**Habilitar (produção - padrão):**
```bash
export RATE_LIMIT_ENABLED=true
```

### Configuração de Upload

A API possui validações de segurança para uploads de arquivos:

**Limites:**
- Tamanho máximo: 50MB (configurável via `MAX_FILE_SIZE`)
- Tipos permitidos: PDF, imagens (PNG, JPG, GIF), texto (TXT, MD, CSV), Office (DOC, DOCX, XLS, XLSX), compactados (ZIP, RAR, 7Z), dados (JSON, XML)

**Configurar tamanho máximo:**
```bash
# 100MB (em bytes)
export MAX_FILE_SIZE=104857600

# 25MB
export MAX_FILE_SIZE=26214400
```

**Validações Implementadas:**
- ✅ Validação de extensão de arquivo
- ✅ Validação de MIME type
- ✅ Verificação de tamanho durante upload (streaming)
- ✅ Sanitização de nomes de arquivo
- ✅ Proteção contra path traversal

### Tratamento de Erros

A API possui tratamento centralizado de erros com logging estruturado:

**Tipos de Erro Tratados:**
- Erros de banco de dados (SQLAlchemy)
- Erros de validação (Pydantic)
- Erros de JSON inválido
- Erros de arquivo não encontrado
- Erros de permissão
- Timeouts
- Erros genéricos

**Modo Debug:**
```bash
# Habilitar modo debug (expõe detalhes completos de erros)
export DEBUG=true

# Modo produção (padrão): mensagens genéricas
export DEBUG=false
```

**Logging:**
- Logs estruturados em JSON
- Inclui: tipo de erro, path, method, IP do cliente
- Traceback completo em modo debug

### Backup e Recuperação

A API possui sistema completo de backup e recuperação do banco de dados:

**Endpoints de Backup:**
- `POST /backup/create` - Criar backup manual
- `GET /backup/list` - Listar todos os backups
- `POST /backup/restore/{filename}` - Restaurar backup específico
- `GET /backup/stats` - Estatísticas de backups

**Scripts Manuais:**
```bash
# Criar backup
cd backend
python scripts/backup_manual.py

# Restaurar backup
python scripts/restore_backup.py plans_backup_20251117_214042.db
```

**Backup Agendado (Cron):**
```bash
# Adicionar ao crontab para backup diário às 2h
0 2 * * * /caminho/para/backend/scripts/backup_scheduled.sh
```

**Configuração:**
```bash
# Diretório de backups
export BACKUP_DIR="/caminho/para/backups"

# Retenção (dias)
export BACKUP_RETENTION_DAYS=30

# Caminho do banco
export DATABASE_PATH="/caminho/para/plans.db"
```

**Características:**
- ✅ Verificação de integridade automática
- ✅ Limpeza automática de backups antigos
- ✅ Backup de segurança antes de restaurar
- ✅ Logging de todas as operações

## 📚 Metodologia — Planejamento de Inteligência (a→j)

A aplicação segue a estrutura de **10 fases** de um Plano de Inteligência:

1. **a) Assunto** — O quê, quem, onde
2. **b) Faixa de Tempo** — Período de análise
3. **c) Usuário** — Perfil do demandante
4. **d) Finalidade** — Objetivo do conhecimento
5. **e) Prazo** — Deadline + urgência
6. **f) Aspectos Essenciais** — O que é crítico
7. **g) Aspectos Conhecidos** — O que já se sabe
8. **h) Aspectos a Conhecer** — O que falta descobrir
9. **i) PIRs & Coleta** — Requisitos + plano de coleta
10. **j) Medidas** — Segurança e extraordinárias

**Preview:** Exibe KPIs (Coverage, Linkage) e Gantt das tarefas.

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra uma issue ou pull request.

## 📄 Licença

Projeto ROC — Todos os direitos reservados.

## 📞 Suporte

Para dúvidas ou bugs, entre em contato com a equipe de desenvolvimento ROC.
