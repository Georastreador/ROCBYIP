"""
AUTH_REQUIRED:
  - none: sem autenticação (desenvolvimento)
  - api_key: apenas X-API-Key válida (REQUIRE_API_KEY=true recomendado)
  - jwt: apenas Bearer JWT
  - api_key_or_jwt: qualquer um dos dois

Se AUTH_REQUIRED não estiver definido, usa REQUIRE_API_KEY legado:
  REQUIRE_API_KEY=true → api_key; caso contrário → none.
"""
import os


def auth_required_mode() -> str:
    explicit = os.environ.get("AUTH_REQUIRED", "").strip().lower()
    if explicit in ("none", "api_key", "jwt", "api_key_or_jwt"):
        return explicit
    if os.environ.get("REQUIRE_API_KEY", "false").lower() == "true":
        return "api_key"
    return "none"
