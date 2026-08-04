"""Testes unitarios para o cadastro e listagem de especialidades (US-01, US-06)."""

import pytest

from app.exceptions.dominio import EspecialidadeDuplicada, RegraDeNegocioViolada
from app.models.especialidade import Especialidade
from app.services.especialidade_service import EspecialidadeService


class FakeEspecialidadeRepository:
    def __init__(self, itens: list[Especialidade] | None = None):
        self._itens = list(itens or [])

    def buscar_por_id(self, id_: int) -> Especialidade | None:
        return next((e for e in self._itens if e.id == id_), None)

    def buscar_por_nome(self, nome: str) -> Especialidade | None:
        nome_norm = nome.strip().lower()
        return next((e for e in self._itens if e.nome.strip().lower() == nome_norm), None)

    def listar_ativas(self, apenas_ativas: bool = True) -> list[Especialidade]:
        if apenas_ativas:
            return [e for e in self._itens if e.ativo]
        return list(self._itens)

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
    """US-01 CA2 - Nome duplicado (case-insensitive) deve dar erro 409 (EspecialidadeDuplicada)."""
    existente = Especialidade(id=1, nome="Cardiologia", ativo=True)
    repo = FakeEspecialidadeRepository([existente])
    service = EspecialidadeService(repo)

    with pytest.raises(EspecialidadeDuplicada) as exc_info:
        service.cadastrar("cardiologia")

    assert exc_info.value.status_code == 409
    assert exc_info.value.mensagem == "Especialidade ja cadastrada"


@pytest.mark.unit
def test_bloquear_cadastro_nome_vazio_ou_curto_apos_strip():
    """Valida que nome com menos de 3 caracteres apos strip e recusado."""
    repo = FakeEspecialidadeRepository()
    service = EspecialidadeService(repo)

    with pytest.raises(
        RegraDeNegocioViolada, match="Nome da especialidade deve ter ao menos 3 caracteres"
    ):
        service.cadastrar("   ab   ")


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


@pytest.mark.unit
def test_alternar_status_especialidade():
    """Valida alternancia de status ativo/inativo de uma especialidade."""
    esp = Especialidade(id=1, nome="Cardiologia", ativo=True)
    repo = FakeEspecialidadeRepository([esp])
    service = EspecialidadeService(repo)

    atualizado = service.alternar_status(1)
    assert atualizado.ativo is False

    reativado = service.alternar_status(1)
    assert reativado.ativo is True
