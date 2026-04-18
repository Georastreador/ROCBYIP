#!/bin/bash

# ROC Planejamento de Inteligência — Script de Execução
# Para macOS — Duplo clique para iniciar a aplicação
# 
# Este script:
# 1. Verifica se Python está instalado
# 2. Cria virtual environment se não existir
# 3. Instala dependências
# 4. Inicia Backend (FastAPI) em background
# 5. Inicia Frontend (Streamlit)
# 6. Abre browser automaticamente

set -e  # Sair ao primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║      ROC Planejamento de Inteligência — MVP v3            ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║              Iniciando Aplicação...                       ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Erro: Python 3 não encontrado!${NC}"
    echo ""
    echo "Por favor, instale Python 3.10 ou superior:"
    echo "  → https://www.python.org/downloads/"
    echo ""
    read -p "Pressione ENTER para sair..."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} encontrado${NC}"
echo ""

# Criar virtual environment se não existir
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Criando ambiente virtual...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
    echo ""
fi

# Ativar virtual environment
echo -e "${YELLOW}🔧 Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Instalar/atualizar dependências
echo -e "${YELLOW}📥 Instalando dependências...${NC}"
pip install --quiet --upgrade pip setuptools wheel

if [ -f "backend/requirements.txt" ]; then
    pip install --quiet -r backend/requirements.txt
    echo -e "${GREEN}✅ Dependências do backend instaladas${NC}"
fi

if [ -f "app/requirements.txt" ]; then
    pip install --quiet -r app/requirements.txt
    echo -e "${GREEN}✅ Dependências do frontend instaladas${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Preparação concluída!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Liberar porta 8000 se estiver em uso
echo -e "${YELLOW}🔧 Verificando porta 8000...${NC}"
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}   Porta 8000 em uso, encerrando processo anterior...${NC}"
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi
echo -e "${GREEN}✅ Porta 8000 liberada${NC}"
echo ""

# Iniciar Backend
echo -e "${YELLOW}🚀 Iniciando Backend (FastAPI)...${NC}"
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level critical > /dev/null 2>&1 &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}✅ Backend iniciado (PID: ${BACKEND_PID})${NC}"
echo -e "${YELLOW}   Aguardando inicialização...${NC}"
sleep 5

# Verificar se backend iniciou corretamente
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Erro ao iniciar backend!${NC}"
    echo -e "${RED}   Verifique se a porta 8000 está disponível.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend pronto em http://localhost:8000${NC}"
echo ""

# Iniciar Frontend
echo -e "${YELLOW}🚀 Iniciando Frontend (Streamlit)...${NC}"
sleep 2

# Abrir browser (macOS)
if command -v open &> /dev/null; then
    sleep 3
    open http://localhost:8501
fi

cd app
streamlit run streamlit_app.py --logger.level=error

# Ao sair, matar backend
kill $BACKEND_PID 2>/dev/null || true

echo ""
echo -e "${BLUE}✅ Aplicação encerrada.${NC}"
