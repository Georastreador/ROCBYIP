# 🔍 4 Problemas Identificados no streamlit_app.py

**Data da Análise:** 2025-01-27  
**Arquivo Analisado:** `app/streamlit_app.py`  
**Status:** ⚠️ **PROBLEMAS IDENTIFICADOS**

---

## 📋 Resumo Executivo

Foram identificados **4 problemas** no arquivo `streamlit_app.py` que precisam ser corrigidos:

1. 🔴 **Uso de `datetime.utcnow()` deprecated** (linha 389)
2. 🟠 **Tratamento de erros muito genérico** (linhas 163, 388, 544, 552)
3. 🟡 **Falta de validação de tamanho de entrada** (múltiplos campos)
4. 🟡 **Falta de sanitização de dados antes de enviar para API** (linha 419)

---

## 🔴 PROBLEMA 1: Uso de `datetime.utcnow()` Deprecated

**Severidade:** 🔴 **ALTA**  
**Localização:** Linha 389

**Descrição:**
O código usa `datetime.utcnow()` que foi deprecado no Python 3.12+. Esta função será removida em versões futuras do Python.

**Código Problemático:**
```python
# Linha 387-389
try:
    dl = datetime.fromisoformat(plan["deadline"].get("date") or "")
except Exception:
    dl = datetime.utcnow()  # ❌ DEPRECATED
```

**Problema:**
- `datetime.utcnow()` está deprecated desde Python 3.12
- Pode causar warnings ou erros em versões futuras
- Não é timezone-aware

**Solução Recomendada:**
```python
from datetime import datetime, timezone, timedelta

try:
    dl = datetime.fromisoformat(plan["deadline"].get("date") or "")
except (ValueError, TypeError):
    dl = datetime.now(timezone.utc)  # ✅ CORRETO
```

**Impacto:**
- ✅ Compatibilidade com Python 3.12+
- ✅ Timezone-aware (mais preciso)
- ✅ Especifica tipos de exceção

---

## 🟠 PROBLEMA 2: Tratamento de Erros Muito Genérico

**Severidade:** 🟠 **MÉDIA-ALTA**  
**Localização:** Linhas 163, 388, 544, 552

**Descrição:**
O código usa `except Exception` de forma muito genérica, capturando todos os tipos de erro sem distinção. Isso pode mascarar erros importantes e dificultar o debugging.

**Código Problemático:**
```python
# Linha 163
try:
    img = Image.open(ASSETS_DIR / "faixa_tempo.png")
    st.image(img, caption="...", use_column_width=True)
except Exception as e:  # ❌ MUITO GENÉRICO
    st.warning(f"Não foi possível carregar a imagem: {e}")

# Linha 388
try:
    dl = datetime.fromisoformat(plan["deadline"].get("date") or "")
except Exception:  # ❌ MUITO GENÉRICO
    dl = datetime.utcnow()

# Linhas 544, 552 - Similar
```

**Problema:**
- Captura TODOS os tipos de exceção
- Pode mascarar erros críticos (KeyboardInterrupt, SystemExit)
- Dificulta identificação da causa raiz do erro
- Mensagens de erro podem expor informações sensíveis

**Solução Recomendada:**
```python
# Para carregamento de imagens
try:
    img = Image.open(ASSETS_DIR / "faixa_tempo.png")
    st.image(img, caption="...", use_column_width=True)
except (FileNotFoundError, IOError, OSError) as e:
    st.warning(f"Não foi possível carregar a imagem: {e}")
except Exception as e:
    # Log erro inesperado mas não quebra a aplicação
    st.warning("Erro ao carregar imagem. Verifique os logs.")
    # Log detalhado para debugging (não mostrar ao usuário)

# Para parsing de data
try:
    dl = datetime.fromisoformat(plan["deadline"].get("date") or "")
except (ValueError, TypeError):
    dl = datetime.now(timezone.utc)
```

**Impacto:**
- ✅ Tratamento específico por tipo de erro
- ✅ Melhor debugging
- ✅ Não mascara erros críticos
- ✅ Mensagens de erro mais informativas

