"""Testes unitarios para o cadastro e listagem de especialidades (US-01, US-06)."""

import pytest

from app.exceptions.dominio import EspecialidadeDuplicada, RegraDeNegocioViolada
from app.models.especialidade import Especialidade
from app.models.medico import Medico
from app.services.especialidade_service import EspecialidadeService


class FakeEspecialidadeRepository:
    def __init__(self, itens: list[Especialidade] | None = None):
        self._itens = list(itens or [])

    def buscar_por_id(self, id_: int) -> Especialidade | None:
        return next((e for e in self._itens if e.id == id_), None)

    def buscar_por_nome(self, nome: str) -> Especialidade | None:
        nome_norm = nome.strip().lower()
        return next((e for e in self._itens if e.nome.strip().lower() == nome_norm), None)

    def listar_ativas(self, apenas_ativas: bool | None = None) -> list[Especialidade]:
        if apenas_ativas is not None:
            return [e for e in self._itens if e.ativo is apenas_ativas]
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
def test_us01_descricao_enviada_e_persistida_e_nao_descartada():
    """US-01 - a API aceita `descricao` no corpo; ela nao pode ser perdida no caminho."""
    service = EspecialidadeService(FakeEspecialidadeRepository())

    criada = service.cadastrar("Dermatologia", "Cuida da pele, cabelos e unhas")

    assert criada.descricao == "Cuida da pele, cabelos e unhas"


@pytest.mark.unit
def test_us01_descricao_em_branco_vira_nula():
    """Evita gravar string vazia onde a coluna e opcional."""
    service = EspecialidadeService(FakeEspecialidadeRepository())

    assert service.cadastrar("Cardiologia", "   ").descricao is None
    assert service.cadastrar("Pediatria").descricao is None


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
def test_listar_especialidades_filtro_status_ativa_inativa_e_todas():
    """Sem filtro (apenas_ativas=None) retorna todas; True apenas ativas; False apenas inativas."""
    esp1 = Especialidade(id=1, nome="Cardiologia", ativo=True)
    esp2 = Especialidade(id=2, nome="Dermatologia Inativa", ativo=False)
    repo = FakeEspecialidadeRepository([esp1, esp2])
    service = EspecialidadeService(repo)

    # apenas_ativas=None -> Todas
    todas = service.listar_ativas(apenas_ativas=None)
    assert len(todas) == 2

    # apenas_ativas=True -> Apenas ativas
    ativas = service.listar_ativas(apenas_ativas=True)
    assert len(ativas) == 1
    assert ativas[0].nome == "Cardiologia"

    # apenas_ativas=False -> Apenas inativas
    inativas = service.listar_ativas(apenas_ativas=False)
    assert len(inativas) == 1
    assert inativas[0].nome == "Dermatologia Inativa"


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


@pytest.mark.unit
def test_rn17_inativar_especialidade_nao_cascateia_nos_medicos():
    """RN17 - decisao deliberada do PO (ADR-009): inativar preserva o passado.

    Inativar a especialidade so vira a flag dela. Os medicos vinculados continuam
    `ativo = True` e nenhuma consulta ja marcada muda de status — quem desmarca, caso
    a caso, e o atendente pela US-12. O que a RN17 barra e o agendamento novo, em
    `ConsultaService._reservar_slot` e `AgendaService.listar_livres`.
    """
    especialidade = Especialidade(id=1, nome="Cardiologia", ativo=True)
    medico = Medico(
        id=1,
        nome="Dr. Silva",
        email="silva@clinica.com",
        crm="CRM1",
        especialidade_id=1,
        ativo=True,
    )
    especialidade.medicos = [medico]
    service = EspecialidadeService(FakeEspecialidadeRepository([especialidade]))

    inativada = service.alternar_status(1)

    assert inativada.ativo is False
    assert medico.ativo is True
