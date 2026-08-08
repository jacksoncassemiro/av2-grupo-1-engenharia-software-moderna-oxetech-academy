"""CTU03 e CTU04 - RN03 (slot ocupado) e RN04 (24h de antecedencia)."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.core.config import settings
from app.exceptions.dominio import (
    CancelamentoNaoPermitido,
    HorarioIndisponivel,
    MedicoInativo,
    RecursoNaoEncontrado,
    TransicaoDeStatusInvalida,
)
from app.models.enums import StatusConsulta, TipoUsuario
from app.repositories import consulta_repository  # noqa: F401 - garante import da camada
from app.schemas.consulta_schema import _pode_cancelar  # noqa: PLC2701
from app.services.cancelamento_strategy import CancelamentoPorPaciente
from app.services.consulta_service import ConsultaService
from tests.conftest import FakeConsultaRepository, FakeHorarioRepository, montar_consulta

FUSO = ZoneInfo(settings.TIMEZONE)


@pytest.mark.unit
def test_ctu03_deve_bloquear_agendamento_em_horario_ja_ocupado(slot_livre):
    """RN03 - slot com consulta ativa nao pode ser reservado de novo."""
    consulta_existente = montar_consulta(slot_livre, StatusConsulta.CONFIRMADA)
    slot_livre.disponivel = False
    service = ConsultaService(
        FakeConsultaRepository([consulta_existente]),
        FakeHorarioRepository([slot_livre]),
    )

    with pytest.raises(HorarioIndisponivel) as erro:
        service.agendar(
            paciente_id=2, horario_id=slot_livre.id, solicitado_por=TipoUsuario.PACIENTE
        )

    assert erro.value.status_code == 409


@pytest.mark.unit
def test_ctu04_deve_bloquear_cancelamento_do_paciente_com_menos_de_24h(slot_livre):
    """RN04 - consulta 12h a frente nao pode ser cancelada pelo paciente."""
    consulta = montar_consulta(slot_livre)  # 2026-08-12 14:00
    service = ConsultaService(
        FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre])
    )
    agora = datetime(2026, 8, 12, 2, 0, tzinfo=FUSO)  # faltam 12h

    with pytest.raises(CancelamentoNaoPermitido):
        service.cancelar(consulta.id, TipoUsuario.PACIENTE, agora=agora)

    assert consulta.status is StatusConsulta.CONFIRMADA


@pytest.mark.unit
def test_paciente_pode_cancelar_com_mais_de_24h_e_slot_e_liberado(slot_livre):
    """RN04 + RN03 - cancelamento valido devolve o slot para a agenda."""
    slot_livre.disponivel = False
    consulta = montar_consulta(slot_livre)
    service = ConsultaService(
        FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre])
    )
    agora = datetime(2026, 8, 10, 14, 0, tzinfo=FUSO)  # faltam 48h

    service.cancelar(consulta.id, TipoUsuario.PACIENTE, motivo="Imprevisto", agora=agora)

    assert consulta.status is StatusConsulta.CANCELADA
    assert slot_livre.disponivel is True


@pytest.mark.unit
def test_us09_agendamento_atendente_gera_status_confirmada(slot_livre):
    """US-09 - Atendente agenda diretamente para o paciente, gerando status CONFIRMADA."""
    horarios = FakeHorarioRepository([slot_livre])
    service = ConsultaService(FakeConsultaRepository(), horarios)

    consulta = service.agendar(
        paciente_id=1, horario_id=slot_livre.id, solicitado_por=TipoUsuario.ATENDENTE
    )

    assert consulta.paciente_id == 1
    assert consulta.status is StatusConsulta.CONFIRMADA
    assert slot_livre.disponivel is False


@pytest.mark.unit
def test_atendente_cancela_ignorando_a_regra_de_24h(slot_livre):
    """US-12 - Strategy do atendente nao valida prazo."""
    consulta = montar_consulta(slot_livre)
    service = ConsultaService(
        FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre])
    )
    agora = datetime(2026, 8, 12, 12, 0, tzinfo=FUSO)  # faltam 2h

    service.cancelar(consulta.id, TipoUsuario.ATENDENTE, agora=agora)

    assert consulta.status is StatusConsulta.CANCELADA


@pytest.mark.unit
def test_nao_permite_cancelar_consulta_ja_finalizada(slot_livre):
    """RN10 - FINALIZADA e estado terminal."""
    consulta = montar_consulta(slot_livre, StatusConsulta.FINALIZADA)
    service = ConsultaService(
        FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre])
    )

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


@pytest.mark.unit
def test_us08_agendamento_paciente_sucesso(slot_livre):
    """US-08 - Paciente agenda consulta em slot livre, gerando status SOLICITADA e ocupando slot."""
    horarios = FakeHorarioRepository([slot_livre])
    service = ConsultaService(FakeConsultaRepository(), horarios)

    consulta = service.agendar(
        paciente_id=1, horario_id=slot_livre.id, solicitado_por=TipoUsuario.PACIENTE
    )

    assert consulta.paciente_id == 1
    assert consulta.status is StatusConsulta.SOLICITADA
    assert slot_livre.disponivel is False


@pytest.mark.unit
def test_rn16_nao_agenda_com_medico_inativado(slot_livre):
    """RN16 - medico inativado nao recebe consulta nova.

    Reproduzido na API antes da correcao: apos PATCH /medicos/{id}/status o medico
    sumia da listagem, mas POST /consultas no slot dele respondia 201.
    """
    slot_livre.medico.ativo = False
    service = ConsultaService(FakeConsultaRepository(), FakeHorarioRepository([slot_livre]))

    with pytest.raises(MedicoInativo) as erro:
        service.agendar(
            paciente_id=1, horario_id=slot_livre.id, solicitado_por=TipoUsuario.PACIENTE
        )

    assert erro.value.status_code == 409
    assert slot_livre.disponivel is True  # o slot nao pode ter sido consumido


@pytest.mark.unit
def test_rn16_atendente_tambem_nao_agenda_com_medico_inativado(slot_livre):
    """RN16 vale para os dois perfis: a regra e do dominio, nao da tela."""
    slot_livre.medico.ativo = False
    service = ConsultaService(FakeConsultaRepository(), FakeHorarioRepository([slot_livre]))

    with pytest.raises(MedicoInativo):
        service.agendar(
            paciente_id=1, horario_id=slot_livre.id, solicitado_por=TipoUsuario.ATENDENTE
        )


@pytest.mark.unit
def test_rn12_paciente_nao_cancela_consulta_de_outro_paciente(slot_livre):
    """RN12 - consulta de terceiro e tratada como inexistente (404), nunca vaza dado."""
    consulta = montar_consulta(slot_livre)  # paciente_id = 1
    service = ConsultaService(
        FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre])
    )

    with pytest.raises(RecursoNaoEncontrado) as erro:
        service.cancelar(consulta.id, TipoUsuario.PACIENTE, paciente_id=999)

    assert erro.value.status_code == 404
    assert consulta.status is StatusConsulta.CONFIRMADA


@pytest.mark.unit
def test_rn12_paciente_nao_detalha_consulta_de_outro_paciente(slot_livre):
    """RN12 - US-10 so mostra o proprio historico."""
    consulta = montar_consulta(slot_livre)  # paciente_id = 1
    service = ConsultaService(
        FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre])
    )

    assert service.detalhar_do_paciente(consulta.id, consulta.paciente_id) is consulta

    with pytest.raises(RecursoNaoEncontrado):
        service.detalhar_do_paciente(consulta.id, paciente_id=999)


@pytest.mark.unit
def test_rn04_prazo_de_cancelamento_vem_de_uma_unica_configuracao(slot_livre):
    """RN04 - o mesmo settings.CANCELAMENTO_ANTECEDENCIA_HORAS aplica a regra e alimenta
    o `pode_cancelar` da resposta. Se houvesse duas variaveis, a API responderia
    `pode_cancelar=True` para uma consulta que o service recusa cancelar.
    """
    consulta = montar_consulta(slot_livre)  # 2026-08-12 14:00
    service = ConsultaService(
        FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre])
    )
    agora = datetime(2026, 8, 12, 2, 0, tzinfo=FUSO)  # faltam 12h, menos que as 24h padrao

    pode_cancelar = _pode_cancelar(consulta, agora, settings.CANCELAMENTO_ANTECEDENCIA_HORAS)

    with pytest.raises(CancelamentoNaoPermitido):
        service.cancelar(consulta.id, TipoUsuario.PACIENTE, agora=agora)

    assert pode_cancelar is False  # a resposta concorda com a regra aplicada


@pytest.mark.unit
def test_rn04_mensagem_de_recusa_reflete_a_configuracao_e_nao_um_24_fixo(slot_livre):
    """RN04 - o prazo nunca e hardcoded; a mensagem acompanha a configuracao."""
    consulta = montar_consulta(slot_livre)
    strategy = CancelamentoPorPaciente(48)
    agora = datetime(2026, 8, 11, 14, 0, tzinfo=FUSO)  # faltam 24h, menos que as 48h exigidas

    with pytest.raises(CancelamentoNaoPermitido) as erro:
        strategy.validar(consulta, agora)

    assert "48 horas" in str(erro.value)


@pytest.mark.unit
def test_us13_mudar_status_consulta_valido_e_invalido(slot_livre):
    """US-13 - Valida transições de status válidas e rejeita inválidas."""
    consulta = montar_consulta(slot_livre, StatusConsulta.SOLICITADA)
    service = ConsultaService(
        FakeConsultaRepository([consulta]), FakeHorarioRepository([slot_livre])
    )

    # SOLICITADA -> CONFIRMADA
    atualizada = service.mudar_status(consulta.id, StatusConsulta.CONFIRMADA)
    assert atualizada.status is StatusConsulta.CONFIRMADA

    # CONFIRMADA -> FINALIZADA
    finalizada = service.mudar_status(consulta.id, StatusConsulta.FINALIZADA)
    assert finalizada.status is StatusConsulta.FINALIZADA

    # FINALIZADA -> CONFIRMADA (rejeitado)
    with pytest.raises(TransicaoDeStatusInvalida):
        service.mudar_status(consulta.id, StatusConsulta.CONFIRMADA)
