"""Controller de medicos e da agenda deles (US-02, US-05, US-06, US-07)."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import UsuarioAutenticado, exigir_atendente, usuario_atual
from app.repositories.especialidade_repository import EspecialidadeRepository
from app.repositories.horario_repository import HorarioRepository
from app.repositories.medico_repository import MedicoRepository
from app.schemas.agenda_schema import GradeHorariaCriar, HorarioResposta
from app.schemas.medico_schema import MedicoCriar, MedicoResposta
from app.services.agenda_service import AgendaService
from app.services.medico_service import MedicoService

router = APIRouter(prefix="/medicos", tags=["Medicos e Agenda"])


def obter_medico_service(db: Annotated[Session, Depends(get_db)]) -> MedicoService:
    return MedicoService(MedicoRepository(db), EspecialidadeRepository(db))


def obter_agenda_service(db: Annotated[Session, Depends(get_db)]) -> AgendaService:
    return AgendaService(HorarioRepository(db), MedicoRepository(db))


@router.post("", response_model=MedicoResposta, status_code=201, summary="US-02")
def cadastrar(
    dados: MedicoCriar,
    service: Annotated[MedicoService, Depends(obter_medico_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> MedicoResposta:
    medico = service.cadastrar(dados)
    db.commit()
    return MedicoResposta.model_validate(medico)


@router.get("", response_model=list[MedicoResposta], summary="US-06")
def listar(
    service: Annotated[MedicoService, Depends(obter_medico_service)],
    _: Annotated[UsuarioAutenticado, Depends(usuario_atual)],
    especialidade_id: Annotated[int | None, Query()] = None,
    apenas_ativos: Annotated[
        bool | None,
        Query(description="Filtrar status: True=ativos, False=inativos, None=todos"),
    ] = None,
) -> list[MedicoResposta]:
    return [
        MedicoResposta.model_validate(m)
        for m in service.listar_ativos(especialidade_id, apenas_ativos=apenas_ativos)
    ]


@router.patch("/{medico_id}/status", response_model=MedicoResposta)
def alternar_status(
    medico_id: int,
    service: Annotated[MedicoService, Depends(obter_medico_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> MedicoResposta:
    medico = service.alternar_status(medico_id)
    db.commit()
    return MedicoResposta.model_validate(medico)


@router.post(
    "/{medico_id}/agenda",
    response_model=list[HorarioResposta],
    status_code=201,
    summary="US-05",
)
def cadastrar_grade(
    medico_id: int,
    dados: GradeHorariaCriar,
    service: Annotated[AgendaService, Depends(obter_agenda_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> list[HorarioResposta]:
    slots = service.cadastrar_slots(medico_id, dados.data, dados.horarios)
    db.commit()
    return [HorarioResposta.model_validate(s) for s in slots]


@router.get(
    "/{medico_id}/horarios-livres",
    response_model=list[HorarioResposta],
    summary="US-07",
)
def listar_horarios_livres(
    medico_id: int,
    data: Annotated[date, Query(description="AAAA-MM-DD")],
    service: Annotated[AgendaService, Depends(obter_agenda_service)],
    _: Annotated[UsuarioAutenticado, Depends(usuario_atual)],
) -> list[HorarioResposta]:
    return [HorarioResposta.model_validate(s) for s in service.listar_livres(medico_id, data)]
