# 📚 Índice de Documentação — ROC Planejamento de Inteligência v3

**Data:** 11 de Novembro de 2025  
**Versão:** 3.0 (MVP)

---

## 🗂️ Estrutura de Documentação

```
DOC ROOT
├── 📖 README.md ........................... Guia principal + início rápido
├── 👥 USER_GUIDE.md ...................... Guia do usuário final (13 etapas)
├── 🔧 TECHNICAL_DOCS.md .................. Referência técnica (Dev)
├── 📊 SYSTEM_REPORT.md ................... Análise completa do sistema
├── 💼 EXECUTIVE_SUMMARY.md ............... Sumário para executivos
├── 🏛️ ARCHITECTURE.md .................... Diagramas e arquitetura
├── 📚 DOCUMENTATION_INDEX.md ............ Este arquivo
└── ⚙️ Arquivos de configuração
    ├── Makefile
    ├── pytest.ini
    ├── requirements.txt (app)
    └── requirements.txt (backend)
```

---

## 📖 Qual Documento Devo Ler?

### 👤 **Sou usuário final**

**Leia em ordem:**
1. **[README.md](#readme)** — Visão geral (2 min)
2. **[USER_GUIDE.md](#user-guide)** — Guia passo-a-passo das 13 etapas (30 min)
3. **[FAQ no USER_GUIDE.md](#user-guide)** — Respostas comuns (5 min)

**Tempo total:** ~37 minutos

---

### 🔧 **Sou desenvolvedor/integrador**

**Leia em ordem:**
1. **[README.md](#readme)** — Setup inicial (5 min)
2. **[TECHNICAL_DOCS.md](#technical-docs)** — APIs e configuração (20 min)
3. **[ARCHITECTURE.md](#architecture)** — Fluxo de dados (15 min)
4. **[SYSTEM_REPORT.md](#system-report)** — Detalhes internos (30 min)

**Tempo total:** ~70 minutos

---

### 👔 **Sou gestor/arquiteto**

**Leia em ordem:**
1. **[EXECUTIVE_SUMMARY.md](#executive-summary)** — Visão geral (5 min)
2. **[SYSTEM_REPORT.md](#system-report)** — Capacidades (20 min)
3. **[ARCHITECTURE.md](#architecture)** — Escalabilidade (10 min)

**Tempo total:** ~35 minutos

---

### 🎯 **Quero deploy/DevOps**

**Leia:**
1. **[TECHNICAL_DOCS.md](#technical-docs)** — Seção "Configuração" (10 min)
2. **[ARCHITECTURE.md](#architecture)** — Checklist de Implementação (15 min)
3. **[README.md](#readme)** — Variáveis de ambiente (5 min)

**Tempo total:** ~30 minutos

---

## 📄 Descrição de Cada Documento

### <a name="readme"></a>📖 **README.md**

**Propósito:** Documentação principal e início rápido

**Contém:**
- ✅ Visão geral do projeto
- ✅ Características principais
- ✅ Instruções de início (passos 1-4)
- ✅ Estrutura do projeto
- ✅ Endpoints API (tabela)
- ✅ Metodologia de 10 fases
- ✅ Variáveis de ambiente
- ✅ Dependências

**Melhor para:** Primeira leitura, qualquer público

**Tempo de leitura:** 5-10 minutos

---

### <a name="user-guide"></a>👥 **USER_GUIDE.md**

**Propósito:** Guia completo para usuários finais

**Contém:**
- ✅ Visão geral simples
- ✅ Como começar (passo-a-passo)
- ✅ Entender a layout
- ✅ Tipos de controles (text, date, select, etc.)
- ✅ **Guia das 13 Etapas** (DETALHADO)
  - O que é cada etapa
  - Exemplos práticos
  - Quando usar
  - Impactos nas próximas etapas
- ✅ Funcionalidades avançadas
  - Validação LGPD
  - KPIs (Coverage, Linkage)
  - Gantt chart
  - Exportação
  - Upload de evidências
- ✅ FAQ (~10 perguntas)
- ✅ Boas práticas

**Melhor para:** Usuários finais, primeiro uso

**Tempo de leitura:** 30-45 minutos

---

### <a name="technical-docs"></a>🔧 **TECHNICAL_DOCS.md**

**Propósito:** Referência técnica para desenvolvedores

**Contém:**
- ✅ Stack tecnológico (versões)
- ✅ Instalação passo-a-passo
- ✅ Configuração de ambiente
- ✅ **API REST — Referência Completa**
  - 8 endpoints
  - Request/Response examples
  - Códigos HTTP
  - Headers
- ✅ Estrutura de código
  - Fluxo Frontend → Backend
  - Fluxo Backend (FastAPI)
  - Persistência (SQLite)
- ✅ Boas práticas
  - Segurança para produção
  - Logging
  - Validação
  - Tratamento de erros
  - Índices DB
- ✅ Troubleshooting (5 problemas comuns)
- ✅ Checklist de deploy
- ✅ Como contribuir

**Melhor para:** Desenvolvedores, DevOps

**Tempo de leitura:** 20-30 minutos

---

### <a name="system-report"></a>📊 **SYSTEM_REPORT.md**

**Propósito:** Análise técnica completa do sistema

**Contém:**
- ✅ Sumário executivo
- ✅ Arquitetura em 4 camadas
  - Apresentação (Streamlit)
  - Aplicação (FastAPI)
  - Dados (SQLite)
  - Serviços (audit, lgpd, pdf)
- ✅ Fluxo de dados (caso completo com diagrama)
- ✅ Segurança implementada (5 pontos)
- ✅ KPIs e métricas
- ✅ Gantt chart simplificado
- ✅ Estratégia de testes
- ✅ Performance e escalabilidade
- ✅ Deployment (3 opções)
- ✅ Problemas conhecidos e roadmap
- ✅ Estrutura de dados (exemplo JSON completo)

**Melhor para:** Arquitetos, tech leads, relatórios

**Tempo de leitura:** 30-45 minutos

---

### <a name="executive-summary"></a>💼 **EXECUTIVE_SUMMARY.md**

**Propósito:** Sumário executivo para decisores

**Contém:**
- ✅ O que é (simples)
- ✅ Principais características (tabela)
- ✅ Início rápido (para usuários)
- ✅ Arquitetura em 30 segundos
- ✅ O que cada etapa faz (tabela)
- ✅ Segurança (checklist)
- ✅ KPIs calculados
- ✅ O que é salvo
- ✅ Endpoints API (tabela)
- ✅ Estrutura de dados (JSON)
- ✅ Validações automáticas
- ✅ Fluxo de uso típico
- ✅ Próximos passos (roadmap)
- ✅ Estatísticas (linhas de código, etc.)
- ✅ Configuração mínima para produção
- ✅ ROI (return on investment)
- ✅ Conclusão

**Melhor para:** C-level, business stakeholders, decisores

**Tempo de leitura:** 5-10 minutos

---

### <a name="architecture"></a>🏛️ **ARCHITECTURE.md**

**Propósito:** Diagramas detalhados e checklist de implementação

**Contém:**
- ✅ Diagrama visual completo (ASCII art)
- ✅ Fluxo de dados — ciclo completo
- ✅ **Checklist de Implementação** por fase
  - Fase 1: Setup inicial
  - Fase 2: Backend (modelos, schemas, routes, services, security)
  - Fase 3: Frontend (interface, 13 etapas, funcionalidades)
  - Fase 4: Validação e testes
  - Fase 5: Documentação
  - Fase 6: Deployment
- ✅ Variáveis de ambiente (checklist)
- ✅ Status final (tabela)
- ✅ Próximas prioridades (v4)
- ✅ How to get started

**Melhor para:** Project managers, implementadores, verificação de status

**Tempo de leitura:** 15-25 minutos

---

## 🎯 Matriz de Referência Rápida

| Pergunta | Documento | Seção |
|----------|-----------|-------|
| **Como começo?** | README | Início Rápido |
| **Como uso cada etapa?** | USER_GUIDE | Guia das 13 Etapas |
| **Qual é a estrutura de dados?** | SYSTEM_REPORT | Estrutura de Dados |
| **Como integro via API?** | TECHNICAL_DOCS | API REST Completa |
| **Qual é a arquitetura?** | ARCHITECTURE | Diagrama de Arquitetura |
| **Qual é o valor do sistema?** | EXECUTIVE_SUMMARY | ROI |
| **Qual é o status do projeto?** | ARCHITECTURE | Checklist |
| **Como deploy em produção?** | TECHNICAL_DOCS | Seção Deployment |
| **Tenho um erro, o que fazer?** | TECHNICAL_DOCS | Troubleshooting |
| **Qual é a próxima versão?** | SYSTEM_REPORT | Roadmap |

---

## 🔍 Buscar por Tópico

### Segurança
- **README.md** → Seção "Segurança"
- **SYSTEM_REPORT.md** → Seção "Segurança Implementada"
- **TECHNICAL_DOCS.md** → Seção "Boas Práticas" (Configuração de Segurança)

### API REST
- **README.md** → Seção "API REST — Endpoints Principais"
- **TECHNICAL_DOCS.md** → Seção "API REST — Referência Completa" (detalhado)

### KPIs e Métricas
- **SYSTEM_REPORT.md** → Seção "KPIs e Métricas"
- **USER_GUIDE.md** → Seção "Cálculo de Cobertura" e "Ligação PIR-Coleta"

### Validação LGPD
- **USER_GUIDE.md** → Seção "Validação Automática (LGPD)"
- **SYSTEM_REPORT.md** → Seção "lgpd.py — Validação de Conformidade"

### Banco de Dados
- **SYSTEM_REPORT.md** → Seção "Persistência (SQLite)"
- **TECHNICAL_DOCS.md** → Seção "Estrutura de Código" (Persistência)

### Upload de Evidências
- **USER_GUIDE.md** → Seção "Upload de Evidências"
- **TECHNICAL_DOCS.md** → Endpoint `/evidence/upload`

### Exportação (PDF/HTML)
- **USER_GUIDE.md** → Seção "Exportação"
- **SYSTEM_REPORT.md** → Seção "pdf.py — Geração de Relatórios"
- **TECHNICAL_DOCS.md** → Endpoints `/export/pdf/{id}` e `/export/html/{id}`

### 13 Etapas
- **USER_GUIDE.md** → Seção "Guia das 13 Etapas" (PRINCIPAL)
- **README.md** → Seção "Metodologia — Planejamento de Inteligência (a→j)"

### Deployment
- **TECHNICAL_DOCS.md** → Seção "Deployment"
- **SYSTEM_REPORT.md** → Seção "Deployment"
- **ARCHITECTURE.md** → Seção "Fase 6: Deployment"

### Troubleshooting
- **TECHNICAL_DOCS.md** → Seção "Troubleshooting" (5 problemas comuns)
- **USER_GUIDE.md** → Seção "FAQ"

---

## 📊 Estatísticas de Documentação

| Métrica | Valor |
|---------|-------|
| **Documentos criados** | 6 |
| **Páginas totais** | ~150+ |
| **Palavras totais** | ~40.000+ |
| **Diagramas/tabelas** | 20+ |
| **Exemplos de código** | 15+ |
| **Checklists** | 5 |
| **FAQs** | 10+ |
| **Links internos** | 30+ |

---

## 🔄 Fluxo de Aprendizado Recomendado

### **Novato (0-2 horas)**
1. **EXECUTIVE_SUMMARY.md** (5 min) — Entender o que é
2. **README.md** (5 min) — Contexto geral
3. **USER_GUIDE.md - Etapas** (30 min) — Como usar
4. **Praticar no app** (30 min) — Criar um plano teste
5. **USER_GUIDE.md - FAQ** (5 min) — Dúvidas

### **Intermediário (2-6 horas)**
1. Completar "Novato"
2. **TECHNICAL_DOCS.md** (30 min) — APIs e configuração
3. **SYSTEM_REPORT.md - Sumário Executivo** (10 min) — Contexto
4. **SYSTEM_REPORT.md - Arquitetura** (20 min) — Como funciona
5. **Integrar com API externa** (1 hora) — Hands-on

### **Avançado (6-16 horas)**
1. Completar "Intermediário"
2. **SYSTEM_REPORT.md** (completo, 45 min)
3. **ARCHITECTURE.md** (completo, 25 min)
4. **TECHNICAL_DOCS.md** (completo, 30 min)
5. **Modificar código** (1+ hora) — Adicionar funcionalidade
6. **Deploy em staging** (2+ horas) — Integração com infra

---

## 📢 Convenções de Documentação

### Ícones Usados
- 📖 Documentação/guias
- 👥 Usuário final
- 🔧 Desenvolvedores
- 📊 Relatórios/análise
- 💼 Executivos/gestão
- 🏛️ Arquitetura
- ✅ Completo/implementado
- ⚠️ Parcial/recomendação
- 🎯 Objetivos
- 🚀 Deploy/produção

### Estrutura de Seções
- **O que é:** Definição simples
- **Contém:** Lista de tópicos
- **Melhor para:** Público-alvo
- **Tempo:** Estimativa de leitura

### Exemplos
```json
{
  "format": "json",
  "notes": "Quando há código, está em blocos dedicados"
}
```

### Tabelas
Sempre com headers claros e alinhamento

---

## 🔗 Navegar Entre Documentos

```
ENTRY POINT
    ├─ README.md
    │   ├─ USER_GUIDE.md (usuários finais)
    │   ├─ TECHNICAL_DOCS.md (devs)
    │   └─ SYSTEM_REPORT.md (aprofundado)
    │
    ├─ EXECUTIVE_SUMMARY.md (gestores)
    │   ├─ SYSTEM_REPORT.md (detalhes)
    │   └─ ARCHITECTURE.md (escalabilidade)
    │
    └─ ARCHITECTURE.md (arquitetos)
        └─ TECHNICAL_DOCS.md (implementação)
```

---

## ✏️ Como Contribuir com Documentação

Se encontrar erros ou ambiguidades:

1. Abra uma issue no GitHub
2. Especifique o documento e seção
3. Descreva a correção/melhoria
4. Envie um PR com a correção

---

## 📋 Versão e Histórico

| Versão | Data | Mudanças |
|--------|------|----------|
| 3.0 | 11/11/2025 | Documentação inicial completa |
| 2.0 | TBD | Melhorias futuras |
| 1.0 | TBD | MVP inicial |

---

## 🎓 Recursos Adicionais

### Documentação Externa
- **FastAPI:** https://fastapi.tiangolo.com
- **Streamlit:** https://docs.streamlit.io
- **SQLAlchemy:** https://docs.sqlalchemy.org
- **Pydantic:** https://docs.pydantic.dev

### Tutoriais Relacionados
- OSINT methodology (10 fases)
- RESTful API design
- Streamlit best practices
- SQLite optimization

---

## 🏁 Próximos Passos

1. **Escolha seu documento** na matriz acima
2. **Leia na ordem recomendada** para seu perfil
3. **Consulte a matriz de referência** para tópicos específicos
4. **Explore os links internos** para aprofundar
5. **Pratique** criando um plano no app
6. **Contribua** com melhorias na documentação

---

**Bem-vindo! Escolha seu caminho e comece a explorar! 🚀**

---

**Índice atualizado em:** 11/11/2025  
**Status:** Completo e pronto para uso
