"""Servico de medicos (US-02, US-06)."""

from app.exceptions.dominio import CrmDuplicado, EmailDuplicado, RecursoNaoEncontrado
from app.models.medico import Medico
from app.repositories.especialidade_repository import EspecialidadeRepository
from app.repositories.medico_repository import MedicoRepository
from app.schemas.medico_schema import MedicoCriar


class MedicoService:
    def __init__(self, medicos: MedicoRepository, especialidades: EspecialidadeRepository):
        self.medicos = medicos
        self.especialidades = especialidades

    def cadastrar(self, dados: MedicoCriar) -> Medico:
        """Cadastra um novo médico.

        RN02 - Email unico (409).
        CA1 - Exige especialidade valida e ativa (404).
        CA3 - CRM unico (409).
        """
        especialidade = self.especialidades.buscar_por_id(dados.especialidade_id)
        if especialidade is None or not especialidade.ativo:
            raise RecursoNaoEncontrado("Selecione uma especialidade")

        if self.medicos.buscar_por_email(dados.email):
            raise EmailDuplicado()

        if self.medicos.buscar_por_crm(dados.crm):
            raise CrmDuplicado()

        medico = Medico(
            nome=dados.nome.strip(),
            email=str(dados.email).strip().lower(),
            crm=dados.crm.strip().upper(),
            especialidade_id=dados.especialidade_id,
            ativo=True,
        )
        return self.medicos.salvar(medico)

    def listar_ativos(
        self, especialidade_id: int | None = None, apenas_ativos: bool | None = None
    ) -> list[Medico]:
        """Listagem de médicos (US-06 / CA4 da US-02).
        
        Se apenas_ativos for None, retorna todos os médicos.
        Se True, apenas os ativos. Se False, apenas os inativos.
        """
        return self.medicos.listar_ativos(especialidade_id, apenas_ativos=apenas_ativos)

    def alternar_status(self, medico_id: int) -> Medico:
        """Alterna o status ativo/inativo do médico."""
        medico = self.medicos.buscar_por_id(medico_id)
        if medico is None:
            raise RecursoNaoEncontrado("Medico nao encontrado")
        medico.ativo = not medico.ativo
        return self.medicos.salvar(medico)
