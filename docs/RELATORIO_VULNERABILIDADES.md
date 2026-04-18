# 🔒 Relatório de Vulnerabilidades - ROCBYIP vf1

**Data da Análise:** 2025-02-11  
**Versão Analisada:** vf1  
**Status:** ⚠️ **VULNERABILIDADES IDENTIFICADAS**

---

## 📋 Resumo Executivo

Análise de segurança atualizada da aplicação ROCBYIP vf1. Várias correções foram implementadas desde o relatório anterior, mas **ainda existem vulnerabilidades que requerem atenção**:

- 🔴 **Críticas:** 1
- 🟠 **Alta:** 2
- 🟡 **Média:** 4
- 🟢 **Baixa:** 2

---

## ✅ Correções Já Implementadas (Relatório Anterior)

| # | Vulnerabilidade | Status |
|---|-----------------|--------|
| 1 | XSS em export HTML | ✅ Corrigido – `sanitize_html_text()` em todos os campos |
| 2 | API Key padrão insegura | ✅ Corrigido – Sem valor padrão, validação de força |
| 3 | CORS permissivo | ✅ Corrigido – Métodos e headers restritos |
| 4 | Path Traversal em upload | ✅ Corrigido – `sanitize_filename()` + `safe_path_join()` |
| 5 | Exposição em logs de auditoria | ✅ Corrigido – `sanitize_log_detail()` |
| 6 | Arquivos sem context manager | ✅ Corrigido – Uso de `with open()` |

---

## 🔴 VULNERABILIDADES CRÍTICAS

### 1. Path Traversal no Endpoint de Restauração de Backup

**Severidade:** 🔴 **CRÍTICA**  
**CVSS Score:** 8.1 (High)

**Descrição:**
O parâmetro `backup_filename` na rota `/backup/restore/{backup_filename}` é utilizado diretamente em `os.path.join()` sem validação, permitindo path traversal.

**Local Encontrado:**
- `backend/app/main.py` - Linhas 403-418

**Código Vulnerável:**
```python
@app.post("/backup/restore/{backup_filename}")
def restore_backup_endpoint(backup_filename: str, db: Session = Depends(get_db)):
    backup_path = os.path.join(BACKUP_DIR, backup_filename)  # VULNERÁVEL
```

**Exemplo de Exploração:**
```
POST /backup/restore/..%2F..%2F..%2Fetc%2Fpasswd
POST /backup/restore/plans_backup_20250101.db%2F..%2F..%2Fsensitive_file
```

**Impacto:**
- Leitura/escrita de arquivos arbitrários no sistema
- Possível substituição do banco de dados por arquivo malicioso
- Comprometimento total do servidor

**Recomendação:**
```python
# Usar sanitize_filename e validar que o arquivo existe em BACKUP_DIR
from security.security_utils import sanitize_filename, safe_path_join

@app.post("/backup/restore/{backup_filename}")
def restore_backup_endpoint(backup_filename: str, db: Session = Depends(get_db)):
    # Validar formato: apenas plans_backup_YYYYMMDD_HHMMSS.db
    import re
    if not re.match(r'^plans_backup_\d{8}_\d{6}\.db$', backup_filename):
        raise HTTPException(status_code=400, detail="Invalid backup filename format")
    
    try:
        backup_path = safe_path_join(BACKUP_DIR, backup_filename)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid backup filename")
    # ... resto do código
```

---

## 🟠 VULNERABILIDADES DE ALTA SEVERIDADE

### 2. Endpoints de Backup sem Rate Limiting

**Severidade:** 🟠 **ALTA**  
**CVSS Score:** 6.5 (Medium)

**Descrição:**
Os endpoints `/backup/create`, `/backup/restore/{filename}`, `/backup/list` e `/backup/stats` não possuem rate limiting, permitindo abuso.

**Locais Encontrados:**
- `backend/app/main.py` - Linhas 519-596

