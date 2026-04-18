# Infraestrutura — HTTPS e reverse proxy (ROCBYIP)

Objetivo: terminar TLS na borda (nginx ou Traefik) e expor **dois destinos** na Internet:

| Serviço   | Porta local típica | URL pública sugerida      |
|----------|--------------------|---------------------------|
| FastAPI  | 8000               | `https://api.seu-dominio` |
| Streamlit | 8501              | `https://app.seu-dominio` |

Subdomínios separados evitam misturar rotas `/api` com o Streamlit e simplificam CORS.

## Variáveis da aplicação (obrigatório em produção)

No **servidor** onde corre o backend e o Streamlit:

```bash
export HOST=0.0.0.0
export API_URL="https://api.seu-dominio"
export CORS_ORIGINS="https://app.seu-dominio"
```

- `API_URL` é lido pelo `app/streamlit_app.py` (chamadas à API).
- `CORS_ORIGINS` é lido por `backend/app/main.py` (origens permitidas no browser).

O Streamlit envia automaticamente `X-API-Key` (variável `API_KEY`) e, após login no painel, `Authorization: Bearer …` para JWT.

Segurança adicional no backend (ver `backend/app/auth_policy.py`):

- `AUTH_REQUIRED`: `none` | `api_key` | `jwt` | `api_key_or_jwt` (se omitido: deriva de `REQUIRE_API_KEY` legado).
- `JWT_SECRET`, `INITIAL_ADMIN_EMAIL` / `INITIAL_ADMIN_PASSWORD` (primeiro administrador), `FIELD_ENCRYPTION_KEY` (opcional, finalidade cifrada), `ALLOW_REGISTRATION`, `ENABLE_PUBLIC_SHARE`.

## Opção A — nginx + certificados

1. Copie e adapte `nginx/rocbyip.example.conf` (domínios, caminhos SSL).
2. Certificados Let's Encrypt (exemplo com certbot em Ubuntu):

   ```bash
   sudo certbot certonly --webroot -w /var/www/html -d api.seu-dominio -d app.seu-dominio
   ```

   Ou use o plugin nginx se preferir gestão automática do `server` block.

3. Valide e recarregie:

   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ```

4. Suba a app com `HOST=0.0.0.0` (uvicorn e streamlit a ouvir em todas as interfaces).

## Opção B — Traefik (Docker)

1. Ficheiros em `traefik/`: `docker-compose.traefik.yml`, `traefik.yml`, `dynamic/rocbyip.yml`.
2. Edite o **e-mail** em `traefik.yml` (`certificatesResolvers.letsencrypt.acme.email`).
3. Edite os **Host** em `dynamic/rocbyip.yml` para os seus FQDN.
4. DNS de `api.*` e `app.*` devem apontar para o IP do servidor **antes** do primeiro arranque (HTTP-01 na porta 80).

```bash
cd infra/traefik
docker compose -f docker-compose.traefik.yml up -d
```

O compose usa `extra_hosts` com `host-gateway` para que `host.docker.internal` resolva para o host no Linux.

## Provedores cloud (terminação TLS)

Padrão comum: o balanceador **HTTPS** do cloud termina TLS e encaminha HTTP internamente para a VM ou container. Nesse caso:

- Configure **health check** no `/health` (FastAPI).
- Passe cabeçalhos `X-Forwarded-Proto` / `X-Forwarded-For` (a maioria dos LB faz isso por defeito).
- Use as **mesmas** variáveis `API_URL` e `CORS_ORIGINS` com os URLs **públicos** https.

Exemplos: AWS ALB + EC2, GCP Cloud Load Balancing, Azure App Gateway, Fly.io / Railway / Render (cada um com o seu formato de domínio e variáveis). O ponto fixo é: URL público da API alinhado com `API_URL` e origem do Streamlit alinhada com `CORS_ORIGINS`.

## Notas de segurança

- Não exponha `/docs` publicamente sem autenticação extra se a API estiver na Internet; considere restrições no proxy ou `ENVIRONMENT=production` com rotas desativadas (evolução futura na app).
- Garanta que SQLite ou ficheiros de upload **não** ficam num volume inseguro; em cloud prefira Postgres (`DATABASE_URL`) e backups geridos.
