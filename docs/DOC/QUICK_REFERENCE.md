# ⚡ Guia de Referência Rápida — ROC Planejamento v3

**Use este guia para encontrar rapidamente o que você precisa!**

---

## 🚀 Início Rápido (2 minutos)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd app
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Acessar
- **Aplicação:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

---

## 📚 Encontrar Documentação

### "Quero entender o que é"
→ Leia **EXECUTIVE_SUMMARY.md** (5 min)

### "Quero começar a usar"
→ Leia **USER_GUIDE.md** (30 min)

### "Tenho uma dúvida sobre as 13 etapas"
→ Consulte **USER_GUIDE.md** — Seção "Guia das 13 Etapas"

### "Preciso integrar via API"
→ Leia **TECHNICAL_DOCS.md** — Seção "API REST"

### "Quero entender a arquitetura"
→ Leia **SYSTEM_REPORT.md** ou **ARCHITECTURE.md**

### "Tenho um erro"
→ Consulte **TECHNICAL_DOCS.md** — Seção "Troubleshooting"

### "Vou fazer deploy"
→ Leia **TECHNICAL_DOCS.md** — Seção "Deployment"

---

## 🔍 Buscar Rápido

| Tópico | Documento | Seção |
|--------|-----------|-------|
| 13 Etapas | USER_GUIDE | "Guia das 13 Etapas" |
| API REST | TECHNICAL_DOCS | "API REST — Referência" |
| Segurança | SYSTEM_REPORT | "Segurança Implementada" |
| LGPD | USER_GUIDE | "Validação Automática" |
| KPIs | SYSTEM_REPORT | "KPIs e Métricas" |
| Banco de dados | SYSTEM_REPORT | "Persistência (SQLite)" |
| Deployment | TECHNICAL_DOCS | "Deployment" |
| Upload | USER_GUIDE | "Upload de Evidências" |
| Exportação | USER_GUIDE | "Exportação" |
| FAQ | USER_GUIDE | "FAQ" |

---

## 💡 Respostas Rápidas

### Como criar um plano?
1. Acesse http://localhost:8501
2. Preencha as 13 etapas (esquerda)
3. Clique em "Salvar Plano (API)"

### Como exportar PDF?
1. Salve o plano primeiro
2. Clique "Exportar PDF (API)"
3. Arquivo aparece em `backend/exports/plan_X.pdf`

### Como fazer upload de evidências?
1. Plano deve estar salvo
2. Na aba "Revisão & Export", role para baixo
3. Escolha arquivo e clique "Anexar"

### Como chamar a API?
```bash
curl -X POST http://localhost:8000/plans \
  -H "Content-Type: application/json" \
  -d '{"title":"...", "subject":{...}, ...}'
```

### Como validar LGPD?
1. Salve o plano
2. Clique "Checar LGPD (API)"
3. Veja os problemas (se houver)

### Como habilitar API Key?
```bash
export REQUIRE_API_KEY=true
export API_KEY=sua_chave_secreta
```
Depois inclua em requisições:
```
Header: X-API-Key: sua_chave_secreta
```

---

## 📊 8 Endpoints da API

```
GET  /health
POST /plans
GET  /plans
GET  /plans/{id}
POST /plans/{id}/lgpd_check
GET  /export/pdf/{id}
GET  /export/html/{id}
POST /evidence/upload
```

Documentação interativa: http://localhost:8000/docs

---

## 🛠 Variáveis de Ambiente

```bash
# Backend
API_KEY=seu_token
REQUIRE_API_KEY=true
REPORT_LOGO_PATH=/caminho/logo.png

# Frontend
API_URL=http://localhost:8000
```

---

## ❌ Problemas Comuns

### "Connection refused"
```bash
# Backend não está rodando
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### "ModuleNotFoundError"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Mude a porta
uvicorn app.main:app --port 8001
streamlit run app.py --server.port 8502
```

### "Database locked"
```bash
# Feche outras conexões ou use:
export SQLITE_TMPDIR=/tmp
```

---

## 📖 Estrutura dos Documentos

```
COMPLETION_SUMMARY.md ........... Resumo da análise (este documento)
DOCUMENTATION_INDEX.md .......... Índice de navegação
README.md ....................... Documentação principal (★ LEIA PRIMEIRO)
USER_GUIDE.md ................... Guia do usuário
TECHNICAL_DOCS.md .............. Referência técnica
SYSTEM_REPORT.md ............... Análise completa
EXECUTIVE_SUMMARY.md ........... Sumário para executivos
ARCHITECTURE.md ................ Diagramas e checklist
```

---

## ⚙️ Configuração Básica

