"""Testes unitarios para cadastro e listagem de medicos (US-02, US-06)."""

import pytest

from app.exceptions.dominio import CrmDuplicado, EmailDuplicado, RecursoNaoEncontrado
from app.models.especialidade import Especialidade
from app.models.medico import Medico
from app.schemas.medico_schema import MedicoCriar
from app.services.medico_service import MedicoService


class FakeMedicoRepository:
    def __init__(self, itens: list[Medico] | None = None):
        self._itens = list(itens or [])

    def buscar_por_id(self, id_: int) -> Medico | None:
        return next((m for m in self._itens if m.id == id_), None)

    def buscar_por_email(self, email: str) -> Medico | None:
        email_norm = email.strip().lower()
        return next((m for m in self._itens if m.email.strip().lower() == email_norm), None)

    def buscar_por_crm(self, crm: str) -> Medico | None:
        crm_norm = crm.strip().lower()
        return next((m for m in self._itens if m.crm.strip().lower() == crm_norm), None)

    def listar_ativos(
        self, especialidade_id: int | None = None, apenas_ativos: bool | None = None
    ) -> list[Medico]:
        resultado = list(self._itens)
        if apenas_ativos is not None:
            resultado = [m for m in resultado if m.ativo is apenas_ativos]
        if especialidade_id is not None:
            resultado = [m for m in resultado if m.especialidade_id == especialidade_id]
        return resultado

    def salvar(self, entidade: Medico) -> Medico:
        if entidade.ativo is None:
            entidade.ativo = True
        if entidade not in self._itens:
            entidade.id = len(self._itens) + 1
            self._itens.append(entidade)
        return entidade


class FakeEspecialidadeRepository:
    def __init__(self, itens: list[Especialidade] | None = None):
        self._itens = list(itens or [])

    def buscar_por_id(self, especialidade_id: int) -> Especialidade | None:
        return next((e for e in self._itens if e.id == especialidade_id), None)


@pytest.mark.unit
def test_cadastrar_medico_com_sucesso():
    """US-02 CA1 - Cadastro de médico com especialidade válida."""
    esp = Especialidade(id=1, nome="Cardiologia", ativo=True)
    service = MedicoService(FakeMedicoRepository(), FakeEspecialidadeRepository([esp]))

    dados = MedicoCriar(
        nome="Dr. Silva", email="silva@clinica.com", crm="CRM12345", especialidade_id=1
    )
    medico = service.cadastrar(dados)

    assert medico.id == 1
    assert medico.nome == "Dr. Silva"
    assert medico.crm == "CRM12345"
    assert medico.especialidade_id == 1
    assert medico.ativo is True


@pytest.mark.unit
def test_bloquear_cadastro_medico_sem_especialidade_valida():
    """US-02 CA1 - Médico sem especialidade cadastrada/ativa lança RecursoNaoEncontrado (404)."""
    service = MedicoService(FakeMedicoRepository(), FakeEspecialidadeRepository())

    dados = MedicoCriar(
        nome="Dr. Silva", email="silva@clinica.com", crm="CRM12345", especialidade_id=99
    )
    with pytest.raises(RecursoNaoEncontrado, match="Selecione uma especialidade"):
        service.cadastrar(dados)


@pytest.mark.unit
def test_bloquear_cadastro_medico_email_duplicado():
    """US-02 CA2 (RN02) - E-mail duplicado lança EmailDuplicado (409)."""
    esp = Especialidade(id=1, nome="Cardiologia", ativo=True)
    existente = Medico(
        id=1,
        nome="Dr. Antigo",
        email="silva@clinica.com",
        crm="CRM99999",
        especialidade_id=1,
        ativo=True,
    )
    service = MedicoService(FakeMedicoRepository([existente]), FakeEspecialidadeRepository([esp]))

    dados = MedicoCriar(
        nome="Dr. Novo", email="SILVA@clinica.com", crm="CRM12345", especialidade_id=1
    )
    with pytest.raises(EmailDuplicado):
        service.cadastrar(dados)


@pytest.mark.unit
def test_bloquear_cadastro_medico_crm_duplicado():
    """US-02 CA3 - CRM duplicado lança CrmDuplicado (409)."""
    esp = Especialidade(id=1, nome="Cardiologia", ativo=True)
    existente = Medico(
        id=1,
        nome="Dr. Antigo",
        email="antigo@clinica.com",
        crm="CRM12345",
        especialidade_id=1,
        ativo=True,
    )
    service = MedicoService(FakeMedicoRepository([existente]), FakeEspecialidadeRepository([esp]))

    dados = MedicoCriar(
        nome="Dr. Novo", email="novo@clinica.com", crm="crm12345", especialidade_id=1
    )
    with pytest.raises(CrmDuplicado):
        service.cadastrar(dados)


