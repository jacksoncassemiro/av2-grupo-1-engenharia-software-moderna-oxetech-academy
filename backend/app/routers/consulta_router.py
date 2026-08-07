"""Controller de consultas do paciente (US-08, US-10, US-11)."""

from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import UsuarioAutenticado, exigir_paciente
from app.models.enums import TipoUsuario
from app.repositories.consulta_repository import ConsultaRepository
from app.repositories.horario_repository import HorarioRepository
from app.schemas.consulta_schema import ConsultaCancelar, ConsultaResposta, ConsultaSolicitar
from app.services.consulta_service import ConsultaService

router = APIRouter(prefix="/consultas", tags=["Consultas (Paciente)"])


def obter_service(db: Annotated[Session, Depends(get_db)]) -> ConsultaService:
    return ConsultaService(ConsultaRepository(db), HorarioRepository(db))


@router.post("", response_model=ConsultaResposta, status_code=201, summary="US-08")
def solicitar(
    dados: ConsultaSolicitar,
    service: Annotated[ConsultaService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[UsuarioAutenticado, Depends(exigir_paciente)],
) -> ConsultaResposta:
    consulta = service.agendar(
        usuario.paciente_id, dados.horario_disponivel_id, TipoUsuario.PACIENTE
    )
    db.commit()
    agora = datetime.now(ZoneInfo(settings.TIMEZONE))
    return ConsultaResposta.de_consulta(consulta, agora, settings.CANCELAMENTO_ANTECEDENCIA_HORAS)


@router.get("", response_model=list[ConsultaResposta], summary="US-10")
def minhas_consultas(
    service: Annotated[ConsultaService, Depends(obter_service)],
    usuario: Annotated[UsuarioAutenticado, Depends(exigir_paciente)],
) -> list[ConsultaResposta]:
    agora = datetime.now(ZoneInfo(settings.TIMEZONE))
    return [
        ConsultaResposta.de_consulta(c, agora, settings.CANCELAMENTO_ANTECEDENCIA_HORAS)
        for c in service.listar_do_paciente(usuario.paciente_id)
    ]


@router.get("/{consulta_id}", response_model=ConsultaResposta, summary="US-10")
def detalhar_consulta(
    consulta_id: int,
    service: Annotated[ConsultaService, Depends(obter_service)],
    usuario: Annotated[UsuarioAutenticado, Depends(exigir_paciente)],
) -> ConsultaResposta:
    consulta = service.detalhar_do_paciente(consulta_id, usuario.paciente_id)
    agora = datetime.now(ZoneInfo(settings.TIMEZONE))
    return ConsultaResposta.de_consulta(consulta, agora, settings.CANCELAMENTO_ANTECEDENCIA_HORAS)


@router.patch("/{consulta_id}/cancelar", response_model=ConsultaResposta, summary="US-11 / RN04")
def cancelar(
    consulta_id: int,
    dados: ConsultaCancelar,
    service: Annotated[ConsultaService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[UsuarioAutenticado, Depends(exigir_paciente)],
) -> ConsultaResposta:
    consulta = service.cancelar(
        consulta_id,
        TipoUsuario.PACIENTE,
        dados.motivo,
        paciente_id=usuario.paciente_id,  # RN12 - so cancela a propria consulta
    )
    db.commit()
    agora = datetime.now(ZoneInfo(settings.TIMEZONE))
    return ConsultaResposta.de_consulta(consulta, agora, settings.CANCELAMENTO_ANTECEDENCIA_HORAS)
