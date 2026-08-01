"""Servico de especialidades (US-01, US-06)."""

from app.exceptions.dominio import RegraDeNegocioViolada
from app.models.especialidade import Especialidade
from app.repositories.especialidade_repository import EspecialidadeRepository


class EspecialidadeService:
    def __init__(self, repositorio: EspecialidadeRepository):
        self.repositorio = repositorio

    def cadastrar(self, nome: str) -> Especialidade:
        """Cadastra uma nova especialidade médica.

        RN12 - Autorização validada na controller via `exigir_atendente`.
        CA2 - Nome duplicado (case-insensitive) levanta RegraDeNegocioViolada (409).
        """
        if self.repositorio.buscar_por_nome(nome):
            raise RegraDeNegocioViolada("Especialidade ja cadastrada")
        return self.repositorio.salvar(Especialidade(nome=nome.strip()))

    def listar_ativas(self) -> list[Especialidade]:
        """Listagem de especialidades ativas (US-06 / CA3 da US-01)."""
        return self.repositorio.listar_ativas()