**Problemas Identificados:**
- ❌ `create_backup` – pode ser chamado repetidamente para DoS
- ❌ `restore_backup` – pode ser explorado para corrupção de dados
- ❌ `list_backups` – pode ser usado para enumerar backups
- ❌ `backup/stats` – sem restrição de taxa

**Impacto:**
- DoS através de criação excessiva de backups
- Sobrecarga do disco
- Enumeração de backups disponíveis

**Recomendação:**
```python
@app.post("/backup/create")
@limiter.limit("5/minute")
def create_backup_endpoint(request: Request, db: Session = Depends(get_db)):
    ...

@app.post("/backup/restore/{backup_filename}")
@limiter.limit("3/minute")
def restore_backup_endpoint(request: Request, backup_filename: str, db: Session = Depends(get_db)):
    ...

@app.get("/backup/list")
@limiter.limit("30/minute")
def list_backups_endpoint(request: Request, db: Session = Depends(get_db)):
    ...

@app.get("/backup/stats")
@limiter.limit("60/minute")
def backup_stats_endpoint(request: Request, db: Session = Depends(get_db)):
    ...
```

**Nota:** O decorador `@limiter.limit()` requer o parâmetro `request: Request` na assinatura da função.

---

### 3. Falta de Autenticação Específica para Backup

**Severidade:** 🟠 **ALTA**  
**CVSS Score:** 6.0 (Medium)

**Descrição:**
Quando `REQUIRE_API_KEY=false`, qualquer usuário pode criar, listar e restaurar backups. Operações de backup são críticas e deveriam ter proteção adicional.

**Recomendação:**
- Proteger endpoints de backup com autenticação obrigatória
- Ou criar variável `REQUIRE_API_KEY_FOR_BACKUP=true` para proteção extra
- Em produção, sempre exigir API key

---

## 🟡 VULNERABILIDADES DE MÉDIA SEVERIDADE

### 4. Schemas Pydantic sem Limites de Tamanho

**Severidade:** 🟡 **MÉDIA**  
**CVSS Score:** 5.3 (Medium)

**Descrição:**
Os schemas em `backend/app/schemas/schemas.py` não definem `max_length` para campos de texto, permitindo payloads arbitrariamente grandes.

**Locais Encontrados:**
- `backend/app/schemas/schemas.py` - Todos os modelos

**Exemplo:**
```python
# Atual - sem limite
class Subject(BaseModel):
    what: str
    who: str
    where: str

# Recomendado
class Subject(BaseModel):
    what: str = Field(..., max_length=1000)
    who: str = Field(..., max_length=1000)
    where: str = Field(..., max_length=1000)
```

**Impacto:**
- DoS através de payloads muito grandes
- Consumo excessivo de memória
- Possível degradação do banco SQLite

**Recomendação:**
- Adicionar `Field(..., max_length=N)` em todos os campos de string
- Limitar tamanho de listas com `Field(..., max_length=100)` para arrays

---

### 5. Diretório de Exports sem Limpeza

**Severidade:** 🟡 **MÉDIA**  
**CVSS Score:** 4.0 (Low)

**Descrição:**
Os arquivos PDF e HTML exportados são salvos em `exports/` com nomes previsíveis (`plan_{id}.pdf`, `plan_{id}.html`) e nunca são removidos.

**Locais Encontrados:**
- `backend/app/main.py` - Linhas 232-235, 246-250

**Impacto:**
- Preenchimento gradual do disco
- Possível DoS por esgotamento de espaço

**Recomendação:**
- Implementar política de retenção para exports
- Limpar arquivos antigos periodicamente
- Considerar geração em memória e streaming ao invés de gravar em disco

---

### 6. SQLite em Produção

**Severidade:** 🟡 **MÉDIA**  
**CVSS Score:** 5.0 (Medium)

**Descrição:**
Uso de SQLite com `check_same_thread=False` pode causar problemas de concorrência em ambientes com múltiplos workers.

**Local Encontrado:**
- `backend/app/db/database.py`

**Recomendação:**
- Migrar para PostgreSQL ou MySQL em produção
- Em SQLite, usar um único worker ou connection pooling adequado

---