---

## 🟡 PROBLEMA 3: Falta de Validação de Tamanho de Entrada

**Severidade:** 🟡 **MÉDIA**  
**Localização:** Múltiplos campos de entrada (linhas 73, 94, 97, 99, 101, 168, 169, 188, 286, 288, 305, 306, 308)

**Descrição:**
Os campos de entrada (`st.text_input`, `st.text_area`) não têm limites de tamanho máximo, permitindo que usuários insiram dados excessivamente grandes que podem:
- Causar problemas de performance
- Consumir memória excessiva
- Causar erros ao enviar para API
- Potencialmente causar DoS

**Código Problemático:**
```python
# Linha 94
plan["title"] = st.text_input("Título do Plano", plan["title"] or "Plano de Inteligência")
# ❌ Sem limite de tamanho

# Linha 188
plan["purpose"] = st.text_area("Finalidade", plan["purpose"], height=150)
# ❌ Sem limite de tamanho (max_chars)

# Linha 286
q = st.text_input("Pergunta (PIR)")
# ❌ Sem limite de tamanho
```

**Problema:**
- Campos podem receber dados muito grandes
- Sem validação antes de enviar para API
- Pode causar erros 413 (Payload Too Large) na API
- Risco de DoS através de entrada excessiva

**Solução Recomendada:**
```python
# Definir constantes de limite
MAX_TITLE_LENGTH = 200
MAX_TEXT_LENGTH = 5000
MAX_PIR_QUESTION_LENGTH = 500

# Aplicar limites
plan["title"] = st.text_input(
    "Título do Plano", 
    plan["title"] or "Plano de Inteligência",
    max_chars=MAX_TITLE_LENGTH
)

plan["purpose"] = st.text_area(
    "Finalidade", 
    plan["purpose"], 
    height=150,
    max_chars=MAX_TEXT_LENGTH
)

q = st.text_input(
    "Pergunta (PIR)",
    max_chars=MAX_PIR_QUESTION_LENGTH
)

# Validação adicional antes de enviar
if len(plan["title"]) > MAX_TITLE_LENGTH:
    st.error(f"Título muito longo. Máximo: {MAX_TITLE_LENGTH} caracteres")
    st.stop()
```

**Impacto:**
- ✅ Previne entrada excessiva
- ✅ Melhor performance
- ✅ Evita erros na API
- ✅ Melhor experiência do usuário

---

## 🟡 PROBLEMA 4: Falta de Sanitização de Dados Antes de Enviar para API

**Severidade:** 🟡 **MÉDIA**  
**Localização:** Linha 419 (e outras chamadas de API)

**Descrição:**
Os dados do plano são enviados diretamente para a API sem sanitização prévia. Embora o backend tenha validação, é uma boa prática sanitizar no frontend também para:
- Prevenir caracteres problemáticos
- Melhorar segurança
- Evitar erros de serialização JSON
- Garantir consistência dos dados

**Código Problemático:**
```python
# Linha 419
r = client.post(f"{API_URL}/plans", json=plan)
# ❌ Dados enviados sem sanitização

# Linha 525
files = {"file": (up.name, up.getvalue())}
data = {"plan_id": str(saved["id"])}
r = client.post(f"{API_URL}/evidence/upload", files=files, data=data)
# ❌ Nome do arquivo pode conter caracteres problemáticos
```

**Problema:**
- Dados podem conter caracteres de controle
- Strings podem ter encoding inconsistente
- Nomes de arquivo podem conter caracteres especiais
- Pode causar erros de serialização JSON

