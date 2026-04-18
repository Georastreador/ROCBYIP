# Como Rodar a Aplicação — OSINT Planning MVP v3

## 📋 Estrutura da Aplicação

- **Backend**: FastAPI em `backend/app/main.py` (porta 8000)
- **Frontend**: Streamlit em `app/streamlit_app.py` (porta 8502)
- **Banco de Dados**: SQLAlchemy (SQLite por padrão em `test.db`)

---

## 🚀 Pré-requisitos

1. **Python 3.9+** instalado
2. **pip** (gerenciador de pacotes)
3. Recomendado: **virtualenv**

---

## 📦 Instalação das Dependências

### Opção 1: Criar e ativar virtualenv (recomendado)

```bash
cd /Users/rikardocroce/Library/CloudStorage/OneDrive-Personal/\#\ ROC\ project\ Dsvn/BYIP/intel_planning_osint_mvp_v3
python3 -m venv .venv
source .venv/bin/activate
```

### Opção 2: Usar Python direto (sem isolamento)

Pule para o próximo passo.

### Instalar pacotes

```bash
pip install -r backend/requirements.txt
pip install -r app/requirements.txt
```

Ou, se forem os mesmos (já que estão duplicados):

```bash
pip install -r backend/requirements.txt
```

---

## ▶️ Rodar a Aplicação Completa

### 1️⃣ Terminal 1: Rodar o Backend (FastAPI)

```bash
cd /Users/rikardocroce/Library/CloudStorage/OneDrive-Personal/\#\ ROC\ project\ Dsvn/BYIP/intel_planning_osint_mvp_v3
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Saída esperada:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Verificar saúde (em outro terminal):
```bash
curl http://127.0.0.1:8000/health
# Resposta esperada: {"status":"ok"}
```

### 2️⃣ Terminal 2: Rodar o Frontend (Streamlit)

```bash
cd /Users/rikardocroce/Library/CloudStorage/OneDrive-Personal/\#\ ROC\ project\ Dsvn/BYIP/intel_planning_osint_mvp_v3
streamlit run app/streamlit_app.py
```

Saída esperada:
```
Local URL: http://localhost:8502
Network URL: http://192.168.0.44:8502
```

Acesse em seu navegador: **http://localhost:8502**

---

## 🔧 Variáveis de Ambiente (Opcional)

Se quiser customizar a aplicação:

```bash
# Para usar uma chave de API diferente no backend
export API_KEY="sua_chave_segura"
export REQUIRE_API_KEY="true"

# Para apontar o Streamlit para um backend diferente
export API_URL="http://192.168.0.100:8000"

# Para usar um banco de dados diferente (padrão: test.db)
export DATABASE_URL="sqlite:///./custom_db.db"
```

---

## 🧪 Testes

Atualmente **não há testes automáticos** no repositório. Para adicionar testes básicos:

### Instalar pytest

```bash
pip install pytest httpx
```

### Criar arquivo de teste

Crie `tests/test_health.py`:

```python
import httpx

def test_health():
    """Testa o endpoint /health da API"""
    r = httpx.get("http://127.0.0.1:8000/health", timeout=2.0)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
```

### Rodar teste (com backend rodando)

```bash
pytest -v
```

---

## 📝 Endpoints da API (Backend)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Verifica saúde da API |
| POST | `/plans` | Criar novo plano |
| GET | `/plans` | Listar todos os planos |
| GET | `/plans/{plan_id}` | Obter plano específico |
| POST | `/plans/{plan_id}/lgpd_check` | Verificar conformidade LGPD |
| POST | `/evidence/upload` | Upload de evidência |
| GET | `/export/pdf/{plan_id}` | Exportar plano como PDF |
| GET | `/export/html/{plan_id}` | Exportar plano como HTML |

---

## 🐛 Solução de Problemas

### Erro: "Address already in use"
A porta 8000 ou 8502 já está em uso. Libere com:
```bash
# Para matar processos na porta 8000
lsof -ti:8000 | xargs kill -9

# Para matar processos na porta 8502
lsof -ti:8502 | xargs kill -9
```

### Erro: "No such module 'backend'"
Certifique-se de estar na raiz do projeto ao executar o comando uvicorn.

### Erro: "StreamlitSecretNotFoundError"
✅ Já foi corrigido! A aplicação agora usa `os.getenv()` em vez de `st.secrets.get()`.

---

## 📚 Estrutura de Arquivos

```
.
├── README.md
├── RUNNING.md (este arquivo)
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py (FastAPI app)
│       ├── db/
│       │   └── database.py
│       ├── models/
│       │   └── models.py
│       ├── schemas/
│       │   └── schemas.py
│       └── services/
│           ├── audit.py
│           ├── lgpd.py
│           └── pdf.py
├── app/
│   ├── requirements.txt
│   └── streamlit_app.py (Streamlit UI)
└── exports/ (gerado em runtime - PDFs/HTMLs)
    └── uploads/ (gerado em runtime - evidências)
```

---

## ✅ Checklist Rápido

- [ ] Python 3.9+ instalado
- [ ] Dependências instaladas: `pip install -r backend/requirements.txt`
- [ ] Backend rodando: `uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`
- [ ] Backend saudável: `curl http://127.0.0.1:8000/health`
- [ ] Frontend rodando: `streamlit run app/streamlit_app.py`
- [ ] Frontend acessível em `http://localhost:8502`

---

**Data de atualização**: 11 de novembro de 2025
