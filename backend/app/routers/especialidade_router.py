"""Controller de especialidades (US-01, US-06)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import UsuarioAutenticado, exigir_atendente, usuario_atual
from app.exceptions.dominio import RegraDeNegocioViolada
from app.models.especialidade import Especialidade
from app.repositories.especialidade_repository import EspecialidadeRepository
from app.schemas.especialidade_schema import EspecialidadeCriar, EspecialidadeResposta

router = APIRouter(prefix="/especialidades", tags=["Especialidades"])


@router.post("", response_model=EspecialidadeResposta, status_code=201, summary="US-01")
def cadastrar(
    dados: EspecialidadeCriar,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],
) -> EspecialidadeResposta:
    repositorio = EspecialidadeRepository(db)
    if repositorio.buscar_por_nome(dados.nome):
        raise RegraDeNegocioViolada("Especialidade ja cadastrada")
    especialidade = repositorio.salvar(Especialidade(**dados.model_dump()))
    db.commit()
    return EspecialidadeResposta.model_validate(especialidade)


@router.get("", response_model=list[EspecialidadeResposta], summary="US-06")
def listar(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(usuario_atual)],
) -> list[EspecialidadeResposta]:
    return [
        EspecialidadeResposta.model_validate(e) for e in EspecialidadeRepository(db).listar_ativas()
    ]
