"""Controller de autenticacao (US-00). So orquestra: nada de regra de negocio aqui."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.paciente_repository import PacienteRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth_schema import (
    LoginRequisicao,
    PrimeiroAcesso,
    TokenResposta,
    VerificarCpfResposta,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


def obter_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(UsuarioRepository(db), PacienteRepository(db))


@router.post("/login", response_model=TokenResposta, summary="Login por CPF ou e-mail")
def login(
    dados: LoginRequisicao,
    service: Annotated[AuthService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
) -> TokenResposta:
    token = service.autenticar(dados.login, dados.senha)
    db.commit()
    usuario = UsuarioRepository(db).buscar_por_login(
        AuthService._normalizar(dados.login)  # noqa: SLF001
    )
    return TokenResposta(access_token=token, tipo_usuario=usuario.tipo_usuario.value)


@router.get(
    "/verificar-cpf/{cpf}",
    response_model=VerificarCpfResposta,
    summary="Checa se o CPF ja tem cadastro e/ou login ativo",
)
def verificar_cpf(
    cpf: str, service: Annotated[AuthService, Depends(obter_service)]
) -> VerificarCpfResposta:
    return VerificarCpfResposta(**service.verificar_cpf(cpf))


@router.post(
    "/vincular-ou-criar",
    response_model=TokenResposta,
    status_code=201,
    summary="Primeiro acesso: ativa o login existente ou faz o auto-cadastro (ADR-005)",
)
def vincular_ou_criar(
    dados: PrimeiroAcesso,
    service: Annotated[AuthService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
) -> TokenResposta:
    token = service.vincular_ou_criar(dados)
    db.commit()
    return TokenResposta(access_token=token, tipo_usuario="PACIENTE")
