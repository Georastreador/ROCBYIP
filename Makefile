.PHONY: install backend frontend test health help clean

help:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  OSINT Planning MVP v3 — Makefile                             ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo ""
	@echo "  make install              Instala dependências do projeto"
	@echo "  make backend              Roda o backend FastAPI (porta 8000)"
	@echo "  make frontend             Roda o frontend Streamlit (porta 8502)"
	@echo "  make health               Verifica saúde da API (GET /health)"
	@echo "  make test                 Roda testes (requer pytest)"
	@echo "  make clean                Remove arquivos temporários (__pycache__, .pyc)"
	@echo ""
	@echo "Exemplo de uso (2 terminais):"
	@echo "  Terminal 1: make backend"
	@echo "  Terminal 2: make frontend"
	@echo ""

install:
	@echo "📦 Instalando dependências..."
	pip install -r backend/requirements.txt
	@echo "✅ Dependências instaladas com sucesso!"

backend:
	@echo "🚀 Iniciando Backend (FastAPI) em http://127.0.0.1:8000"
	uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	@echo "🚀 Iniciando Frontend (Streamlit) em http://localhost:8502"
	streamlit run app/streamlit_app.py

health:
	@echo "🏥 Verificando saúde da API..."
	@curl -s http://127.0.0.1:8000/health | python -m json.tool || echo "❌ API não respondeu (verifique se o backend está rodando)"

test:
	@echo "🧪 Executando testes..."
	pytest -v

clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Limpeza concluída!"
