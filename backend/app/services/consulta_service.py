"""Regras de agendamento, cancelamento e ciclo de vida da consulta."""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.exceptions.dominio import (
    HorarioIndisponivel,
    MedicoInativo,
    RecursoNaoEncontrado,
    TransicaoDeStatusInvalida,
)
from app.models.consulta import Consulta
from app.models.enums import TRANSICOES_PERMITIDAS, StatusConsulta, TipoUsuario
from app.repositories.consulta_repository import ConsultaRepository
from app.repositories.horario_repository import HorarioRepository
from app.services.cancelamento_strategy import obter_strategy


class ConsultaService:
    def __init__(self, consultas: ConsultaRepository, horarios: HorarioRepository):
        self.consultas = consultas
        self.horarios = horarios

    def agendar(self, paciente_id: int, horario_id: int, solicitado_por: TipoUsuario) -> Consulta:
        """US-08 (paciente -> SOLICITADA) e US-09 (atendente -> CONFIRMADA)."""
        slot = self._reservar_slot(horario_id)
        consulta = Consulta(
            paciente_id=paciente_id,
            medico_id=slot.medico_id,
            horario_disponivel_id=slot.id,
            status=self._status_inicial(solicitado_por),
        )
        return self.consultas.salvar(consulta)

    def listar_do_paciente(self, paciente_id: int, agora: datetime | None = None) -> list[Consulta]:
        """US-10 - o paciente so enxerga o proprio historico, futuras primeiro."""
        return self.consultas.listar_por_paciente(paciente_id, agora or self._agora())

    def detalhar_do_paciente(self, consulta_id: int, paciente_id: int) -> Consulta:
        """US-10 / RN12 - consulta de outro paciente responde 404, nunca vaza dado."""
        return self._buscar_do_paciente_ou_falhar(consulta_id, paciente_id)

    def listar_para_atendente(self, status: StatusConsulta | None = None) -> list[Consulta]:
        """US-13 / CA5 - o atendente ve tudo, com filtro opcional por status."""
        if status is None:
            return self.consultas.listar()
        return self.consultas.listar_por_status(status)

    def cancelar(
        self,
        consulta_id: int,
        perfil: TipoUsuario,
        motivo: str | None = None,
        agora: datetime | None = None,
        paciente_id: int | None = None,
    ) -> Consulta:
        """US-11 / US-12. A regra de prazo vem da Strategy, nao de um if.

        `paciente_id` restringe o cancelamento ao dono da consulta (RN12); o
        atendente cancela qualquer uma e por isso passa None.
        """
        consulta = (
            self._buscar_ou_falhar(consulta_id)
            if paciente_id is None
            else self._buscar_do_paciente_ou_falhar(consulta_id, paciente_id)
        )
        self._garantir_transicao(consulta.status, StatusConsulta.CANCELADA)

        strategy = obter_strategy(perfil, settings.CANCELAMENTO_ANTECEDENCIA_HORAS)
        strategy.validar(consulta, agora or self._agora())

        consulta.status = StatusConsulta.CANCELADA
        consulta.motivo_cancelamento = motivo
        consulta.horario.disponivel = True  # RN03 - libera o slot
        return self.consultas.salvar(consulta)

    def mudar_status(self, consulta_id: int, novo_status: StatusConsulta) -> Consulta:
        """US-13 - atendente confirma ou finaliza a consulta (RN06 / RN10)."""
        consulta = self._buscar_ou_falhar(consulta_id)
        self._garantir_transicao(consulta.status, novo_status)
        consulta.status = novo_status
        return self.consultas.salvar(consulta)

    # --- privados ---

    def _reservar_slot(self, horario_id: int):
        slot = self.horarios.buscar_para_reserva(horario_id)  # SELECT FOR UPDATE
        if slot is None:
            raise RecursoNaoEncontrado("Horario nao encontrado")
        if not slot.medico.ativo:
            raise MedicoInativo  # RN16
        if not slot.disponivel or self.consultas.existe_ativa_no_slot(slot.id):
            raise HorarioIndisponivel  # RN03
        slot.disponivel = False
        return slot

    @staticmethod
    def _status_inicial(solicitado_por: TipoUsuario) -> StatusConsulta:
        if solicitado_por is TipoUsuario.ATENDENTE:
            return StatusConsulta.CONFIRMADA
        return StatusConsulta.SOLICITADA

    @staticmethod
    def _garantir_transicao(atual: StatusConsulta, destino: StatusConsulta) -> None:
        if destino not in TRANSICOES_PERMITIDAS[atual]:
            raise TransicaoDeStatusInvalida(
                f"Nao e permitido ir de {atual.value} para {destino.value}"
            )

    @staticmethod
    def _agora() -> datetime:
        return datetime.now(ZoneInfo(settings.TIMEZONE))

    def _buscar_ou_falhar(self, consulta_id: int) -> Consulta:
        consulta = self.consultas.buscar_por_id(consulta_id)
        if consulta is None:
            raise RecursoNaoEncontrado("Consulta nao encontrada")
        return consulta

    def _buscar_do_paciente_ou_falhar(self, consulta_id: int, paciente_id: int) -> Consulta:
        """RN12 - consulta de outro paciente e tratada como inexistente."""
        consulta = self._buscar_ou_falhar(consulta_id)
        if consulta.paciente_id != paciente_id:
            raise RecursoNaoEncontrado("Consulta nao encontrada")
        return consulta
