"""
Criptografia opcional em repouso para campos de texto (ex.: finalidade do plano).

Defina FIELD_ENCRYPTION_KEY com o output de:
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

Sem a variável, os dados permanecem em texto simples (compatível com instalações existentes).
"""
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

_PREFIX = "F1:"

_key = os.environ.get("FIELD_ENCRYPTION_KEY", "").strip()
_fernet: Optional[Fernet] = None
if _key:
    try:
        _fernet = Fernet(_key.encode("ascii"))
    except Exception:
        _fernet = None


def encryption_enabled() -> bool:
    return _fernet is not None


def encrypt_field(plain: str) -> str:
    if not _fernet or plain is None:
        return plain
    return _PREFIX + _fernet.encrypt(plain.encode("utf-8")).decode("ascii")


def decrypt_field(stored: str) -> str:
    if not stored or not stored.startswith(_PREFIX):
        return stored
    if not _fernet:
        return stored
    try:
        return _fernet.decrypt(stored[len(_PREFIX) :].encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError):
        return stored
