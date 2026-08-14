"""
Módulo de Utilitários de Segurança para ROCBYIP vf1
Contém funções para sanitização, validação e segurança
"""
import html
import io
import re
import os
import logging
import secrets
import zipfile
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTES DE SEGURANÇA
# ============================================================================

MAX_USER_INPUT_LENGTH = 1000  # Máximo de caracteres em entrada do usuário
MAX_LOG_DETAIL_LENGTH = 500   # Máximo de caracteres em logs


# ============================================================================
# SANITIZAÇÃO DE TEXTO E HTML
# ============================================================================

def sanitize_html_text(text: Any, max_length: Optional[int] = None) -> str:
    """
    Sanitiza texto para uso em HTML escapando caracteres especiais
    
    Args:
        text: Texto a ser sanitizado (pode ser qualquer tipo)
        max_length: Tamanho máximo permitido
    
    Returns:
        Texto sanitizado e escapado para HTML
    """
    if text is None:
        return ""
    
    # Converter para string
    text = str(text)
    
    # Limitar tamanho se especificado
    if max_length:
        text = text[:max_length]
    
    # Escapar caracteres HTML especiais
    sanitized = html.escape(text)
    
    # Remover caracteres de controle
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', sanitized)
    
    return sanitized.strip()


def sanitize_text(text: str, max_length: int = MAX_USER_INPUT_LENGTH, allow_newlines: bool = True) -> str:
    """
    Sanitiza texto de entrada removendo caracteres perigosos
    
    Args:
        text: Texto a ser sanitizado
        max_length: Tamanho máximo permitido
        allow_newlines: Se True, permite \n, \r, \t
    
    Returns:
        Texto sanitizado
    """
    if not text:
        return ""
    
    # Converter para string se necessário
    text = str(text)
    
    # Limitar tamanho
    if max_length:
        text = text[:max_length]
    
    # Remover caracteres de controle
    if allow_newlines:
        # Permite \n (0x0A), \r (0x0D), \t (0x09)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    else:
        # Remove todos os caracteres de controle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Normalizar espaços em branco múltiplos (exceto quebras de linha)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remover espaços no início e fim
    text = text.strip()
    
    return text


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo prevenindo path traversal
    
    Args:
        filename: Nome de arquivo a sanitizar
    
    Returns:
        Nome de arquivo sanitizado
    """
    if not filename:
        return "unnamed"
    
    # Remover path separators
    filename = filename.replace('/', '').replace('\\', '')
    
    # Remover caracteres perigosos (manter apenas alfanuméricos, pontos, hífens, underscores)
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Substituir espaços por underscores
    filename = filename.replace(' ', '_')
    
    # Limitar tamanho
    filename = filename[:255]
    
    # Remover pontos múltiplos
    while '..' in filename:
        filename = filename.replace('..', '.')
    
    # Remover pontos no início e fim
    filename = filename.strip('.')
    
    return filename or "unnamed"


# ============================================================================
# VALIDAÇÃO DE PATHS
# ============================================================================

def safe_path_join(base_dir: str, *paths: str) -> str:
    """
    Junta paths de forma segura prevenindo path traversal
    
    Args:
        base_dir: Diretório base
        *paths: Caminhos a juntar
    
    Returns:
        Path seguro absoluto
    
    Raises:
        ValueError: Se path traversal for detectado
    """
    base = Path(base_dir).resolve()
    
    # Construir path completo
    full_path = base
    for path in paths:
        sanitized = sanitize_filename(path)
        full_path = full_path / sanitized
    
    # Resolver path final
    try:
        resolved = full_path.resolve()
        # Verificar que está dentro do base_dir
        resolved.relative_to(base)
    except ValueError:
        raise ValueError("Path traversal detectado - acesso negado")
    
    return str(resolved)


# ============================================================================
# SANITIZAÇÃO DE LOGS
# ============================================================================

def sanitize_log_detail(detail: str, max_length: int = MAX_LOG_DETAIL_LENGTH) -> str:
    """
    Sanitiza detalhes de log removendo informações sensíveis
    
    Args:
        detail: Detalhe do log a sanitizar
        max_length: Tamanho máximo permitido
    
    Returns:
        Detalhe sanitizado
    """
    if not detail:
        return ""
    
    detail = str(detail)
    
    # Limitar tamanho
    if max_length:
        detail = detail[:max_length]
    
    # Remover possíveis informações sensíveis (padrões comuns)
    patterns_to_mask = [
        (r'(password|pwd|passwd)\s*[:=]\s*[^\s]+', r'\1=***'),
        (r'(token|api[_-]?key|secret|key)\s*[:=]\s*[^\s]+', r'\1=***'),
        (r'(authorization|auth)\s*[:=]\s*[^\s]+', r'\1=***'),
        (r'bearer\s+[a-zA-Z0-9_-]+', 'bearer ***', re.IGNORECASE),
    ]
    
    for pattern, replacement, *flags in patterns_to_mask:
        flags_combined = flags[0] if flags else 0
        detail = re.sub(pattern, replacement, detail, flags=flags_combined)
    
    # Remover caracteres de controle
    detail = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', detail)
    
    return detail.strip()


# ============================================================================
# VALIDAÇÃO DE API KEY
# ============================================================================

def validate_api_key(api_key: Optional[str], require_key: bool = False) -> tuple[bool, Optional[str]]:
    """
    Valida formato e força de API key
    
    Args:
        api_key: Chave API a validar
        require_key: Se True, chave é obrigatória
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if require_key:
        if not api_key:
            return False, "API_KEY é obrigatória quando REQUIRE_API_KEY=true"
        
        if len(api_key) < 32:
            return False, "API_KEY deve ter pelo menos 32 caracteres"
        
        # Validar que não é valor padrão inseguro
        insecure_defaults = ["devkey", "default", "test", "admin", "password", "123456"]
        if api_key.lower() in insecure_defaults:
            return False, "API_KEY não pode usar valores padrão inseguros"

    return True, None


