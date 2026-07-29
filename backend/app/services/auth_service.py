"""Autenticacao com login flexivel: CPF (paciente) ou e-mail (atendente) - US-00."""

from app.core.security import criar_token_acesso, gerar_hash_senha, senha_confere
from app.exceptions.dominio import CredenciaisInvalidas, EmailDuplicado
from app.models.enums import TipoUsuario
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.repositories.paciente_repository import PacienteRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth_schema import PrimeiroAcesso


class AuthService:
    def __init__(self, usuarios: UsuarioRepository, pacientes: PacienteRepository):
        self.usuarios = usuarios
        self.pacientes = pacientes

    def autenticar(self, login: str, senha: str) -> str:
        """Devolve o JWT. `login` pode ser CPF (so digitos) ou e-mail."""
        usuario = self.usuarios.buscar_por_login(self._normalizar(login))
        if usuario is None or not usuario.ativo or not senha_confere(senha, usuario.senha_hash):
            raise CredenciaisInvalidas
        return criar_token_acesso(usuario.login, usuario.tipo_usuario.value, usuario.paciente_id)

    def verificar_cpf(self, cpf: str) -> dict:
        """US-00 - a tela de primeiro acesso pergunta antes de pedir a senha."""
        paciente = self.pacientes.buscar_por_cpf(self._so_digitos(cpf))
        if paciente is None:
            return {"cadastro_existe": False, "login_ativo": False, "nome": None}
        return {
            "cadastro_existe": True,
            "login_ativo": self.usuarios.buscar_por_paciente_id(paciente.id) is not None,
            "nome": paciente.nome,
        }

    def vincular_ou_criar(self, dados: PrimeiroAcesso) -> str:
        """US-00 - ativa o login de um paciente ja cadastrado OU faz o auto-cadastro.

        Este e o ponto que resolve o conflito do enunciado (ver ADR-005): o Case
        pede que o paciente se cadastre, a lista de funcionalidades da o cadastro
        ao atendente. Aqui os dois caminhos convergem no mesmo endpoint.
        """
        cpf = self._so_digitos(dados.cpf)
        paciente = self.pacientes.buscar_por_cpf(cpf)

        if paciente is None:
            paciente = self._auto_cadastrar(dados, cpf)
        elif self.usuarios.buscar_por_paciente_id(paciente.id) is not None:
            raise CredenciaisInvalidas("Este CPF ja possui login ativo. Use a tela de login.")

        usuario = self.usuarios.salvar(
            Usuario(
                nome=paciente.nome,
                login=cpf,
                senha_hash=gerar_hash_senha(dados.senha),
                tipo_usuario=TipoUsuario.PACIENTE,
                paciente_id=paciente.id,
            )
        )
        return criar_token_acesso(usuario.login, usuario.tipo_usuario.value, paciente.id)

    # --- privados ---

    def _auto_cadastrar(self, dados: PrimeiroAcesso, cpf: str) -> Paciente:
        if dados.nome is None or dados.telefone is None:
            raise CredenciaisInvalidas("Nome e telefone sao obrigatorios no auto-cadastro")
        if dados.email and self.pacientes.buscar_por_email(dados.email):
            raise EmailDuplicado  # RN02
        return self.pacientes.salvar(
            Paciente(nome=dados.nome, cpf=cpf, email=dados.email, telefone=dados.telefone)
        )

    @classmethod
    def _normalizar(cls, login: str) -> str:
        login = login.strip()
        return cls._so_digitos(login) if "@" not in login else login.lower()

    @staticmethod
    def _so_digitos(valor: str) -> str:
        return "".join(caractere for caractere in valor if caractere.isdigit())
