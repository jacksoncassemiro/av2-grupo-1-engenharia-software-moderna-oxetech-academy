"""Controller administrativo do atendente (US-09, US-12, US-13, US-14)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import UsuarioAutenticado, exigir_atendente
from app.models.enums import TipoUsuario
from app.repositories.consulta_repository import ConsultaRepository
from app.repositories.horario_repository import HorarioRepository
from app.schemas.consulta_schema import (
    ConsultaAgendarPorAtendente,
    ConsultaCancelar,
    ConsultaMudarStatus,
    ConsultaResposta,
)
from app.services.consulta_service import ConsultaService

router = APIRouter(prefix="/atendente", tags=["Consultas (Atendente)"])


def obter_service(db: Annotated[Session, Depends(get_db)]) -> ConsultaService:
    return ConsultaService(ConsultaRepository(db), HorarioRepository(db))


@router.post("/consultas", response_model=ConsultaResposta, status_code=201, summary="US-09")
def agendar_para_paciente(
    dados: ConsultaAgendarPorAtendente,
    service: Annotated[ConsultaService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> ConsultaResposta:
    consulta = service.agendar(
        dados.paciente_id, dados.horario_disponivel_id, TipoUsuario.ATENDENTE
    )
    db.commit()
    return ConsultaResposta.model_validate(consulta)


@router.patch("/consultas/{consulta_id}/cancelar", response_model=ConsultaResposta, summary="US-12")
def cancelar(
    consulta_id: int,
    dados: ConsultaCancelar,
    service: Annotated[ConsultaService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> ConsultaResposta:
    consulta = service.cancelar(consulta_id, TipoUsuario.ATENDENTE, dados.motivo)
    db.commit()
    return ConsultaResposta.model_validate(consulta)


@router.patch("/consultas/{consulta_id}/status", response_model=ConsultaResposta, summary="US-13")
def mudar_status(
    consulta_id: int,
    dados: ConsultaMudarStatus,
    service: Annotated[ConsultaService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> ConsultaResposta:
    consulta = service.mudar_status(consulta_id, dados.status)
    db.commit()
    return ConsultaResposta.model_validate(consulta)
