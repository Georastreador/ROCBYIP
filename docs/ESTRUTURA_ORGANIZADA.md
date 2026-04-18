# 📁 Estrutura Organizada - ROCBYIP vf1

**Data de Organização:** 2025-01-27  
**Status:** ✅ Organização Concluída

---

## 📂 Estrutura de Pastas

```
ROCBYIP vf1/
│
├── 📄 Arquivos Principais
│   ├── main.py                    # Script de inicialização
│   ├── README.md                  # Documentação principal
│   ├── RELATORIO_VULNERABILIDADES.md
│   ├── LICENSE                    # Licença
│   ├── Makefile                   # Comandos auxiliares
│   ├── pytest.ini                 # Configuração de testes
│   └── .gitignore                 # Arquivos ignorados pelo Git
│
├── 🔒 security/                    # Módulo de Segurança
│   ├── __init__.py
│   └── security_utils.py        # Utilitários de segurança
│
├── 📚 docs/                        # Documentação
│   ├── CORRECOES_IMPLEMENTADAS.md
│   ├── ESTRUTURA_ORGANIZADA.md
│   └── [outros documentos em DOC/]
│
├── 📦 archive/                     # Arquivos Arquivados
│   ├── replit/                   # Arquivos do Replit
│   └── old_versions/             # Versões antigas (se houver)
│
├── 🌐 backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── main.py              # Aplicação principal
│   │   ├── db/                  # Banco de dados
│   │   ├── models/              # Modelos SQLAlchemy
│   │   ├── schemas/             # Schemas Pydantic
│   │   └── services/            # Serviços (audit, backup, lgpd, pdf)
│   ├── backups/                 # Backups do banco
│   ├── plans.db                 # Banco SQLite
│   ├── requirements.txt         # Dependências
│   └── scripts/                 # Scripts de backup
│
├── 🎨 app/                        # Frontend Streamlit
│   ├── streamlit_app.py         # Aplicação Streamlit
│   ├── requirements.txt         # Dependências
│   └── attached_assets/         # Assets e imagens
│
├── 🧪 tests/                       # Testes
│   ├── __init__.py
│   └── test_api.py              # Testes da API
│
├── 📦 exports/                     # Arquivos Exportados
│   └── [PDFs e HTMLs gerados]
│
├── 📤 uploads/                     # Arquivos Uploadados
│   └── [evidências uploadadas]
│
└── 📚 DOC/                         # Documentação Técnica
    ├── ARCHITECTURE.md
    ├── TECHNICAL_DOCS.md
    ├── ANALISE_PRODUCAO.md
    └── [outros documentos]
```

---

## 📋 Descrição das Pastas

### 📄 Arquivos Principais (Raiz)
- **main.py**: Script de inicialização
- **README.md**: Documentação principal do projeto
- **RELATORIO_VULNERABILIDADES.md**: Relatório de segurança

### 🔒 security/
Módulo de segurança com utilitários:
- **security_utils.py**: Funções de sanitização, validação e segurança

### 🌐 backend/
Backend FastAPI com toda a lógica de negócio:
- **app/main.py**: API REST principal
- **app/db/**: Configuração do banco de dados
- **app/models/**: Modelos SQLAlchemy
- **app/schemas/**: Schemas Pydantic para validação
- **app/services/**: Serviços especializados (auditoria, backup, LGPD, PDF)

### 🎨 app/
Frontend Streamlit:
- **streamlit_app.py**: Interface do usuário
- **attached_assets/**: Imagens e assets

### 🧪 tests/
Testes automatizados:
- **test_api.py**: Testes da API REST

### 📚 DOC/
Documentação técnica completa:
- Arquitetura, guias técnicos, análises

---

## 🗑️ Arquivos Removidos/Arquivados

### Removidos:
- ✅ `__pycache__/` - Cache Python (regenerado automaticamente)
- ✅ `*.pyc` - Arquivos compilados Python

### Arquivados:
- ✅ `.replit` → `archive/replit/.replit`
- ✅ `uv.lock` → `archive/`
- ✅ `pyproject.toml` → `archive/`

---

## 📝 Arquivos Mantidos na Raiz

Apenas arquivos essenciais para execução:
- ✅ `main.py` - Script de inicialização
- ✅ `README.md` - Documentação principal
- ✅ `RELATORIO_VULNERABILIDADES.md` - Relatório de segurança
- ✅ `LICENSE` - Licença
- ✅ `Makefile` - Comandos auxiliares
- ✅ `pytest.ini` - Configuração de testes
- ✅ `.gitignore` - Configuração Git

---

## 🚀 Como Usar a Estrutura

### Executar a Aplicação:
```bash
# Via Makefile
make run-backend    # Inicia Backend (FastAPI)
make run-frontend   # Inicia Frontend (Streamlit)

# Ou diretamente
python main.py
```

### Executar Testes:
```bash
pytest tests/ -v
```

### Acessar Documentação:
- Ver `DOC/` para documentação técnica
- Ver `README.md` para início rápido
- Ver `RELATORIO_VULNERABILIDADES.md` para análise de segurança

---

## 📌 Notas Importantes

1. **Não edite arquivos em `archive/`** - São arquivos antigos mantidos apenas para referência
2. **Cache Python** é gerado automaticamente - Não versionar
3. **Arquivos em `docs/`** são para referência e documentação
4. **Banco de dados** (`plans.db`) não deve ser versionado
5. **Uploads e exports** não devem ser versionados

---

## 🔄 Próximos Passos Recomendados

1. ✅ Estrutura organizada
2. ⏳ Criar `.gitignore` adequado (se necessário)
3. ⏳ Atualizar `README.md` com nova estrutura (se necessário)
4. ⏳ Configurar variáveis de ambiente para produção

---

**Última Atualização:** 2025-01-27

