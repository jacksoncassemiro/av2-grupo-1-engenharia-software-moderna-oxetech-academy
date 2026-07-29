"""CTU03 e CTU04 - RN03 (slot ocupado) e RN04 (24h de antecedencia)."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.core.config import settings
from app.exceptions.dominio import (
    CancelamentoNaoPermitido,
    HorarioIndisponivel,
    TransicaoDeStatusInvalida,
)
from app.models.enums import StatusConsulta, TipoUsuario
from app.repositories import consulta_repository  # noqa: F401 - garante import da camada
from app.services.consulta_service import ConsultaService
from tests.conftest import FakeConsultaRepository, FakeHorarioRepository, montar_consulta

FUSO = ZoneInfo(settings.TIMEZONE)


@pytest.mark.unit
def test_ctu03_deve_bloquear_agendamento_em_horario_ja_ocupado(slot_livre):
    """RN03 - slot com consulta ativa nao pode ser reservado de novo."""
    consulta_existente = montar_consulta(slot_livre, StatusConsulta.CONFIRMADA)
    slot_livre.disponivel = False
    service = ConsultaService(
        FakeConsultaRepository([consulta_existente]), FakeHorarioRepository([slot_livre])
    )

    with pytest.raises(HorarioIndisponivel) as erro:
        service.agendar(paciente_id=2, horario_id=slot_livre.id, solicitado_por=TipoUsuario.PACIENTE)

    assert erro.value.status_code == 409


@pytest.mark.unit
def test_ctu04_deve_bloquear_cancelamento_do_paciente_com_menos_de_24h(slot_livre):
    """RN04 - consulta 12h a frente nao pode ser cancelada pelo paciente."""
    consulta = montar_consulta(slot_livre)  # 2026-08-12 14:00
    service = ConsultaService(FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre]))
    agora = datetime(2026, 8, 12, 2, 0, tzinfo=FUSO)  # faltam 12h

    with pytest.raises(CancelamentoNaoPermitido):
        service.cancelar(consulta.id, TipoUsuario.PACIENTE, agora=agora)

    assert consulta.status is StatusConsulta.CONFIRMADA


@pytest.mark.unit
def test_paciente_pode_cancelar_com_mais_de_24h_e_slot_e_liberado(slot_livre):
    """RN04 + RN03 - cancelamento valido devolve o slot para a agenda."""
    slot_livre.disponivel = False
    consulta = montar_consulta(slot_livre)
    service = ConsultaService(FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre]))
    agora = datetime(2026, 8, 10, 14, 0, tzinfo=FUSO)  # faltam 48h

    service.cancelar(consulta.id, TipoUsuario.PACIENTE, motivo="Imprevisto", agora=agora)

    assert consulta.status is StatusConsulta.CANCELADA
    assert slot_livre.disponivel is True


@pytest.mark.unit
def test_atendente_cancela_ignorando_a_regra_de_24h(slot_livre):
    """US-12 - Strategy do atendente nao valida prazo."""
    consulta = montar_consulta(slot_livre)
    service = ConsultaService(FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre]))
    agora = datetime(2026, 8, 12, 12, 0, tzinfo=FUSO)  # faltam 2h

    service.cancelar(consulta.id, TipoUsuario.ATENDENTE, agora=agora)

    assert consulta.status is StatusConsulta.CANCELADA


@pytest.mark.unit
def test_nao_permite_cancelar_consulta_ja_finalizada(slot_livre):
    """RN10 - FINALIZADA e estado terminal."""
    consulta = montar_consulta(slot_livre, StatusConsulta.FINALIZADA)
    service = ConsultaService(FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre]))

    with pytest.raises(TransicaoDeStatusInvalida):
        service.cancelar(consulta.id, TipoUsuario.ATENDENTE)


@pytest.mark.unit
def test_status_inicial_depende_de_quem_agenda(slot_livre):
    """US-08 vs US-09 - paciente gera SOLICITADA, atendente gera CONFIRMADA."""
    horarios = FakeHorarioRepository([slot_livre])
    service = ConsultaService(FakeConsultaRepository(), horarios)

    solicitada = service.agendar(1, slot_livre.id, TipoUsuario.PACIENTE)
    assert solicitada.status is StatusConsulta.SOLICITADA

    slot_livre.disponivel = True
    solicitada.status = StatusConsulta.CANCELADA  # libera o slot para o segundo agendamento
    confirmada = service.agendar(1, slot_livre.id, TipoUsuario.ATENDENTE)
    assert confirmada.status is StatusConsulta.CONFIRMADA
