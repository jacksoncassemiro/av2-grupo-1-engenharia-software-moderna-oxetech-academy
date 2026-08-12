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


@pytest.mark.unit
def test_us07_listar_horarios_livres_retorna_apenas_slots_disponiveis(medico):
    """US-07 / RN03 - Retorna apenas slots com disponivel=True para a data e medico."""
    from app.models.horario_disponivel import HorarioDisponivel

    slot_livre = HorarioDisponivel(
        id=1, medico_id=medico.id, data=date(2026, 8, 12), horario=time(9, 0), disponivel=True
    )
    slot_ocupado = HorarioDisponivel(
        id=2, medico_id=medico.id, data=date(2026, 8, 12), horario=time(10, 0), disponivel=False
    )

    service = AgendaService(
        FakeHorarioRepository([slot_livre, slot_ocupado]), FakeMedicoRepository([medico])
    )

    livres = service.listar_livres(medico.id, date(2026, 8, 12))

    assert len(livres) == 1
    assert livres[0].horario == time(9, 0)


@pytest.mark.unit
def test_rn16_medico_inativado_nao_oferece_horario(medico):
    """RN16 - nao adianta esconder o medico da lista e continuar oferecendo a agenda dele."""
    from app.models.horario_disponivel import HorarioDisponivel

    medico.ativo = False
    slot = HorarioDisponivel(
        id=1, medico_id=medico.id, data=date(2026, 8, 12), horario=time(9, 0), disponivel=True
    )
    service = AgendaService(FakeHorarioRepository([slot]), FakeMedicoRepository([medico]))

    assert service.listar_livres(medico.id, date(2026, 8, 12)) == []


@pytest.mark.unit
def test_rn17_medico_de_especialidade_inativada_nao_oferece_horario(medico):
    """RN17 - mesma logica da RN16 pelo lado da especialidade."""
    from app.models.horario_disponivel import HorarioDisponivel

    medico.especialidade.ativo = False
    slot = HorarioDisponivel(
        id=1, medico_id=medico.id, data=date(2026, 8, 12), horario=time(9, 0), disponivel=True
    )
    service = AgendaService(FakeHorarioRepository([slot]), FakeMedicoRepository([medico]))

    assert service.listar_livres(medico.id, date(2026, 8, 12)) == []


@pytest.mark.unit
def test_us07_listar_horarios_livres_falha_se_medico_nao_existe():
    """US-07 - Listar horarios livres de medico inexistente lanca RecursoNaoEncontrado (404)."""
    service = AgendaService(FakeHorarioRepository(), FakeMedicoRepository([]))

    with pytest.raises(RecursoNaoEncontrado):
        service.listar_livres(999, date(2026, 8, 12))