def api_keys_match(provided: Optional[str], expected: Optional[str]) -> bool:
    """Compara API keys em tempo constante. False se qualquer uma estiver ausente."""
    if not provided or not expected:
        return False
    return secrets.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))


# ============================================================================
# VALIDAÇÃO DE CONTEÚDO DE UPLOAD (MAGIC BYTES)
# ============================================================================

# Assinaturas (magic bytes) para os tipos binários aceitos em uploads de evidência
_FILE_SIGNATURES = {
    ".pdf": (b"%PDF",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".gif": (b"GIF87a", b"GIF89a"),
    ".docx": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    ".xlsx": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    ".doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
    ".xls": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
    ".zip": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
    ".rar": (b"Rar!\x1a\x07\x00", b"Rar!\x1a\x07\x01\x00"),
    ".7z": (b"7z\xbc\xaf\x27\x1c",),
}


def _is_valid_ooxml(content: bytes) -> bool:
    """
    Confirma que um ZIP é um pacote OOXML (docx/xlsx) de verdade, não apenas
    qualquer arquivo ZIP renomeado. Todo pacote OOXML válido tem um
    "[Content_Types].xml" na raiz. Só lê a lista de entradas (namelist),
    nunca descompacta conteúdo — não há risco de zip bomb aqui.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            return "[Content_Types].xml" in zf.namelist()
    except (zipfile.BadZipFile, OSError, EOFError):
        return False


def content_matches_extension(filename: str, content: bytes) -> bool:
    """
    Valida magic bytes para tipos binários; texto é aceito se não for vazio.
    O cliente controla `filename` e o `Content-Type` declarado — magic bytes
    são o único sinal que não é trivialmente falsificável sem alterar o
    próprio arquivo.
    """
    ext = Path(filename).suffix.lower()
    if ext in {".txt", ".md", ".csv", ".json", ".xml"}:
        return True
    signatures = _FILE_SIGNATURES.get(ext)
    if not signatures:
        return False
    if not any(content.startswith(sig) for sig in signatures):
        return False
    if ext in {".docx", ".xlsx"}:
        # PK\x03\x04 e afins também batem com qualquer ZIP comum — exige a
        # estrutura interna do OOXML para não aceitar um .zip só renomeado.
        return _is_valid_ooxml(content)
    return True
