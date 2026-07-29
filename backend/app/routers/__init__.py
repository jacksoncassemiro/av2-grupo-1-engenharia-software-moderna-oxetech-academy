"""Camada Controller do MVC - routers FastAPI."""

from fastapi import APIRouter

from app.core.config import settings
from app.routers import (
    atendente_router,
    auth_router,
    consulta_router,
    especialidade_router,
    medico_router,
    paciente_router,
)

api_router = APIRouter(prefix=settings.API_PREFIX)
api_router.include_router(auth_router.router)
api_router.include_router(paciente_router.router)
api_router.include_router(especialidade_router.router)
api_router.include_router(medico_router.router)
api_router.include_router(consulta_router.router)
api_router.include_router(atendente_router.router)

__all__ = ["api_router"]
