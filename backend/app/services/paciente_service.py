"""Regras de negocio de paciente. Nao conhece HTTP nem SQLAlchemy."""

from app.exceptions.dominio import CpfDuplicado, EmailDuplicado, RecursoNaoEncontrado
from app.models.paciente import Paciente
from app.repositories.paciente_repository import PacienteRepository
from app.schemas.paciente_schema import PacienteAtualizar, PacienteCriar


class PacienteService:
    def __init__(self, repositorio: PacienteRepository):
        self.repositorio = repositorio

    def cadastrar(self, dados: PacienteCriar) -> Paciente:
        """US-03. Funcao pequena que delega cada validacao (Clean Code pratica 2)."""
        self._garantir_cpf_inedito(dados.cpf)
        self._garantir_email_inedito(dados.email)
        return self.repositorio.salvar(Paciente(**dados.model_dump()))

    def atualizar(self, paciente_id: int, dados: PacienteAtualizar) -> Paciente:
        """US-04."""
        paciente = self._buscar_ou_falhar(paciente_id)
        alteracoes = dados.model_dump(exclude_unset=True)

        if "email" in alteracoes:
            self._garantir_email_inedito(alteracoes["email"], ignorar_id=paciente_id)

        for campo, valor in alteracoes.items():
            setattr(paciente, campo, valor)
        return self.repositorio.salvar(paciente)

    # --- validacoes privadas ---

    def _garantir_cpf_inedito(self, cpf: str) -> None:
        """RN01."""
        if self.repositorio.buscar_por_cpf(cpf):
            raise CpfDuplicado

    def _garantir_email_inedito(self, email: str | None, ignorar_id: int | None = None) -> None:
        """RN02. E-mail nulo nao colide (paciente de balcao pode nao ter e-mail)."""
        if email is None:
            return
        existente = self.repositorio.buscar_por_email(email)
        if existente and existente.id != ignorar_id:
            raise EmailDuplicado

    def _buscar_ou_falhar(self, paciente_id: int) -> Paciente:
        paciente = self.repositorio.buscar_por_id(paciente_id)
        if paciente is None:
            raise RecursoNaoEncontrado("Paciente nao encontrado")
        return paciente
