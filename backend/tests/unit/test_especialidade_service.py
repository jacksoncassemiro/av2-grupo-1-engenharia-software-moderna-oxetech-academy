"""Testes unitarios para o cadastro e listagem de especialidades (US-01, US-06)."""

import pytest

from app.exceptions.dominio import RegraDeNegocioViolada
from app.models.especialidade import Especialidade
from app.services.especialidade_service import EspecialidadeService


class FakeEspecialidadeRepository:
    def __init__(self, itens: list[Especialidade] | None = None):
        self._itens = list(itens or [])

    def buscar_por_nome(self, nome: str) -> Especialidade | None:
        nome_norm = nome.strip().lower()
        return next((e for e in self._itens if e.nome.strip().lower() == nome_norm), None)

    def listar_ativas(self) -> list[Especialidade]:
        return [e for e in self._itens if e.ativo]

    def salvar(self, entidade: Especialidade) -> Especialidade:
        if entidade.ativo is None:
            entidade.ativo = True
        if entidade not in self._itens:
            entidade.id = len(self._itens) + 1
            self._itens.append(entidade)
        return entidade


@pytest.mark.unit
def test_cadastrar_especialidade_com_sucesso():
    """US-01 CA1 - Cadastro de especialidade valida criação."""
    repo = FakeEspecialidadeRepository()
    service = EspecialidadeService(repo)

    especialidade = service.cadastrar("Cardiologia")

    assert especialidade.id == 1
    assert especialidade.nome == "Cardiologia"
    assert especialidade.ativo is True


@pytest.mark.unit
def test_bloquear_cadastro_especialidade_duplicada_case_insensitive():
    """US-01 CA2 - Nome duplicado (case-insensitive) deve ser recusado com erro de dominio."""
    existente = Especialidade(id=1, nome="Cardiologia", ativo=True)
    repo = FakeEspecialidadeRepository([existente])
    service = EspecialidadeService(repo)

    with pytest.raises(RegraDeNegocioViolada, match="Especialidade ja cadastrada"):
        service.cadastrar("cardiologia")


@pytest.mark.unit
def test_listar_apenas_especialidades_ativas():
    """US-01 CA3 / US-06 - Deve listar apenas especialidades com ativo = True."""
    esp1 = Especialidade(id=1, nome="Cardiologia", ativo=True)
    esp2 = Especialidade(id=2, nome="Dermatologia Inativa", ativo=False)
    repo = FakeEspecialidadeRepository([esp1, esp2])
    service = EspecialidadeService(repo)

    resultado = service.listar_ativas()

    assert len(resultado) == 1
    assert resultado[0].nome == "Cardiologia"
