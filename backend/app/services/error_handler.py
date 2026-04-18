"""
Tratamento centralizado de erros para a API
"""
import os
import logging
import traceback
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from pydantic import ValidationError
import json

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Modo debug (desenvolvimento) - expõe mais detalhes
DEBUG_MODE = os.environ.get("DEBUG", "false").lower() == "true"


def log_error(error: Exception, request: Request, context: Optional[dict] = None):
    """Log estruturado de erros"""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "path": request.url.path,
        "method": request.method,
        "client_ip": request.client.host if request.client else None,
    }
    
    if context:
        error_info.update(context)
    
    # Log completo com traceback em modo debug
    if DEBUG_MODE:
        error_info["traceback"] = traceback.format_exc()
        logger.error(f"Error details: {json.dumps(error_info, indent=2, default=str)}")
    else:
        logger.error(f"Error: {json.dumps(error_info, default=str)}")


def setup_exception_handlers(app):
    """Configura todos os exception handlers"""
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """Tratamento de erros do SQLAlchemy"""
        log_error(exc, request, {"error_category": "database"})
        
        if isinstance(exc, IntegrityError):
            return JSONResponse(
                status_code=409,
                content={
                    "error": "Database integrity error",
                    "detail": "A conflict occurred with the current state of the resource." if not DEBUG_MODE else str(exc)
                }
            )
        elif isinstance(exc, OperationalError):
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Database connection error",
                    "detail": "Service temporarily unavailable. Please try again later." if not DEBUG_MODE else str(exc)
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Database error",
                    "detail": "An error occurred while processing your request." if not DEBUG_MODE else str(exc)
                }
            )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """Tratamento de erros de validação Pydantic"""
        log_error(exc, request, {"error_category": "validation"})
        
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "detail": "Invalid input data",
                "errors": errors
            }
        )

    @app.exception_handler(json.JSONDecodeError)
    async def json_decode_exception_handler(request: Request, exc: json.JSONDecodeError):
        """Tratamento de erros de decodificação JSON"""
        log_error(exc, request, {"error_category": "json"})
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid JSON",
                "detail": "The request body contains invalid JSON." if not DEBUG_MODE else str(exc)
            }
        )

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_exception_handler(request: Request, exc: FileNotFoundError):
        """Tratamento de arquivos não encontrados"""
        log_error(exc, request, {"error_category": "file_io"})
        
        return JSONResponse(
            status_code=404,
            content={
                "error": "File not found",
                "detail": "The requested file could not be found." if not DEBUG_MODE else str(exc)
            }
        )

    @app.exception_handler(PermissionError)
    async def permission_exception_handler(request: Request, exc: PermissionError):
        """Tratamento de erros de permissão"""
        log_error(exc, request, {"error_category": "permission"})
        
        return JSONResponse(
            status_code=403,
            content={
                "error": "Permission denied",
                "detail": "You do not have permission to perform this action." if not DEBUG_MODE else str(exc)
            }
        )

    @app.exception_handler(TimeoutError)
    async def timeout_exception_handler(request: Request, exc: TimeoutError):
        """Tratamento de timeouts"""
        log_error(exc, request, {"error_category": "timeout"})
        
        return JSONResponse(
            status_code=504,
            content={
                "error": "Request timeout",
                "detail": "The request took too long to process. Please try again." if not DEBUG_MODE else str(exc)
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Tratamento de HTTPExceptions (mantém comportamento padrão mas com logging)"""
        log_error(exc, request, {"error_category": "http", "status_code": exc.status_code})
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail if isinstance(exc.detail, str) else "HTTP error",
                "detail": exc.detail
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handler genérico para todos os outros erros"""
        log_error(exc, request, {"error_category": "general"})
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later." if not DEBUG_MODE else str(exc)
            }
        )

