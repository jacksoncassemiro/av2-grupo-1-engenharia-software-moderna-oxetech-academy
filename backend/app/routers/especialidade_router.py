"""Controller de especialidades (US-01, US-06)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import UsuarioAutenticado, exigir_atendente, usuario_atual
from app.repositories.especialidade_repository import EspecialidadeRepository
from app.schemas.especialidade_schema import EspecialidadeCriar, EspecialidadeResposta
from app.services.especialidade_service import EspecialidadeService

router = APIRouter(prefix="/especialidades", tags=["Especialidades"])


def obter_service(db: Annotated[Session, Depends(get_db)]) -> EspecialidadeService:
    return EspecialidadeService(EspecialidadeRepository(db))


@router.post("", response_model=EspecialidadeResposta, status_code=201, summary="US-01")
def cadastrar(
    dados: EspecialidadeCriar,
    service: Annotated[EspecialidadeService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> EspecialidadeResposta:
    especialidade = service.cadastrar(dados.nome)
    db.commit()
    return EspecialidadeResposta.model_validate(especialidade)


@router.get("", response_model=list[EspecialidadeResposta], summary="US-06")
def listar(
    service: Annotated[EspecialidadeService, Depends(obter_service)],
    _: Annotated[UsuarioAutenticado, Depends(usuario_atual)],
    apenas_ativas: Annotated[
        bool | None,
        Query(description="Filtrar status: True=ativas, False=inativas, None=todas"),
    ] = None,
) -> list[EspecialidadeResposta]:
    return [
        EspecialidadeResposta.model_validate(e)
        for e in service.listar_ativas(apenas_ativas=apenas_ativas)
    ]


@router.patch("/{especialidade_id}/status", response_model=EspecialidadeResposta)
def alternar_status(
    especialidade_id: int,
    service: Annotated[EspecialidadeService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> EspecialidadeResposta:
    especialidade = service.alternar_status(especialidade_id)
    db.commit()
    return EspecialidadeResposta.model_validate(especialidade)
