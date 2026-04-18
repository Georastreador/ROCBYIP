# RELATÓRIO DA APLICAÇÃO — ROC Planejamento de Inteligência (MVP v3)

**Resumo Executivo**

- **Objetivo**: Apresentar funcionalidades, vantagens e estimativa de ROI da solução `ROC Planejamento de Inteligência`.
- **Escopo**: Frontend em Streamlit (`app/streamlit_app.py`), backend em FastAPI (`backend/app/main.py`), persistência em SQLite (`backend/app.db`), geração de relatórios PDF/HTML e auditoria.

**Funcionalidades**

- **Interface**: `app/streamlit_app.py` — formulário guiado com 13 etapas do planejamento de inteligência.
- **Criação de Planos**: `POST /plans` — coleta de Assunto, Faixa de Tempo, Usuário, Finalidade, Prazo e demais seções (PIRs, Coleta, Medidas).
- **Persistência**: Banco SQLite para planos, evidências e logs de auditoria.
- **Validação LGPD**: `POST /plans/{plan_id}/lgpd_check` — checagens automáticas de sigilo, faixa de tempo e medidas de mitigação.
- **Gestão de Evidências**: Upload com cálculo de SHA-256 e vínculo ao plano.
- **Exportação**: `GET /export/pdf/{plan_id}` e `GET /export/html/{plan_id}` — geração e download direto de relatórios com template e logotipo.
- **Auditoria**: `audit_logs` registrando ator, timestamp, ação, detalhe e plan_id.
- **Automação para Usuário**: Scripts one‑click (`run_app.command`, `run_app.bat`) para iniciar backend e frontend sem necessidade técnica.
- **Testes & Utilitários**: Suporte a testes (`tests/`), `Makefile`, `pytest.ini`.

**Vantagens de Utilizar a Ferramenta**

- **Padronização**: Todos os planos seguem a metodologia das 10 fases, reduzindo variabilidade e erros.
- **Produtividade**: Formulários guiados e export automático diminuem tempo de elaboração e consolidação do relatório.
- **Rastreabilidade**: Auditoria e hashes de evidência asseguram cadeia de custódia e integridade.
- **Conformidade**: Validações automáticas LGPD reduzem risco legal.
- **Adoção**: Interface web simples e scripts one‑click facilitam uso por analistas não técnicos.
- **Consistência de Apresentação**: Exportações padronizadas em PDF/HTML para stakeholders.
- **Custo Controlado**: Solução leve e customizável internamente, sem licenças caras.

**Estimativa de ROI (modelo ilustrativo)**

- **Parâmetros**:
  - `Tempo_manual` = tempo médio gasto manualmente por plano.
  - `Tempo_tool` = tempo médio usando a aplicação.
  - `Custo_hora` = custo médio por hora do analista.
  - `Planos_anuais` = volume anual de planos.

- **Fórmula**:
  - Ganho_por_plano = (Tempo_manual − Tempo_tool) × Custo_hora
  - Ganho_anual = Ganho_por_plano × Planos_anuais
  - ROI ≈ (Ganho_anual − Custo_anual_sistema) / Custo_anual_sistema

- **Exemplo conservador (ilustrativo)**:
  - `Tempo_manual` = 4 h, `Tempo_tool` = 1 h → economiza 3 h/plano
  - `Custo_hora` = R$ 150 → ganho = R$ 450/plano
  - `Planos_anuais` = 100 → ganho anual = R$ 45.000
  - `Custo_anual_sistema` (manutenção/infra) ≈ R$ 6.000 → ROI ≈ 6,5x

- **Observações**:
  - ROI aumenta com volume e complexidade dos planos.
  - Economia indireta: redução de risco legal, menor retrabalho e melhor tomada de decisão não estão integralmente monetizadas no cálculo simplificado.

**Comparação Qualitativa com Alternativas**

- **Planilhas / Documentos Word**:
  - + Melhor rastreabilidade, validação e export padronizado.
  - − Investimento inicial em implantação.
- **Soluções Proprietárias (SaaS comerciais)**:
  - + Menor custo operacional e possibilidade de customização in‑house.
  - − Menos recursos enterprise out‑of‑the‑box (SSO, advanced analytics) sem integrações adicionais.
- **Ferramentas Internas Improvisadas**:
  - + Mais governança, menos perda de evidências e menos retrabalho.

**Riscos e Mitigações**

- **Adoção/treinamento**: Mitigar com documentação (`GETTING_STARTED_FOR_USERS.md`) e sessões rápidas de onboarding.
- **Segurança e Deploy**: Recomendar deploy em ambiente seguro (HTTPS, variáveis de ambiente seguras, firewall, backups automáticos).
- **Escalabilidade**: Para demandas maiores, migrar `SQLite` → `PostgreSQL` e colocar backend atrás de infraestrutura ASGI escalável.

**Recomendações Práticas**

- **Piloto**: Rodar piloto de 3 meses, medir tempo por plano, número de planos e incidentes ligados à conformidade.
- **Métricas-chave**: Tempo médio por plano, planos/analista/mês, incidentes LGPD, tempo para gerar relatório.
- **Manutenção**: Alocar 1–2 sprints/ano para melhorias e integrações (SSO, armazenamento de evidências externas).
- **Backup**: Automatizar backup do `backend/app.db` e garantir que `backend/app.db` esteja em `.gitignore`.

**Próximos Passos**

- **Personalizar ROI**: Atualizar a seção de ROI com números reais (custo por hora, volume anual). Posso ajudar a calcular se você fornecer os parâmetros.
- **Gerar artefatos**: Inserir gráficos simples (economia por plano, ROI anual) no relatório, se desejar.
- **Implantação**: Planejar um piloto com ambiente restrito e monitoramento.

**Contato / Suporte**

- **Arquivos relevantes**: `app/streamlit_app.py`, `backend/app/main.py`, `backend/app/services/pdf.py`, `run_app.command`.
- **Comandos úteis**:

```
# Iniciar backend local (desenvolvimento)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar frontend (Streamlit)
cd app
streamlit run streamlit_app.py
```

---

Relatório gerado automaticamente. Para ajustar a seção de ROI com números reais, envie: `Tempo_manual` (h), `Tempo_tool` (h), `Custo_hora` (R$) e `Planos_anuais`.
