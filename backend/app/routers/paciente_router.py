"""Controller de pacientes (US-03, US-04)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import UsuarioAutenticado, exigir_atendente, exigir_paciente
from app.repositories.paciente_repository import PacienteRepository
from app.schemas.paciente_schema import PacienteAtualizar, PacienteCriar, PacienteResposta
from app.services.paciente_service import PacienteService

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


def obter_service(db: Annotated[Session, Depends(get_db)]) -> PacienteService:
    return PacienteService(PacienteRepository(db))


@router.post("", response_model=PacienteResposta, status_code=201, summary="US-03")
def cadastrar(
    dados: PacienteCriar,
    service: Annotated[PacienteService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> PacienteResposta:
    paciente = service.cadastrar(dados)
    db.commit()
    return PacienteResposta.model_validate(paciente)


@router.get("", response_model=list[PacienteResposta], summary="US-03")
def listar(
    service: Annotated[PacienteService, Depends(obter_service)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> list[PacienteResposta]:
    pacientes = service.listar()
    return [PacienteResposta.model_validate(p) for p in pacientes]


@router.put("/me", response_model=PacienteResposta, summary="US-04")
def atualizar_meus_dados(
    dados: PacienteAtualizar,
    service: Annotated[PacienteService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[UsuarioAutenticado, Depends(exigir_paciente)],
) -> PacienteResposta:
    paciente = service.atualizar(usuario.paciente_id, dados)
    db.commit()
    return PacienteResposta.model_validate(paciente)
