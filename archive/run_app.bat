@echo off
REM ROC Planejamento de Inteligência — Script de Execução
REM Para Windows — Duplo clique para iniciar a aplicação
REM
REM Este script:
REM 1. Verifica se Python está instalado
REM 2. Cria virtual environment se não existir
REM 3. Instala dependências
REM 4. Inicia Backend (FastAPI) em background
REM 5. Inicia Frontend (Streamlit)
REM 6. Abre browser automaticamente

setlocal enabledelayedexpansion

REM Definir cores (simuladas com escape codes)
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║      ROC Planejamento de Inteligência — MVP v3            ║
echo ║                                                            ║
echo ║              Iniciando Aplicação...                       ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro: Python não foi encontrado!
    echo.
    echo Por favor, instale Python 3.10 ou superior:
    echo   → https://www.python.org/downloads/
    echo.
    echo NOTA: Durante a instalação, certifique-se de marcar
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado
echo.

REM Criar virtual environment se não existir
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
    echo ✅ Ambiente virtual criado
    echo.
)

REM Ativar virtual environment
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar/atualizar dependências
echo 📥 Instalando dependências...
pip install --quiet --upgrade pip setuptools wheel >nul 2>&1

if exist "backend\requirements.txt" (
    pip install --quiet -r backend\requirements.txt >nul 2>&1
    echo ✅ Dependências do backend instaladas
)

if exist "app\requirements.txt" (
    pip install --quiet -r app\requirements.txt >nul 2>&1
    echo ✅ Dependências do frontend instaladas
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✅ Preparação concluída!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Verificar e liberar porta 8000
echo 🔧 Verificando porta 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo    Porta 8000 em uso, encerrando processo...
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo ✅ Porta 8000 liberada
echo.

REM Iniciar Backend em background
echo 🚀 Iniciando Backend (FastAPI)...
cd backend
start "" cmd /c "uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level critical"
cd ..

echo ✅ Backend iniciado
echo    Aguardando inicialização...
timeout /t 5 /nobreak >nul

echo ✅ Backend pronto em http://localhost:8000
echo.

REM Iniciar Frontend
echo 🚀 Iniciando Frontend (Streamlit)...
timeout /t 2 /nobreak >nul

REM Abrir browser (Windows)
start http://localhost:8501

cd app
streamlit run streamlit_app.py --logger.level=error

echo.
echo ✅ Aplicação encerrada.
pause
