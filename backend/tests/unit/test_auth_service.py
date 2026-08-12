"""Login flexivel CPF|e-mail e primeiro acesso / auto-cadastro (US-00, ADR-005)."""

import pytest
from pydantic import ValidationError

from app.core.security import gerar_hash_senha
from app.exceptions.dominio import (
    CredenciaisInvalidas,
    DadosDeAutoCadastroIncompletos,
    LoginJaAtivo,
)
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

    autenticacao = service.autenticar("529.982.247-25", "senha123")

    assert autenticacao.token.count(".") == 2
    assert autenticacao.tipo_usuario == "PACIENTE"


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

    autenticacao = service.autenticar("Recepcao@Clinica.COM", "admin123")

    assert autenticacao.token
    # O perfil sai do service junto com o token: o router nao consulta o banco de novo.
    assert autenticacao.tipo_usuario == "ATENDENTE"


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
def test_ca06_primeiro_acesso_com_login_ja_ativo_responde_409():
    """US-00 CA6 - CPF que ja tem login e conflito de estado (409), nao 401."""
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

    with pytest.raises(LoginJaAtivo) as erro:
        service.vincular_ou_criar(PrimeiroAcesso(cpf=CPF, senha="senha123"))

    assert erro.value.status_code == 409


@pytest.mark.unit
def test_ca05_auto_cadastro_sem_nome_e_telefone_responde_422():
    """US-00 CA5 - falta de dados obrigatorios e erro de validacao, nao de credencial."""
    service = AuthService(FakeUsuarioRepository(), FakePacienteRepository())

    with pytest.raises(DadosDeAutoCadastroIncompletos) as erro:
        service.vincular_ou_criar(PrimeiroAcesso(cpf=CPF, senha="senha123"))

    assert erro.value.status_code == 422


@pytest.mark.unit
@pytest.mark.parametrize("cpf_invalido", ["00000000000", "12345678900", "111", "abcdefghijk"])
def test_rn07_primeiro_acesso_recusa_cpf_com_digito_verificador_invalido(cpf_invalido):
    """RN07 - o auto-cadastro publico usa a mesma validacao de CPF da US-03."""
    with pytest.raises(ValidationError):
        PrimeiroAcesso(cpf=cpf_invalido, senha="senha123", nome="Fulano", telefone="8299990000")


@pytest.mark.unit
def test_rn07_primeiro_acesso_aceita_cpf_valido_com_mascara():
    """RN07 - CPF valido com mascara e normalizado para so digitos."""
    dados = PrimeiroAcesso(
        cpf="529.982.247-25", senha="senha123", nome="Fulano", telefone="8299990000"
    )

    assert dados.cpf == CPF


@pytest.mark.unit
def test_auto_cadastro_recusa_telefone_curto_como_na_us03():
    """Mesmo minimo de telefone de PacienteCriar - as duas portas de criacao sao iguais."""
    with pytest.raises(ValidationError):
        PrimeiroAcesso(cpf=CPF, senha="senha123", nome="Fulano", telefone="1")


@pytest.mark.unit
def test_ca07_credenciais_invalidas_lança_exceção():
    """US-00 CA7 - Credencial inválida deve lançar CredenciaisInvalidas com mensagem genérica."""
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

    # Usuario inexistente
    with pytest.raises(CredenciaisInvalidas) as exc_usuario_inexistente:
        service.autenticar("99999999999", "senha123")

    # Senha incorreta
    with pytest.raises(CredenciaisInvalidas) as exc_senha_incorreta:
        service.autenticar(CPF, "senha_errada")

    assert (
        str(exc_usuario_inexistente.value)
        == str(exc_senha_incorreta.value)
        == "Login ou senha invalidos"
    )
