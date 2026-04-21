"""
Integração Kinde OAuth2 + PKCE para Streamlit — Padrão ROC Intelligence

Desafio do Streamlit: um redirect OAuth completo cria uma NOVA sessão,
perdendo o session_state. Solução: embeder o code_verifier no parâmetro
`state` (codificado em base64), que sobrevive ao redirect.

Fluxo:
  1. App carrega → check_auth() → sem token → show_login_page()
  2. Utilizador clica "Entrar" → redirect para Kinde com state=<verifier+nonce>
  3. Kinde redireciona de volta com ?code=xxx&state=xxx
  4. check_auth() deteta ?code e extrai o verifier do state
  5. exchange_code() obtém access_token → guardado em session_state
  6. App recarrega → check_auth() → token válido → app normal
"""

import os
import base64
import hashlib
import hmac
import secrets
import time
import logging
from urllib.parse import urlencode

import httpx
import streamlit as st
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

# ── Configuração via env vars ─────────────────────────────────────────────────
KINDE_DOMAIN        = os.getenv("KINDE_DOMAIN", "").rstrip("/")
KINDE_CLIENT_ID     = os.getenv("KINDE_CLIENT_ID", "")
KINDE_CLIENT_SECRET = os.getenv("KINDE_CLIENT_SECRET", "")
KINDE_REDIRECT_URI  = os.getenv("KINDE_REDIRECT_URI", "https://byip.rocintelligence.com")
# Segredo para assinar o state (previne adulteração)
_STATE_SECRET = os.getenv("SESSION_SECRET", "roc-byip-state-secret-change-in-prod")

SESSION_KEY = "kinde_access_token"

# Cache JWKS
_jwks_cache: dict = {"keys": None, "expires_at": 0}


# ── PKCE ──────────────────────────────────────────────────────────────────────

def _generate_pkce():
    code_verifier  = secrets.token_urlsafe(64)
    digest         = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge


