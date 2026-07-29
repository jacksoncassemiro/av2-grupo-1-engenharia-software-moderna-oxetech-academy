"""Ponto de entrada da API. Monta CORS, handlers de erro e os routers."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.exceptions.handlers import registrar_handlers
from app.routers import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API do MVP de gestao de clinica medica - AV2 Oxetech Academy, Equipe 01.\n\n"
        "Perfis: **PACIENTE** e **ATENDENTE**. Autenticacao JWT via `/api/auth/login` "
        "com login flexivel (CPF ou e-mail)."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_handlers(app)
app.include_router(api_router)


@app.get("/health", tags=["Infra"], summary="Healthcheck usado pelo Docker e pelo CI")
def health() -> dict[str, str]:
    return {"status": "healthy", "ambiente": settings.APP_ENV}
