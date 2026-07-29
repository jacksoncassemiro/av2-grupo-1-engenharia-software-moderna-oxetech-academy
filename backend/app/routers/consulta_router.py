"""Controller de consultas do paciente (US-08, US-10, US-11)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
    return ConsultaResposta.model_validate(consulta)


@router.get("", response_model=list[ConsultaResposta], summary="US-10")
def minhas_consultas(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[UsuarioAutenticado, Depends(exigir_paciente)],
) -> list[ConsultaResposta]:
    return [
        ConsultaResposta.model_validate(c)
        for c in ConsultaRepository(db).listar_por_paciente(usuario.paciente_id)
    ]


@router.patch("/{consulta_id}/cancelar", response_model=ConsultaResposta, summary="US-11 / RN04")
def cancelar(
    consulta_id: int,
    dados: ConsultaCancelar,
    service: Annotated[ConsultaService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_paciente)],
) -> ConsultaResposta:
    consulta = service.cancelar(consulta_id, TipoUsuario.PACIENTE, dados.motivo)
    db.commit()
    return ConsultaResposta.model_validate(consulta)
