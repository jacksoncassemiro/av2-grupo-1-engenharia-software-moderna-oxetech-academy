"""Servico de especialidades (US-01, US-06)."""

from app.exceptions.dominio import (
    EspecialidadeDuplicada,
    RecursoNaoEncontrado,
    RegraDeNegocioViolada,
)
from app.models.especialidade import Especialidade
from app.repositories.especialidade_repository import EspecialidadeRepository


class EspecialidadeService:
    def __init__(self, repositorio: EspecialidadeRepository):
        self.repositorio = repositorio

    def cadastrar(self, nome: str) -> Especialidade:
        """Cadastra uma nova especialidade médica.

        RN12 - Autorização validada na controller via `exigir_atendente`.
        CA2 - Nome duplicado (case-insensitive) levanta EspecialidadeDuplicada (409).
        """
        nome_limpo = nome.strip()
        if len(nome_limpo) < 3:
            raise RegraDeNegocioViolada("Nome da especialidade deve ter ao menos 3 caracteres")

        if self.repositorio.buscar_por_nome(nome_limpo):
            raise EspecialidadeDuplicada()

        return self.repositorio.salvar(Especialidade(nome=nome_limpo))

    def listar_ativas(self) -> list[Especialidade]:
        """Listagem de especialidades ativas (US-06 / CA3 da US-01)."""
        return self.repositorio.listar_ativas()

    def alternar_status(self, especialidade_id: int) -> Especialidade:
        """Alterna o status ativo/inativo da especialidade."""
        especialidade = self.repositorio.buscar_por_id(especialidade_id)
        if especialidade is None:
            raise RecursoNaoEncontrado("Especialidade nao encontrada")
        especialidade.ativo = not especialidade.ativo
        return self.repositorio.salvar(especialidade)