### 1. Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r app/requirements.txt
```

### 2. Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend
```bash
cd app
streamlit run streamlit_app.py
```

### 4. Teste
```bash
curl http://localhost:8000/health
# Retorna: {"status": "ok"}
```

---

## 🎯 As 13 Etapas (Resumidas)

| # | Etapa | O Que Fazer |
|---|-------|-----------|
| 1 | Assunto | Defina título, O quê?, Quem?, Onde? |
| 2 | Tempo | Data início e fim |
| 3 | Usuário | Usuário, profundidade, sigilo |
| 4 | Finalidade | Objetivo do conhecimento |
| 5 | Prazo | Data limite + urgência |
| 6 | Essenciais | Aspectos críticos |
| 7 | Conhecidos | O que já sabemos |
| 8 | A Conhecer | O que falta descobrir |
| 9 | PIRs & Coleta | Requisitos + plano |
| 10 | Extraordinárias | Ações especiais |
| 11 | Segurança | Proteção de dados |
| 12 | Preview | KPIs + Gantt |
| 13 | Export | Salvar + exportar |

---

## 🔐 Segurança em 30 Segundos

- ✅ API Key: `REQUIRE_API_KEY=true`
- ✅ LGPD: Automaticamente validado
- ✅ Auditoria: Todas as ações registradas
- ✅ Hash: SHA-256 para evidências

---

## 📈 KPIs

```
Coverage = (Conhecidos / Essenciais) × 100%
Linkage = (Tarefas de Coleta / PIRs) × 100%
```

Exemplo: Coverage 60% = 60% do conhecimento já disponível

---

## 🔗 Estrutura de Dados

**Plan:**
```json
{
  "id": 1,
  "title": "...",
  "subject": {"what": "...", "who": "...", "where": "..."},
  "user": {"principal": "...", "depth": "...", "secrecy": "..."},
  "pirs": [{...}],
  "collection": [{...}],
  "evidences": [{...}]
}
```

---

## ✅ Checklist Pré-Produção

- [ ] Todos os testes passam
- [ ] Documentação revisada
- [ ] LGPD validado
- [ ] Backup configurado
- [ ] API Key ativada
- [ ] HTTPS habilitado
- [ ] Rate limiting ativo
- [ ] Logs centralizados

---

## 📞 Suporte Rápido

| Pergunta | Resposta |
|----------|----------|
| URL da app? | http://localhost:8501 |
| URL da API? | http://localhost:8000 |
| Docs da API? | http://localhost:8000/docs |
| Onde salva planos? | Backend (SQLite app.db) |
| Onde salva PDFs? | backend/exports/ |
| Onde salva evidências? | backend/uploads/ |
| Como ver logs? | SYSTEM_REPORT.md |

---

## 🚀 Deploy

### Desenvolvimento (Agora)
- SQLite local
- Localhost

### Staging (Próx)
- PostgreSQL
- Docker

### Produção (Depois)
- PostgreSQL + Backups
- Kubernetes
- HTTPS + API Key

---

## 📚 Leitura Recomendada

**5 minutos:**
- EXECUTIVE_SUMMARY.md

**30 minutos:**
- README.md
- USER_GUIDE.md (Etapas 1-5)

**1 hora:**
- USER_GUIDE.md (completo)
- TECHNICAL_DOCS.md (API)

**2 horas:**
- SYSTEM_REPORT.md
- ARCHITECTURE.md

---

## 🎓 Aprenda Mais

```
Iniciante → README → USER_GUIDE → Praticar
↓
Intermediário → TECHNICAL_DOCS → Integrar
↓
Avançado → SYSTEM_REPORT + ARCHITECTURE → Deploy
```

---

## 🔄 Workflow Típico

```
1. Acesse http://localhost:8501
2. Preencha 13 etapas (10-15 min)
3. Visualize Preview (KPIs + Gantt)
4. Valide LGPD
5. Exporte PDF/HTML
6. Upload evidências (opcional)
✅ Plano finalizado!
```

---

## 💡 Dicas Pro

- Use Preview regularmente para validar
- Sempre cheque LGPD antes de finalizar
- Nomeie planos descritivamente
- Faça backup da app.db regularmente
- Revise PIRs 3x (qualidade > quantidade)

---

## 🎯 Próximas Versões

**v4 (Roadmap):**
- OAuth2
- Edição de planos
- Dashboard
- Colaboração em tempo real
- IA para sugestões

---

**Não sabe por onde começar?**
1. Acesse **DOCUMENTATION_INDEX.md**
2. Escolha seu perfil
3. Siga os documentos recomendados

**Boa sorte! 🚀**

---

**Última atualização:** 11/11/2025