def _encode_state(code_verifier: str) -> str:
    """Embeda o code_verifier no state com uma assinatura HMAC."""
    nonce   = secrets.token_urlsafe(16)
    payload = f"{code_verifier}|{nonce}"
    sig     = hmac.new(_STATE_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return base64.urlsafe_b64encode(f"{payload}|{sig}".encode()).decode()


def _decode_state(state: str) -> str | None:
    """Extrai o code_verifier do state. Retorna None se inválido."""
    try:
        decoded = base64.urlsafe_b64decode(state.encode() + b"==").decode()
        parts   = decoded.split("|")
        if len(parts) != 3:
            return None
        code_verifier, nonce, sig = parts
        expected_sig = hmac.new(_STATE_SECRET.encode(), f"{code_verifier}|{nonce}".encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected_sig):
            return None
        return code_verifier
    except Exception:
        return None


def _build_auth_url(code_challenge: str, state: str) -> str:
    params = {
        "client_id"            : KINDE_CLIENT_ID,
        "redirect_uri"         : KINDE_REDIRECT_URI,
        "response_type"        : "code",
        "scope"                : "openid profile email",
        "code_challenge"       : code_challenge,
        "code_challenge_method": "S256",
        "state"                : state,
    }
    return f"{KINDE_DOMAIN}/oauth2/auth?" + urlencode(params)


def _exchange_code(code: str, code_verifier: str) -> str | None:
    """Troca authorization code por access_token. Retorna None em caso de erro."""
    data = {
        "grant_type"   : "authorization_code",
        "client_id"    : KINDE_CLIENT_ID,
        "redirect_uri" : KINDE_REDIRECT_URI,
        "code"         : code,
        "code_verifier": code_verifier,
    }
    if KINDE_CLIENT_SECRET:
        data["client_secret"] = KINDE_CLIENT_SECRET

    try:
        resp = httpx.post(
            f"{KINDE_DOMAIN}/oauth2/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("access_token")
        logger.error("Kinde token exchange: %s %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.error("Kinde token exchange error: %s", exc)
    return None


def _fetch_jwks() -> dict:
    global _jwks_cache
    now = time.time()
    if _jwks_cache["keys"] and now < _jwks_cache["expires_at"]:
        return _jwks_cache["keys"]
    resp = httpx.get(f"{KINDE_DOMAIN}/.well-known/jwks", timeout=10)
    _jwks_cache = {"keys": resp.json(), "expires_at": now + 3600}
    return _jwks_cache["keys"]


def _validate_token(token: str) -> dict | None:
    """Valida JWT. Retorna payload ou None se inválido."""
    try:
        jwks    = _fetch_jwks()
        payload = jwt.decode(token, jwks, algorithms=["RS256"], options={"verify_aud": False})
        return payload
    except JWTError as exc:
        logger.warning("Token inválido: %s", exc)
        return None


# ── API pública ───────────────────────────────────────────────────────────────

def is_configured() -> bool:
    return bool(KINDE_DOMAIN and KINDE_CLIENT_ID)


def check_auth() -> bool:
    """
    Verifica autenticação. Deve ser chamada logo após st.set_page_config.
    Retorna True se autenticado, False se não (neste caso mostra o ecrã de login).
    """
    if not is_configured():
        return True  # Dev: sem Kinde configurado, deixa passar

    # ── Processar callback OAuth ──────────────────────────────────────────
    params = st.query_params
    code  = params.get("code")
    state = params.get("state")

    if code and state:
        code_verifier = _decode_state(state)
        if code_verifier:
            token = _exchange_code(code, code_verifier)
            if token:
                st.session_state[SESSION_KEY] = token
                st.query_params.clear()
                st.rerun()
                return False  # rerun vai correr logo
        # State inválido ou troca falhou
        st.session_state.pop(SESSION_KEY, None)

    # ── Verificar token existente ─────────────────────────────────────────
    token = st.session_state.get(SESSION_KEY)
    if token:
        payload = _validate_token(token)
        if payload:
            st.session_state["kinde_user"] = payload
            return True
        # Token expirado
        del st.session_state[SESSION_KEY]

    # ── Não autenticado → mostrar ecrã de login ───────────────────────────
    _show_login_page()
    return False


def get_user() -> dict:
    """Retorna o payload do utilizador autenticado."""
    return st.session_state.get("kinde_user", {})


def logout():
    """Remove sessão e redireciona para logout Kinde."""
    st.session_state.pop(SESSION_KEY, None)
    st.session_state.pop("kinde_user", None)
    logout_url = (
        f"{KINDE_DOMAIN}/logout?redirect={KINDE_REDIRECT_URI}"
        if is_configured() else KINDE_REDIRECT_URI
    )
    st.markdown(f'<meta http-equiv="refresh" content="0; url={logout_url}">', unsafe_allow_html=True)
    st.stop()


def _show_login_page():
    """Renderiza o ecrã de login e para a execução do resto da app."""
    code_verifier, code_challenge = _generate_pkce()
    state    = _encode_state(code_verifier)
    auth_url = _build_auth_url(code_challenge, state)

    st.markdown("""
    <style>
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { max-width: 480px; margin: 8vh auto; padding: 2rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding:2rem 1rem;">
        <div style="font-size:3.5rem; margin-bottom:1rem;">🔐</div>
        <h2 style="margin-bottom:0.4rem;">ROC BYIP</h2>
        <p style="color:#888; margin-bottom:0.3rem;">Plataforma ROC Intelligence</p>
        <p style="color:#aaa; font-size:0.85rem; margin-bottom:2rem;">
            Acesso exclusivo para utilizadores autorizados
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button(
            "🔑  Entrar com ROC Intelligence",
            auth_url,
            use_container_width=True,
            type="primary",
        )

    st.stop()  # Impede que o resto da app seja renderizado
