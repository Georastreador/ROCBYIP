# 👥 Guia do Usuário — ROC Planejamento de Inteligência

**Versão:** 3.0  
**Data:** 11 de Novembro de 2025  
**Público:** Analistas, Gestores, Pesquisadores de OSINT

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Como Começar](#como-começar)
3. [Navegação pela Interface](#navegação-pela-interface)
4. [Guia das 13 Etapas](#guia-das-13-etapas)
5. [Funcionalidades Avançadas](#funcionalidades-avançadas)
6. [FAQ](#faq)

---

## Visão Geral

O **ROC Planejamento de Inteligência** é uma plataforma interativa para estruturar operações de OSINT seguindo a **metodologia científica de planejamento em 10 fases (a→j)**. 

### O que você vai conseguir fazer:

✅ **Criar planos estruturados** de inteligência  
✅ **Organizar aspectos essenciais** e requisitos  
✅ **Planejar coleta de dados** com PIRs  
✅ **Validar conformidade LGPD**  
✅ **Exportar relatórios** em PDF e HTML  
✅ **Anexar evidências** com hash automático  

---

## Como Começar

### Passo 1: Acessar a Aplicação

```
🌐 http://localhost:8501
```

Você verá a tela inicial com o título:
```
ROC Planejamento de Inteligência
```

### Passo 2: Entender a Layout

```
┌─────────────────────────────────────────────────────────────┐
│ ROC Planejamento de Inteligência                      🎯     │
├──────────────────┬──────────────────────────────────────────┤
│  ETAPAS          │                                          │
│  ═══════════════ │                                          │
│  Assunto         │     CONTEÚDO DINÂMICO                   │
│  Faixa de Tempo  │     (muda conforme etapa)              │
│  Usuário         │                                          │
│  Finalidade      │                                          │
│  Prazo           │                                          │
│  Aspectos...     │                                          │
│  PIRs & Coleta   │                                          │
│  Medidas...      │                                          │
│  Preview         │                                          │
│  Revisão & Export│                                          │
│                  │                                          │
└──────────────────┴──────────────────────────────────────────┘
```

**Sidebar (esquerda):** Clique em qualquer etapa para navegar  
**Painel Principal (direita):** Formulários e informações contextuais

---

## Navegação pela Interface

### Tipos de Controles

#### 1. **Text Input**
```
📝 Título do Plano
[___________________________________]
```
Digite o texto e pressione Enter ou Tab.

#### 2. **Text Area** (múltiplas linhas)
```
📝 Finalidade
[_______________________________________]
[_______________________________________]
[_______________________________________]
```
Clique e digite livremente. Tab para próximo campo.

#### 3. **Date Picker**
```
📅 Início: [2025-11-01]  ← Clique para abrir calendário
```
Selecione no calendário que aparecer.

#### 4. **Selectbox** (dropdown)
```
Nível de Profundidade:
[V Executivo        ▼]
```
Clique na seta para expandir opções.

#### 5. **Button**
```
┌─────────────────────┐
│ 🔘 Incluir em PIRs  │
└─────────────────────┘
```
Clique para executar ação.

#### 6. **List com Delete**
```
Itens:
- Item 1 ✖
- Item 2 ✖
- Item 3 ✖
```
Clique em **✖** para remover.

---

## Guia das 13 Etapas

### **ETAPA 1️⃣: ASSUNTO** (O quê? Quem? Onde?)

**Objetivo:** Definir o tema central da inteligência.

**Campos:**
- **Título do Plano:** Nome descritivo do projeto
  - Exemplo: `"Análise de Concorrência — Tech Startup X"`
  
- **O quê?** Tema/assunto específico
  - Exemplo: `"Estratégia de marketing digital"`
  
- **Quem?** Alvo ou sujeito
  - Exemplo: `"Empresa TechCorp Inc."`
  
- **Onde?** Localização/contexto geográfico
  - Exemplo: `"Brasil — Região Sudeste"`

**✅ Dica:** Seja específico. Quanto melhor definir o assunto, melhor será o plano.

---

### **ETAPA 2️⃣: FAIXA DE TEMPO**

**Objetivo:** Definir o período de análise e coleta.

**Campos:**
- **Início:** Data de começo do período
- **Fim:** Data de término

**Exemplo:**
```
Início: 01/11/2025
Fim:    30/11/2025
(1 mês de análise)
```

**ℹ️ Informação:** A faixa de tempo guia o escopo de dados a coletar (notícias, posts, documentos desse período).

---

### **ETAPA 3️⃣: USUÁRIO**

**Objetivo:** Caracterizar quem vai usar o conhecimento.

**Campos:**
- **Usuário Principal:** Nome/cargo de quem demanda
  - Exemplo: `"Gerente de Estratégia"`
  
- **Outros Usuários (opcional):** Equipes envolvidas
  - Exemplo: `"Equipe de Marketing, RH"`
  
- **Nível de Profundidade:** 
  - **Executivo:** Resumo, insights principais
  - **Gerencial:** Detalhes tático-operacionais
  - **Técnico:** Dados brutos, análises detalhadas
  
- **Nível de Sigilo:**
  - **Público:** Sem restrição
  - **Restrito:** Acesso limitado
  - **Confidencial:** Acesso muito restrito
  - **Secreto:** Máxima restrição

**Impacto:** O nível de profundidade define como as informações serão apresentadas. O sigilo afeta medidas de segurança obrigatórias.

---

### **ETAPA 4️⃣: FINALIDADE**

**Objetivo:** Explicar o propósito/objetivo do conhecimento.

**Exemplo:**
```
"Identificar oportunidades de parceria estratégica 
ou ameaças competitivas através da análise de 
estrutura organizacional, portfólio de produtos 
e relacionamentos comerciais da empresa X."
```

**✅ Dica:** Seja conciso mas informativo. Esse texto aparecerá em todos os relatórios.

---

### **ETAPA 5️⃣: PRAZO**

**Objetivo:** Estabelecer deadline e urgência.

**Campos:**
- **Data Limite:** Quando o conhecimento é necessário
- **Urgência:**
  - **Baixa:** Sem pressa (>30 dias)
  - **Média:** Normal (10-30 dias)
  - **Alta:** Rápido (2-10 dias)
  - **Crítica:** Muito urgente (<2 dias)

**Impacto:** Afeta o plano de coleta (SLA das tarefas).

---

### **ETAPA 6️⃣: ASPECTOS ESSENCIAIS**

**Objetivo:** Listar os elementos críticos do assunto.

**O que são:** Dimensões, características ou tópicos que **DEVEM** ser cobertos para entender o assunto.

**Exemplo (Análise de Empresa):**
- Estrutura organizacional
- Portfólio de produtos/serviços
- Parcerias comerciais
- Financeiro (receita, investimentos)
- Posicionamento no mercado

**Como adicionar:**
```
Adicionar item em Aspectos Essenciais: [Estrutura organizacional]
                                         [Incluir em Aspectos Essenciais]
```

**✅ Dica:** Pense como um pesquisador — quais são as variáveis fundamentais?

---

### **ETAPA 7️⃣: ASPECTOS CONHECIDOS**

**Objetivo:** Documentar o que **JÁ SABEMOS**.

**Exemplo:**
- Portfólio público no site
- Informações de contato publicamente disponíveis
- Matérias recentes em jornais

**Impacto:** Usado para calcular "Coverage" (% de cobertura de conhecimento).

**Fórmula:**
```
Coverage = (Conhecidos / Essenciais) × 100%
```

---

### **ETAPA 8️⃣: ASPECTOS A CONHECER**

**Objetivo:** Listar lacunas — o que **FALTA DESCOBRIR**.

**Exemplo:**
- Estrutura organizacional interna recente
- Clientes não-públicos
- Planos estratégicos futuros

**⚠️ Importante:** Deve derivar dos Aspectos Essenciais. Se um Essencial não está em "Conhecidos", deve estar em "A Conhecer".

**Relação:**
```
A Conhecer = Essenciais - Conhecidos
```

---

### **ETAPA 9️⃣: PIRs & COLETA**

**Objetivo:** Converter lacunas em requisitos de inteligência (PIRs) e planejar a coleta.

#### **Parte A: PIRs (Priority Intelligence Requirements)**

**O que é PIR?** Pergunta específica cuja resposta é necessária.

**Campos:**
- **Vincular ao Aspecto:** Qual aspecto a conhecer isso responde?
- **Pergunta:** Formule como pergunta clara
  - Exemplo: `"Qual é a estrutura organizacional atual da empresa?"`
- **Prioridade:** Importância relativa (baixa/média/alta/crítica)
- **Justificativa:** Por que essa pergunta é crítica

**Como adicionar:**
```
1. Selecione aspecto: "0 - Estrutura organizacional interna"
2. Digite pergunta: "Qual é a estrutura organizacional atual?"
3. Prioridade: [Alta ▼]
4. Justificativa: "Essencial para compreender liderança e divisões"
5. Clique: [Incluir PIR]
```

**✅ Resultado:** PIRs aparecem em lista numerada

#### **Parte B: Plano de Coleta**

**O que é coleta?** Tarefas práticas para responder aos PIRs.

**Campos:**
- **PIR de referência:** Qual PIR essa tarefa responde?
- **Fonte:** Onde buscar? (Google, LinkedIn, API, etc.)
- **Método:** Como buscar? (busca, scraping, entrevista, etc.)
- **Frequência:** 
  - Único: Uma só vez
  - Diário: Todo dia
  - Semanal: Uma vez por semana
  - Mensal: Uma vez por mês
- **Responsável:** Quem faz
- **SLA (horas):** Quanto tempo tem para fazer

**Exemplo:**
```
PIR #0: "Qual é a estrutura organizacional?"
├─ Fonte: LinkedIn
├─ Método: Scraping de perfis públicos
├─ Frequência: Único
├─ Owner: Analytics Team
└─ SLA: 24 horas
```

**Impacto:** Cria o "Gantt" que aparece em Preview.

---

### **🔟 ETAPA: MEDIDAS EXTRAORDINÁRIAS**

**Objetivo:** Ações fora do escopo normal de coleta pública.

**Exemplos:**
- Entrevista com ex-funcionários
- Contato direto com empresa
- Operação encoberta
- Análise de padrões de tráfego

**⚠️ Aviso:** Use com cautela e sempre respeitando leis e ética.

---

### **1️⃣1️⃣ ETAPA: MEDIDAS DE SEGURANÇA**

**Objetivo:** Como proteger o plano e os dados coletados?

**Exemplos:**
- Criptografia de transmissão
- Controle de acesso (RBAC)
- Trilha de auditoria
- Isolamento de sistemas
- NDA (Non-Disclosure Agreement)

**Impacto:** Verificada em validação LGPD. Obrigatória se sigilo ≥ "Restrito".

---

### **1️⃣2️⃣ ETAPA: PREVIEW**

**Objetivo:** Visualizar plano completo com métricas.

**Informações exibidas:**

#### **Seção 1: Identificação**
- Título, Assunto, Faixa de Tempo
- Usuário, Finalidade, Prazo

#### **Seção 2: Estrutura Analítica**
- Aspectos (Essenciais, Conhecidos, A Conhecer)
- PIRs e Coleta
- Medidas (Extraordinárias, Segurança)

#### **Seção 3: KPIs**
```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐
│ Essencs  │ │ Conhecid │ │ A Conhe  │ │  PIRs    │ │ Tarefas Coleta │
│    5     │ │    3     │ │    2     │ │    6     │ │       4        │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────────────┘

Coverage: 60% (Conhecidos / Essenciais)
Linkage:  67% (Tarefas / PIRs)
```

**O que significa:**
- **Coverage 60%:** Temos 60% do conhecimento necessário
- **Linkage 67%:** 67% dos PIRs têm tarefas de coleta planejadas

#### **Seção 4: Gantt (Cronograma)**
```
| Tarefa              | Início     | Fim        |
|---------------------|------------|------------|
| PIR0 - Google       | 01/11/2025 | 02/11/2025 |
| PIR1 - LinkedIn     | 31/10/2025 | 02/11/2025 |
```

---

### **1️⃣3️⃣ ETAPA: REVISÃO & EXPORT**

**Objetivo:** Salvar, validar e exportar o plano.

#### **Seção 1: Visualização JSON**
- Mostra plano em formato JSON (para devs)

#### **Seção 2: Botões de Ação**

**Botão 1: Salvar Plano (API)**
```
┌─────────────────────────────┐
│ Salvar Plano (API)          │
└─────────────────────────────┘
↓
"Plano salvo: id 1" ✅
```
Persiste no banco de dados. Necessário antes de outras ações.

**Botão 2: Checar LGPD (API)**
```
┌──────────────────────┐
│ Checar LGPD (API)    │
└──────────────────────┘
↓
{
  "ok": true,
  "issues": []
}
```
Valida conformidade com regulações.

**Botão 3: Exportar PDF (API)**
```
┌──────────────────────┐
│ Exportar PDF (API)   │
└──────────────────────┘
↓
"PDF gerado: exports/plan_1.pdf" ✅
```
Gera relatório estilizado em PDF.

**Botão 4: Exportar HTML (API)**
```
┌──────────────────────┐
│ Exportar HTML (API)  │
└──────────────────────┘
↓
"HTML gerado: exports/plan_1.html" ✅
```
Gera relatório em HTML (pode abrir no navegador).

#### **Seção 3: Upload de Evidências**
```
Escolher arquivo: [_____________] [Browse]
                                   [Anexar]
↓
"Evidência anexada: photo.jpg (sha256: abc123...)" ✅
```
Anexa comprovantes (screenshots, documentos, etc.) com hash automático.

---

## Funcionalidades Avançadas

### 🔍 Validação Automática (LGPD)

Ao clicar "Checar LGPD", o sistema valida:

**Regra 1: Sigilo ↔ Segurança**
```
Se sigilo ∈ {restrito, confidencial, secreto}
  ENTÃO security[] DEVE estar preenchido
  E DEVE incluir ≥1 de:
    - controle de acesso
    - criptografia
    - trilha de auditoria
```

**Regra 2: Faixa de Tempo Válida**
```
time_window.start ≤ time_window.end
```

**Regra 3: Aspectos Coerentes**
```
Se aspects_essential[] ≠ ∅
  ENTÃO aspects_to_know[] ≠ ∅
```

**Exemplo — Validação com erro:**
```json
{
  "ok": false,
  "issues": [
    "Plano com sigilo elevado requer medidas de segurança definidas.",
    "Inclua medidas de: controle de acesso, criptografia ou trilha de auditoria."
  ]
}
```

---

### 📊 Cálculo de Cobertura (Coverage)

```
Coverage (%) = (Aspectos Conhecidos / Aspectos Essenciais) × 100
```

**Interpretação:**
- **0-25%:** Falta muita pesquisa
- **25-50%:** Cobertura parcial
- **50-75%:** Cobertura moderada ✅
- **75-100%:** Cobertura completa ou quase

---

### 🔗 Ligação PIR-Coleta (Linkage)

```
Linkage (%) = (Tarefas de Coleta / PIRs) × 100
```

**Interpretação:**
- **<50%:** Alguns PIRs sem plano de coleta
- **50-100%:** Todos os PIRs cobertos ✅

---

### 💾 Exportação

#### **PDF**
- Formatado e pronto para imprimir
- Inclui logotipo (se configurado)
- Salvo em: `backend/exports/plan_{id}.pdf`

#### **HTML**
- Abrir no navegador
- Copiar/colar em documentos
- Salvo em: `backend/exports/plan_{id}.html`

---

### 🔐 Upload de Evidências

**Como funciona:**
1. Clique em "Escolher arquivo"
2. Selecione arquivo (imagem, PDF, etc.)
3. Clique em "Anexar"
4. Sistema calcula **SHA-256** automaticamente
5. Arquivo armazenado com hash

**Verificação de integridade:**
```bash
# Depois, verify usando:
sha256sum arquivo.jpg
# Compare com sha256 salvo no sistema
```

---

## FAQ

### ❓ P: Como começo um novo plano?
**R:** Simplesmente navegue a etapa "Assunto" (primeira do sidebar) e preencha. O session_state cria automaticamente.

### ❓ P: Posso editar um plano já salvo?
**R:** Atualmente, o MVP salva como versão nova. Para editar, seria necessário implementar PUT/PATCH (roadmap v4).

### ❓ P: Meu plano tem muitos dados — por que o PDF fica lento?
**R:** O sistema gera PDF na memória. Para planos >10MB, use a versão HTML (mais rápida).

### ❓ P: Perdi meus dados — há backup?
**R:** Backend salva em SQLite (`app.db`). Faça backup regular de `backend/app.db`.

### ❓ P: Como habilito a segurança com API Key?
**R:** Variável de ambiente: `REQUIRE_API_KEY=true` e `API_KEY=sua_chave`.

### ❓ P: Quantos planos consigo criar?
**R:** Ilimitado (limitado apenas pelo espaço em disco SQLite). Para escala, migrar para PostgreSQL.

### ❓ P: Posso colaborar com outros usuários no mesmo plano?
**R:** MVP v3 não tem colaboração em tempo real. Roadmap v4 inclui isso.

### ❓ P: Qual é a melhor prática para PIRs?
**R:** 
- Formule como **perguntas claras e específicas**
- Uma pergunta = um PIR
- Vincule a um Aspecto a Conhecer
- Defina prioridade realista

### ❓ P: Como garantir conformidade LGPD?
**R:** Use "Checar LGPD" regularmente. Defina medidas de segurança se sigilo alto.

### ❓ P: Posso exportar em Excel?
**R:** Não em v3 (HTML/PDF). Roadmap v4 inclui .xlsx.

---

## 🎓 Boas Práticas

### 1. Planejamento Estruturado
- Preencha todas as 13 etapas
- Não pule seções
- Use Preview para validar antes de salvar

### 2. Nomenclatura Consistente
- Títulos descritivos
- Nomes únicos para planos
- Evite caracteres especiais em nomes

### 3. Qualidade de PIRs
- 1 pergunta = 1 PIR
- Máximo 20-30 PIRs por plano
- Prioridades realistas

### 4. Gestão de Tarefas
- 1 tarefa de coleta por PIR
- SLA realista (24-48h padrão)
- Owner claramente definido

### 5. Segurança
- Sempre defina medidas se sigilo alto
- Revisar em "Checar LGPD"
- Backup regular de planos

---

## 📞 Suporte

**Dúvidas?**
- Consulte **README.md** para visão técnica
- Consulte **SYSTEM_REPORT.md** para arquitetura
- Consulte **TECHNICAL_DOCS.md** para API

---

**Bem-vindo ao ROC Planejamento de Inteligência! 🚀**