@pytest.mark.unit
def test_listar_medicos_ativos_com_filtro():
    """US-02 CA4 / US-06 - Listagem de médicos ativos com filtro por especialidade."""
    m1 = Medico(
        id=1,
        nome="Dr. Silva",
        email="silva@clinica.com",
        crm="CRM1",
        especialidade_id=1,
        ativo=True,
    )
    m2 = Medico(
        id=2,
        nome="Dr. Souza",
        email="souza@clinica.com",
        crm="CRM2",
        especialidade_id=2,
        ativo=True,
    )
    m3 = Medico(
        id=3,
        nome="Dr. Inativo",
        email="inativo@clinica.com",
        crm="CRM3",
        especialidade_id=1,
        ativo=False,
    )
    service = MedicoService(FakeMedicoRepository([m1, m2, m3]), FakeEspecialidadeRepository())

    ativos = service.listar_ativos(especialidade_id=1, apenas_ativos=True)
    assert len(ativos) == 1
    assert ativos[0].nome == "Dr. Silva"


@pytest.mark.unit
def test_us06_ca1_filtrar_medicos_por_especialidade():
    """US-06 CA1 - Filtra medicos pela especialidade especificada."""
    m1 = Medico(
        id=1,
        nome="Dr. Silva",
        email="silva@clinica.com",
        crm="CRM1",
        especialidade_id=1,
        ativo=True,
    )
    m2 = Medico(
        id=2,
        nome="Dra. Souza",
        email="souza@clinica.com",
        crm="CRM2",
        especialidade_id=2,
        ativo=True,
    )
    service = MedicoService(FakeMedicoRepository([m1, m2]), FakeEspecialidadeRepository())

    filtrados = service.listar_ativos(especialidade_id=1, apenas_ativos=True)
    assert len(filtrados) == 1
    assert filtrados[0].nome == "Dr. Silva"


@pytest.mark.unit
def test_listar_medicos_filtro_status_ativo_inativo_e_todos():
    """Filtra medicos por status: apenas_ativos=None (todos), True (ativos), False (inativos)."""
    m1 = Medico(
        id=1,
        nome="Dr. Silva",
        email="silva@clinica.com",
        crm="CRM1",
        especialidade_id=1,
        ativo=True,
    )
    m2 = Medico(
        id=2,
        nome="Dra. Souza",
        email="souza@clinica.com",
        crm="CRM2",
        especialidade_id=2,
        ativo=True,
    )
    m3 = Medico(
        id=3,
        nome="Dr. Inativo",
        email="inativo@clinica.com",
        crm="CRM3",
        especialidade_id=1,
        ativo=False,
    )
    service = MedicoService(FakeMedicoRepository([m1, m2, m3]), FakeEspecialidadeRepository())

    # apenas_ativos=None -> Todos
    todos = service.listar_ativos(especialidade_id=None, apenas_ativos=None)
    assert len(todos) == 3

    # apenas_ativos=True -> Apenas ativos
    ativos = service.listar_ativos(especialidade_id=None, apenas_ativos=True)
    assert len(ativos) == 2
    assert all(m.ativo for m in ativos)

    # apenas_ativos=False -> Apenas inativos
    inativos = service.listar_ativos(especialidade_id=None, apenas_ativos=False)
    assert len(inativos) == 1
    assert inativos[0].nome == "Dr. Inativo"


@pytest.mark.unit
def test_alternar_status_medico():
    """Valida alternancia de status ativo/inativo de um medico."""
    m1 = Medico(
        id=1,
        nome="Dr. Silva",
        email="silva@clinica.com",
        crm="CRM1",
        especialidade_id=1,
        ativo=True,
    )
    service = MedicoService(FakeMedicoRepository([m1]), FakeEspecialidadeRepository())

    inativado = service.alternar_status(1)
    assert inativado.ativo is False

    reativado = service.alternar_status(1)
    assert reativado.ativo is True


@pytest.mark.unit
def test_rn08_deve_rejeitar_email_em_formato_invalido():
    """RN08 - e-mail deve estar em formato valido (validacao no schema)."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        MedicoCriar(
            nome="Dr. Silva",
            email="email-invalido",
            crm="CRM12345",
            especialidade_id=1,
        )