### 7. Host 0.0.0.0 em Script de Execução

**Severidade:** 🟡 **MÉDIA**  
**CVSS Score:** 4.0 (Low)

**Descrição:**
O `run_local.sh` inicia o backend com `--host 0.0.0.0`, expondo a API em todas as interfaces de rede.

**Local Encontrado:**
- `run_local.sh` - Linha 57

**Recomendação:**
- Para desenvolvimento local: `--host 127.0.0.1`
- Documentar que para acesso em rede local deve-se usar 0.0.0.0 explicitamente
- Nunca usar 0.0.0.0 em ambientes de produção sem firewall adequado

---

## 🟢 VULNERABILIDADES DE BAIXA SEVERIDADE

### 8. MIME Type Spoofing em Upload

**Severidade:** 🟢 **BAIXA**  
**CVSS Score:** 3.0 (Low)

**Descrição:**
A validação de upload usa `file.content_type` que pode ser manipulado pelo cliente. A validação por extensão oferece alguma proteção, mas um arquivo `.pdf` poderia conter conteúdo malicioso.

**Mitigação Atual:**
- Validação por extensão
- Hash SHA-256 para integridade
- Sanitização de nomes de arquivo

**Recomendação:**
- Considerar validação de magic bytes (assinatura real do arquivo)
- Usar biblioteca como `python-magic` para verificação de tipo real

---

### 9. Documentação da API Exposta

**Severidade:** 🟢 **BAIXA**  
**CVSS Score:** 2.0 (Low)

**Descrição:**
O Swagger UI (`/docs`) e ReDoc estão disponíveis por padrão no FastAPI, expondo a estrutura completa da API.

**Recomendação:**
- Desabilitar em produção: `docs_url=None, redoc_url=None`
- Ou proteger com autenticação
- Ou configurar via variável de ambiente

---

## 📊 Resumo por Categoria

| Categoria | Quantidade | Severidade |
|-----------|------------|------------|
| Path Traversal | 1 | Crítica |
| Rate Limiting | 4 endpoints | Alta |
| Autenticação | 1 | Alta |
| Validação de Entrada | 1 | Média |
| Gerenciamento de Arquivos | 1 | Média |
| Configuração | 2 | Média/Baixa |

---

## 🎯 Plano de Ação Recomendado

### Fase 1: Imediato (Crítico)
1. **Corrigir Path Traversal no backup/restore** – Validar `backup_filename` com regex e usar `safe_path_join`
2. **Adicionar rate limiting nos endpoints de backup**

### Fase 2: Esta Semana (Alta)
3. Proteger endpoints de backup com autenticação em produção
4. Definir política de quando backup requer API key

### Fase 3: Próximas Semanas (Média)
5. Adicionar limites de tamanho nos schemas Pydantic
6. Implementar limpeza do diretório `exports/`
7. Revisar configuração de host para produção

### Fase 4: Melhorias (Baixa)
8. Considerar validação de magic bytes em uploads
9. Desabilitar ou proteger documentação da API em produção

---

## 📝 Checklist de Segurança Atualizado

- [x] Sanitização HTML em export
- [x] API key sem valor padrão inseguro
- [x] CORS configurado adequadamente
- [x] Path traversal prevenido em upload
- [x] Logs sanitizados
- [x] Context managers para arquivos
- [x] **Path traversal prevenido em backup/restore** ✅
- [x] **Rate limiting em endpoints de backup** ✅
- [x] **Autenticação para endpoints de backup** (REQUIRE_API_KEY_FOR_BACKUP)
- [x] Limites de tamanho em schemas ✅
- [x] Limpeza de exports ✅
- [x] Host seguro no run_local.sh (127.0.0.1) ✅
- [ ] Proteção de documentação em produção

---

## 📚 Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [CWE-307: Improper Restriction of Excessive Authentication Attempts](https://cwe.mitre.org/data/definitions/307.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Última Atualização:** 2025-02-11  
**Próxima Revisão Recomendada:** Após correção da vulnerabilidade crítica de path traversal
