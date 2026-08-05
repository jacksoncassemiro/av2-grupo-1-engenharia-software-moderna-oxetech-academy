"""Dependencias de autenticacao e autorizacao por perfil (RF18 / RN12)."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.security import decodificar_token
from app.models.enums import TipoUsuario

http_bearer = HTTPBearer()


class UsuarioAutenticado:
    """Representa o usuario extraido do token - nao toca no banco."""

    def __init__(self, login: str, tipo_usuario: TipoUsuario, paciente_id: int | None):
        self.login = login
        self.tipo_usuario = tipo_usuario
        self.paciente_id = paciente_id


def usuario_atual(
    auth: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> UsuarioAutenticado:
    token = auth.credentials
    try:
        payload = decodificar_token(token)
    except JWTError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nao autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from erro

    return UsuarioAutenticado(
        login=payload["sub"],
        tipo_usuario=TipoUsuario(payload["tipo_usuario"]),
        paciente_id=payload.get("paciente_id"),
    )


def _exigir_perfil(perfil: TipoUsuario):
    def _dependencia(
        usuario: Annotated[UsuarioAutenticado, Depends(usuario_atual)],
    ) -> UsuarioAutenticado:
        if usuario.tipo_usuario is not perfil:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito ao perfil {perfil.value}",
            )
        return usuario

    return _dependencia


exigir_atendente = _exigir_perfil(TipoUsuario.ATENDENTE)
exigir_paciente = _exigir_perfil(TipoUsuario.PACIENTE)