**Solução Recomendada:**
```python
import json
from html import escape

def sanitize_string(value, max_length=None):
    """Sanitiza string removendo caracteres de controle"""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    
    # Converter para string e remover caracteres de controle
    text = str(value)
    # Remover caracteres de controle (exceto \n, \r, \t)
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Limitar tamanho se especificado
    if max_length:
        text = text[:max_length]
    
    return text.strip()

def sanitize_plan_data(plan):
    """Sanitiza todos os dados do plano antes de enviar"""
    sanitized = {}
    
    # Sanitizar campos de texto
    sanitized["title"] = sanitize_string(plan.get("title"), MAX_TITLE_LENGTH)
    sanitized["purpose"] = sanitize_string(plan.get("purpose"), MAX_TEXT_LENGTH)
    
    # Sanitizar subject
    sanitized["subject"] = {
        "what": sanitize_string(plan.get("subject", {}).get("what")),
        "who": sanitize_string(plan.get("subject", {}).get("who")),
        "where": sanitize_string(plan.get("subject", {}).get("where"))
    }
    
    # Sanitizar arrays de strings
    sanitized["aspects_essential"] = [
        sanitize_string(item) for item in plan.get("aspects_essential", [])
    ]
    sanitized["aspects_known"] = [
        sanitize_string(item) for item in plan.get("aspects_known", [])
    ]
    sanitized["aspects_to_know"] = [
        sanitize_string(item) for item in plan.get("aspects_to_know", [])
    ]
    
    # Manter outros campos (datas, números, etc.)
    sanitized["time_window"] = plan.get("time_window", {})
    sanitized["user"] = plan.get("user", {})
    sanitized["deadline"] = plan.get("deadline", {})
    sanitized["pirs"] = plan.get("pirs", [])
    sanitized["collection"] = plan.get("collection", [])
    sanitized["extraordinary"] = [
        sanitize_string(item) for item in plan.get("extraordinary", [])
    ]
    sanitized["security"] = [
        sanitize_string(item) for item in plan.get("security", [])
    ]
    
    return sanitized

# Usar antes de enviar
sanitized_plan = sanitize_plan_data(plan)
r = client.post(f"{API_URL}/plans", json=sanitized_plan)

# Para nomes de arquivo
import os
safe_filename = os.path.basename(up.name) if up.name else "file"
# Remover caracteres problemáticos
safe_filename = sanitize_string(safe_filename)
files = {"file": (safe_filename, up.getvalue())}
```

**Impacto:**
- ✅ Dados consistentes
- ✅ Previne erros de serialização
- ✅ Melhor segurança
- ✅ Compatibilidade com API

---

## 📊 Resumo por Severidade

| Problema | Severidade | Prioridade | Impacto |
|----------|------------|------------|---------|
| 1. `datetime.utcnow()` deprecated | 🔴 Alta | Alta | Compatibilidade futura |
| 2. Tratamento de erros genérico | 🟠 Média-Alta | Média-Alta | Debugging e segurança |
| 3. Falta de validação de tamanho | 🟡 Média | Média | Performance e segurança |
| 4. Falta de sanitização | 🟡 Média | Média | Segurança e consistência |

---

## 🎯 Plano de Ação Recomendado

### Fase 1: Correções Críticas (Imediato)
1. ✅ Corrigir uso de `datetime.utcnow()` → `datetime.now(timezone.utc)`
2. ✅ Especificar tipos de exceção em `except` clauses

### Fase 2: Melhorias de Segurança (Esta Semana)
3. ✅ Adicionar limites `max_chars` em campos de entrada
4. ✅ Implementar função de sanitização de dados

---

## 📝 Checklist de Correções

- [ ] Problema 1: Substituir `datetime.utcnow()` por `datetime.now(timezone.utc)`
- [ ] Problema 2: Especificar tipos de exceção em todos os `except` clauses
- [ ] Problema 3: Adicionar `max_chars` em todos os campos de texto
- [ ] Problema 4: Implementar função `sanitize_plan_data()` e usar antes de enviar para API
- [ ] Testar todas as correções
- [ ] Verificar que não há regressões

---

## 🔗 Referências

- [Python datetime.utcnow() deprecation](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow)
- [Streamlit text_input max_chars](https://docs.streamlit.io/library/api-reference/widgets/st.text_input)
- [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

---

**Última Atualização:** 2025-01-27  
**Próxima Revisão:** Após implementação das correções

