"""
Testes básicos da API OSINT Planning

Para rodar:
  1. Certifique-se de que o backend está rodando: uvicorn backend.app.main:app
  2. Execute: pytest -v

Para rodar com cobertura:
  pip install pytest-cov
  pytest --cov=backend --cov-report=html
"""

import httpx
import json
import pytest

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5.0


class TestHealth:
    """Testes de verificação de saúde da API"""

    def test_health_endpoint(self):
        """Deve retornar status 'ok'"""
        response = httpx.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        assert response.json().get("status") == "ok"


class TestPlans:
    """Testes de gerenciamento de planos"""

    @pytest.fixture
    def sample_plan(self):
        """Fixture com um plano de exemplo"""
        return {
            "title": "Plano de Teste",
            "subject": {"what": "Teste", "who": "QA", "where": "Local"},
            "time_window": {"start": "2025-11-01", "end": "2025-11-30"},
            "user": {
                "principal": "user@example.com",
                "others": "",
                "depth": "tecnico",
                "secrecy": "publico",
            },
            "purpose": "Tester a API",
            "deadline": {"date": "2025-11-30", "urgency": "alta"},
            "aspects_essential": ["Aspecto 1", "Aspecto 2"],
            "aspects_known": ["Conhecido 1"],
            "aspects_to_know": ["A Conhecer 1"],
            "pirs": [
                {
                    "aspect_ref": 0,
                    "question": "Qual é a resposta?",
                    "priority": "alta",
                    "justification": "Teste",
                }
            ],
            "collection": [
                {
                    "pir_index": 0,
                    "source": "Fonte Teste",
                    "method": "API",
                    "frequency": "unico",
                    "owner": "QA",
                    "sla_hours": 24,
                }
            ],
            "extraordinary": ["Medida 1"],
            "security": ["Segurança 1"],
        }

    def test_create_plan(self, sample_plan):
        """Deve criar um novo plano com sucesso"""
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(f"{BASE_URL}/plans", json=sample_plan)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_plan["title"]
        assert data["id"] is not None
        return data["id"]

    def test_list_plans(self):
        """Deve listar todos os planos"""
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(f"{BASE_URL}/plans")

        assert response.status_code == 200
        plans = response.json()
        assert isinstance(plans, list)

    def test_get_plan_not_found(self):
        """Deve retornar 404 para plano inexistente"""
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(f"{BASE_URL}/plans/99999")

        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
