#!/bin/bash

# Script para executar ROC BYIP localmente
# Inicia Backend (FastAPI) e Frontend (Streamlit) simultaneamente

echo "🚀 Iniciando ROC BYIP"
echo "===================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar se está no diretório correto
if [ ! -f "app/streamlit_app.py" ] || [ ! -f "backend/app/main.py" ]; then
    echo -e "${RED}❌ Erro: Execute este script no diretório da aplicação BYIP${NC}"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado${NC}"
    exit 1
fi

# Ambiente virtual local (.venv ou venv)
if [ -f ".venv/bin/activate" ]; then
    # shellcheck source=/dev/null
    source .venv/bin/activate
    echo -e "${GREEN}✅ Ambiente virtual: .venv${NC}"
elif [ -f "venv/bin/activate" ]; then
    # shellcheck source=/dev/null
    source venv/bin/activate
    echo -e "${GREEN}✅ Ambiente virtual: venv${NC}"
else
    echo -e "${YELLOW}⚠️  Sem venv nesta pasta. Crie com: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt${NC}"
fi

# Variáveis locais (ex.: DATABASE_URL). Use aspas na URL se tiver caracteres especiais.
if [ -f "backend/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    . backend/.env
    set +a
    echo -e "${GREEN}📄 Carregado: backend/.env${NC}"
fi

# Verificar dependências principais
echo "📋 Verificando dependências..."
python3 -c "import fastapi, streamlit, sqlalchemy, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Algumas dependências podem estar faltando${NC}"
    echo "Instale com: pip install -r requirements.txt"
    read -p "Continuar mesmo assim? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

if [ -n "${DATABASE_URL}" ]; then
    echo -e "${GREEN}📦 DATABASE_URL definido (PostgreSQL ou URL explícita).${NC}"
else
    echo -e "${YELLOW}💡 Sem DATABASE_URL: usa SQLite em backend/plans.db. Para Postgres: export DATABASE_URL=postgresql://...${NC}"
fi

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Encerrando serviços...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar Backend
echo ""
echo -e "${GREEN}📡 Iniciando Backend (FastAPI) na porta 8000...${NC}"
cd backend
# Host 127.0.0.1 por segurança (use HOST=0.0.0.0 para acesso em rede local)
uvicorn app.main:app --reload --host ${HOST:-127.0.0.1} --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Aguardar backend iniciar
sleep 3

# Verificar se backend iniciou
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend pode não ter iniciado corretamente${NC}"
    echo "Verifique: tail -f backend.log"
else
    echo -e "${GREEN}✅ Backend iniciado: http://localhost:8000${NC}"
    echo -e "${GREEN}   Documentação: http://localhost:8000/docs${NC}"
fi

# Iniciar Frontend
echo ""
echo -e "${GREEN}🎨 Iniciando Frontend (Streamlit) na porta 8501...${NC}"
cd app
streamlit run streamlit_app.py --server.port 8501 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Aguardar frontend iniciar
sleep 3

echo ""
echo "=================================="
echo -e "${GREEN}✅ Aplicação iniciada!${NC}"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:8501"
echo ""
echo "Documentação API: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para encerrar${NC}"
echo ""

# Manter script rodando
wait
