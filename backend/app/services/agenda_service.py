"""Regras da grade horaria dos medicos (US-05, US-07)."""

from datetime import date, time

from app.exceptions.dominio import MedicoJaAlocado, RecursoNaoEncontrado
from app.models.horario_disponivel import HorarioDisponivel
from app.models.medico import Medico
from app.repositories.horario_repository import HorarioRepository
from app.repositories.medico_repository import MedicoRepository


class AgendaService:
    def __init__(self, horarios: HorarioRepository, medicos: MedicoRepository):
        self.horarios = horarios
        self.medicos = medicos

    def cadastrar_slots(
        self, medico_id: int, data: date, horarios: list[time]
    ) -> list[HorarioDisponivel]:
        """US-05 (CA1, CA2). Valida existencia do medico e cadastra os slots da grade horaria."""
        self._garantir_medico_existe(medico_id)
        return [self._criar_slot(medico_id, data, horario) for horario in horarios]

    def listar_livres(self, medico_id: int, data: date) -> list[HorarioDisponivel]:
        """US-07 / RN03. Medico inativo nao oferece horario (RN16)."""
        medico = self._garantir_medico_existe(medico_id)
        if not medico.ativo:
            return []
        return self.horarios.listar_livres(medico_id, data)

    # --- privados ---

    def _criar_slot(self, medico_id: int, data: date, horario: time) -> HorarioDisponivel:
        if self.horarios.buscar_slot(medico_id, data, horario):
            raise MedicoJaAlocado  # RN05
        return self.horarios.salvar(
            HorarioDisponivel(medico_id=medico_id, data=data, horario=horario, disponivel=True)
        )

    def _garantir_medico_existe(self, medico_id: int) -> Medico:
        medico = self.medicos.buscar_por_id(medico_id)
        if medico is None:
            raise RecursoNaoEncontrado("Medico nao encontrado")
        return medico
