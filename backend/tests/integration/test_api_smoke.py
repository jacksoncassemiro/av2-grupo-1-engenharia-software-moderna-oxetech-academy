"""Smoke de integracao - roda no CI para garantir que a app sobe e as rotas existem."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


@pytest.mark.integration
def test_health_responde_ok():
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "healthy"


@pytest.mark.integration
def test_openapi_expoe_as_rotas_esperadas():
    caminhos = cliente.get("/openapi.json").json()["paths"]
    esperadas = [
        "/api/auth/login",
        "/api/auth/vincular-ou-criar",
        "/api/pacientes",
        "/api/especialidades",
        "/api/medicos",
        "/api/medicos/{medico_id}/agenda",
        "/api/consultas",
        "/api/atendente/consultas",
    ]
    faltando = [rota for rota in esperadas if rota not in caminhos]
    assert not faltando, f"Rotas ausentes no OpenAPI: {faltando}"


@pytest.mark.integration
def test_rota_protegida_rejeita_sem_token():
    """RF19 - 401 sem token."""
    assert cliente.get("/api/consultas").status_code == 401
