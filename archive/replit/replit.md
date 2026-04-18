# ROC Planejamento de Inteligência — MVP v3

## Overview

This is a web-based OSINT (Open Source Intelligence) planning application that implements a systematic 10-phase intelligence planning methodology. The system helps analysts structure intelligence operations through a guided 13-step workflow, from defining the subject matter to exporting professional reports.

The application provides:
- **Structured intelligence planning** following established OSINT methodology
- **LGPD compliance validation** (Brazilian data protection regulation)
- **Evidence management** with cryptographic hashing (SHA-256)
- **Professional report generation** in PDF and HTML formats
- **Full audit trail** of all operations

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit 1.39.0 (reactive web UI)
- **State Management**: Streamlit session state for managing the 13-step workflow
- **HTTP Client**: httpx 0.27.2 for async API communication
- **Port**: 5000 (configured for Replit)
- **Configuration**: `.streamlit/config.toml` configured to bind to `0.0.0.0:5000` with CORS disabled for Replit proxy compatibility

The frontend implements a multi-step wizard pattern with sidebar navigation through 13 distinct phases of intelligence planning. All user data is stored in session state until explicitly saved to the backend.

### Backend Architecture
- **Framework**: FastAPI 0.115.0 (REST API)
- **Server**: Uvicorn 0.30.6 (ASGI)
- **Validation**: Pydantic 2.9.2 for request/response schemas
- **Port**: 8000 (default)

**Design Pattern**: Repository pattern with service layer
- Controllers (FastAPI routes) handle HTTP concerns
- Service layer (`services/`) contains business logic (audit, LGPD validation, PDF generation)
- Repository layer (SQLAlchemy models) handles data persistence

**API Structure**:
- RESTful endpoints for CRUD operations on intelligence plans
- Specialized endpoints for LGPD validation, evidence upload, and report generation
- Optional API key authentication (configurable via environment variables)

### Data Storage
- **Database**: SQLite (embedded, file-based)
- **ORM**: SQLAlchemy 2.0.35
- **File**: `plans.db` (created automatically)

**Schema Design**:
- `plans` table: Stores intelligence plans with JSON-serialized complex fields
- `evidences` table: Stores uploaded file metadata (filename, SHA-256 hash, size)
- `audit_logs` table: Created dynamically, tracks all operations

**Rationale for JSON fields**: Flexibility for nested structures (subject details, PIRs, collection tasks) without complex relational schema. Trade-off: Less queryable but simpler for MVP.

### Authentication & Authorization
- **Optional API Key**: Controlled by environment variables
  - `REQUIRE_API_KEY=true/false` - Enable/disable authentication
  - `API_KEY=<secret>` - The actual key value
- **Implementation**: FastAPI middleware checks `X-API-Key` header
- **Default**: Authentication disabled (`REQUIRE_API_KEY=false`)

**Security considerations**: Current implementation is basic (single API key). Production deployment should consider:
- JWT tokens for user-specific sessions
- Role-based access control
- Rate limiting
- HTTPS enforcement

### Report Generation
- **PDF**: ReportLab 4.2.5 - Programmatic PDF generation with custom layouts
- **HTML**: Template-based generation with embedded CSS
- **Process**: Server-side generation, file download via HTTP response with proper Content-Disposition headers

## External Dependencies

### Third-Party Services
None currently. The application is fully self-contained with no external API dependencies.

### Database
- **SQLite**: Embedded database, no external service required
- **Location**: Local file (`plans.db` in project root)
- **Migration strategy**: SQLAlchemy creates tables on startup via `Base.metadata.create_all()`

### Python Packages
**Core Framework**:
- `fastapi==0.115.0` - REST API framework
- `streamlit==1.39.0` - Frontend framework
- `uvicorn==0.30.6` - ASGI server

**Data & Validation**:
- `pydantic==2.9.2` - Data validation and serialization
- `SQLAlchemy==2.0.35` - ORM and database toolkit
- `pandas` - Data manipulation (used for Gantt chart visualization)

**Utilities**:
- `httpx==0.27.2` - Modern HTTP client (used by Streamlit to call FastAPI)
- `reportlab==4.2.5` - PDF generation
- `python-multipart==0.0.12` - Multipart form data parsing (file uploads)

**Development**:
- `pytest` - Testing framework (referenced in test files)

### File Storage
- **Evidence files**: Stored locally on server filesystem
- **Upload directory**: Configured in application (not externalized to cloud storage)
- **Hash verification**: SHA-256 checksums generated on upload

### Future Integration Points
The architecture supports potential integration with:
- **PostgreSQL**: SQLAlchemy abstraction allows easy database swap
- **Cloud storage**: Evidence upload service can be modified to use S3/Azure Blob
- **SSO providers**: FastAPI supports OAuth2/OIDC integration
- **External OSINT tools**: API structure allows integration as data sources

## Replit Environment Setup

**Date**: November 11, 2025

The application has been configured to run on Replit with the following setup:

### Workflows
1. **Backend Workflow** (`backend`):
   - Command: `uvicorn backend.app.main:app --host localhost --port 8000`
   - Binds to: `localhost:8000` (internal only)
   - Purpose: REST API server

2. **Frontend Workflow** (`frontend`):
   - Command: `streamlit run app/streamlit_app.py`
   - Binds to: `0.0.0.0:5000` (exposed via Replit proxy)
   - Purpose: Web UI
   - Configuration: `.streamlit/config.toml` configured with CORS disabled and host verification bypassed

### Deployment
- **Target**: Autoscale (stateless web application)
- **Command**: Both backend and frontend run concurrently using bash process backgrounding
- **Port**: Frontend serves on port 5000 (required for Replit webview)

### Environment Variables
- `API_URL`: Set to `http://localhost:8000` (default, frontend connects to backend)
- `REQUIRE_API_KEY`: Optional, set to `true` to enable API key authentication
- `API_KEY`: Optional, set to custom API key value

### Package Management
- **Python Version**: 3.11
- **Package Manager**: uv (Replit's Python package manager)
- **Dependencies**: Installed from requirements.txt using `uv add`

### Database
- **SQLite**: Automatically created at `plans.db` on first run
- **Persistence**: Database file is created in project root