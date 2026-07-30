"""Login flexivel CPF|e-mail e primeiro acesso / auto-cadastro (US-00, ADR-005)."""

import pytest

from app.core.security import gerar_hash_senha
from app.exceptions.dominio import CredenciaisInvalidas
from app.models.enums import TipoUsuario
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.schemas.auth_schema import PrimeiroAcesso
from app.services.auth_service import AuthService
from tests.conftest import FakePacienteRepository

CPF = "52998224725"


class FakeUsuarioRepository:
    def __init__(self, usuarios: list[Usuario] | None = None):
        self._itens = list(usuarios or [])

    def buscar_por_login(self, login):
        return next((u for u in self._itens if u.login == login), None)

    def buscar_por_paciente_id(self, paciente_id):
        return next((u for u in self._itens if u.paciente_id == paciente_id), None)

    def salvar(self, entidade):
        if entidade not in self._itens:
            entidade.id = len(self._itens) + 1
            self._itens.append(entidade)
        return entidade


@pytest.mark.unit
def test_paciente_loga_com_cpf_formatado():
    """US-00 - '529.982.247-25' e '52998224725' devem ser o mesmo login."""
    usuario = Usuario(
        id=1,
        nome="Joao",
        login=CPF,
        senha_hash=gerar_hash_senha("senha123"),
        tipo_usuario=TipoUsuario.PACIENTE,
        paciente_id=1,
        ativo=True,
    )
    service = AuthService(FakeUsuarioRepository([usuario]), FakePacienteRepository())

    token = service.autenticar("529.982.247-25", "senha123")

    assert isinstance(token, str) and token.count(".") == 2


@pytest.mark.unit
def test_atendente_loga_com_email_case_insensitive():
    usuario = Usuario(
        id=1,
        nome="Recepcao",
        login="recepcao@clinica.com",
        senha_hash=gerar_hash_senha("admin123"),
        tipo_usuario=TipoUsuario.ATENDENTE,
        ativo=True,
    )
    service = AuthService(FakeUsuarioRepository([usuario]), FakePacienteRepository())

    assert service.autenticar("Recepcao@Clinica.COM", "admin123")


@pytest.mark.unit
def test_primeiro_acesso_ativa_login_de_paciente_cadastrado_pelo_atendente():
    """US-00 - paciente de balcao cria a propria senha."""
    paciente = Paciente(id=1, nome="Joao", cpf=CPF, telefone="8299990000")
    service = AuthService(FakeUsuarioRepository(), FakePacienteRepository([paciente]))

    token = service.vincular_ou_criar(PrimeiroAcesso(cpf=CPF, senha="senha123"))

    assert token
    assert service.verificar_cpf(CPF) == {
        "cadastro_existe": True,
        "login_ativo": True,
        "nome": "Joao",
    }


@pytest.mark.unit
def test_auto_cadastro_cria_paciente_e_credencial_no_mesmo_fluxo():
    """ADR-005 - CPF inedito no primeiro acesso vira cadastro completo."""
    pacientes = FakePacienteRepository()
    service = AuthService(FakeUsuarioRepository(), pacientes)

    token = service.vincular_ou_criar(
        PrimeiroAcesso(
            cpf=CPF,
            senha="senha123",
            nome="Maria Souza",
            telefone="8298887777",
            email="maria@email.com",
        )
    )

    assert token
    assert pacientes.buscar_por_cpf(CPF).nome == "Maria Souza"


@pytest.mark.unit
def test_primeiro_acesso_falha_se_login_ja_existe():
    paciente = Paciente(id=1, nome="Joao", cpf=CPF, telefone="8299990000")
    usuario = Usuario(
        id=1,
        nome="Joao",
        login=CPF,
        senha_hash="x",
        tipo_usuario=TipoUsuario.PACIENTE,
        paciente_id=1,
    )
    service = AuthService(FakeUsuarioRepository([usuario]), FakePacienteRepository([paciente]))

    with pytest.raises(CredenciaisInvalidas):
        service.vincular_ou_criar(PrimeiroAcesso(cpf=CPF, senha="senha123"))
