"""CTU05 - RN05 (bloqueio de alocacao dupla do mesmo medico)."""

from datetime import date, time

import pytest

from app.exceptions.dominio import MedicoJaAlocado, RecursoNaoEncontrado
from app.services.agenda_service import AgendaService
from tests.conftest import FakeHorarioRepository, FakeMedicoRepository


@pytest.mark.unit
def test_ctu05_deve_bloquear_slot_duplicado_para_o_mesmo_medico(medico, slot_livre):
    """RN05 - Dr. Silva ja tem 14:00 no dia 12/08; nao pode cadastrar de novo."""
    service = AgendaService(FakeHorarioRepository([slot_livre]), FakeMedicoRepository([medico]))

    with pytest.raises(MedicoJaAlocado) as erro:
        service.cadastrar_slots(medico.id, date(2026, 8, 12), [time(14, 0)])

    assert "ja possui consulta agendada" in erro.value.mensagem


@pytest.mark.unit
def test_cadastra_multiplos_slots_no_mesmo_dia(medico):
    """US-05 - lancar 09:00, 10:00 e 11:00 de uma vez."""
    service = AgendaService(FakeHorarioRepository(), FakeMedicoRepository([medico]))

    slots = service.cadastrar_slots(
        medico.id, date(2026, 8, 10), [time(9, 0), time(10, 0), time(11, 0)]
    )

    assert len(slots) == 3
    assert all(s.disponivel for s in slots)


@pytest.mark.unit
def test_falha_ao_lancar_agenda_de_medico_inexistente():
    service = AgendaService(FakeHorarioRepository(), FakeMedicoRepository([]))

    with pytest.raises(RecursoNaoEncontrado):
        service.cadastrar_slots(999, date(2026, 8, 10), [time(9, 0)])


@pytest.mark.unit
def test_rn09_horario_comercial_valida_grade():
    """US-05 / RN09 - O schema GradeHorariaCriar bloqueia horarios fora de 08:00-18:00."""
    from pydantic import ValidationError

    from app.schemas.agenda_schema import GradeHorariaCriar

    with pytest.raises(ValidationError) as erro:
        GradeHorariaCriar(data=date(2026, 8, 10), horarios=[time(7, 0), time(19, 0)])

    assert "Horarios fora do funcionamento" in str(erro.value)
