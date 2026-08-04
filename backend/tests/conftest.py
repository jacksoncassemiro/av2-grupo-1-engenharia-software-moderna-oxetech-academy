"""Fixtures compartilhadas.

Os testes unitarios usam FAKES de repositorio (nao mocks cegos) - possivel porque
os Services dependem da abstracao Repository (ADR-006 / DIP do SOLID). Nenhum
teste unitario precisa de banco, o que os deixa rapidos e deterministicos.
"""

from datetime import date, time

import pytest

from app.models.consulta import Consulta
from app.models.enums import STATUS_QUE_OCUPAM_SLOT, StatusConsulta
from app.models.horario_disponivel import HorarioDisponivel
from app.models.medico import Medico
from app.models.paciente import Paciente


class FakePacienteRepository:
    def __init__(self, pacientes: list[Paciente] | None = None):
        self._itens = list(pacientes or [])
        self._proximo_id = len(self._itens) + 1

    def buscar_por_id(self, id_):
        return next((p for p in self._itens if p.id == id_), None)

    def buscar_por_cpf(self, cpf):
        return next((p for p in self._itens if p.cpf == cpf), None)

    def buscar_por_email(self, email):
        return next((p for p in self._itens if p.email == email), None)

    def listar(self):
        return list(self._itens)

    def salvar(self, entidade):
        if entidade.id is None:
            entidade.id = self._proximo_id
            self._proximo_id += 1
            self._itens.append(entidade)
        return entidade


class FakeHorarioRepository:
    def __init__(self, slots: list[HorarioDisponivel] | None = None):
        self._itens = list(slots or [])

    def buscar_por_id(self, id_):
        return next((s for s in self._itens if s.id == id_), None)

    buscar_para_reserva = buscar_por_id

    def buscar_slot(self, medico_id, data, horario):
        return next(
            (
                s
                for s in self._itens
                if s.medico_id == medico_id and s.data == data and s.horario == horario
            ),
            None,
        )

    def listar_livres(self, medico_id, data):
        return [
            s for s in self._itens if s.medico_id == medico_id and s.data == data and s.disponivel
        ]

    def salvar(self, entidade):
        if entidade not in self._itens:
            entidade.id = len(self._itens) + 1
            self._itens.append(entidade)
        return entidade


class FakeMedicoRepository:
    def __init__(self, medicos: list[Medico] | None = None):
        self._itens = list(medicos or [])

    def buscar_por_id(self, id_):
        return next((m for m in self._itens if m.id == id_), None)


class FakeConsultaRepository:
    def __init__(self, consultas: list[Consulta] | None = None):
        self._itens = list(consultas or [])

    def buscar_por_id(self, id_):
        return next((c for c in self._itens if c.id == id_), None)

    def existe_ativa_no_slot(self, horario_disponivel_id):
        return any(
            c.horario_disponivel_id == horario_disponivel_id and c.status in STATUS_QUE_OCUPAM_SLOT
            for c in self._itens
        )

    def listar_por_paciente(self, paciente_id):
        return [c for c in self._itens if c.paciente_id == paciente_id]

    def salvar(self, entidade):
        if entidade not in self._itens:
            entidade.id = len(self._itens) + 1
            self._itens.append(entidade)
        return entidade


@pytest.fixture
def medico() -> Medico:
    return Medico(
        id=1,
        nome="Dr. Silva",
        email="silva@clinica.com",
        crm="CRM123",
        especialidade_id=1,
    )


@pytest.fixture
def slot_livre() -> HorarioDisponivel:
    slot = HorarioDisponivel(
        id=1, medico_id=1, data=date(2026, 8, 12), horario=time(14, 0), disponivel=True
    )
    return slot


def montar_consulta(slot: HorarioDisponivel, status=StatusConsulta.CONFIRMADA) -> Consulta:
    consulta = Consulta(
        id=1,
        paciente_id=1,
        medico_id=slot.medico_id,
        horario_disponivel_id=slot.id,
        status=status,
    )
    consulta.horario = slot
    return consulta
