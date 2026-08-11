"""Fixtures compartilhadas.

Os testes unitarios usam FAKES de repositorio (nao mocks cegos) - possivel porque
os Services dependem da abstracao Repository (ADR-006 / DIP do SOLID). Nenhum
teste unitario precisa de banco, o que os deixa rapidos e deterministicos.
"""

from datetime import date, time

import pytest

from app.models.consulta import Consulta
from app.models.enums import STATUS_QUE_OCUPAM_SLOT, StatusConsulta
from app.models.especialidade import Especialidade
from app.models.horario_disponivel import HorarioDisponivel
from app.models.medico import Medico
from app.models.paciente import Paciente


def montar_medico(ativo: bool = True, especialidade_ativa: bool = True) -> Medico:
    """Medico completo para os fakes.

    `ativo` e `especialidade.ativo` sao explicitos porque o default da coluna so e
    aplicado no flush: fora do banco ficariam None, que a RN16/RN17 leriam como
    indisponivel e mascarariam o teste.
    """
    medico = Medico(
        id=1,
        nome="Dr. Silva",
        email="silva@clinica.com",
        crm="CRM123",
        especialidade_id=1,
        ativo=ativo,
    )
    medico.especialidade = Especialidade(id=1, nome="Cardiologia", ativo=especialidade_ativa)
    return medico


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

    def listar_ativos(self, especialidade_id=None, apenas_ativos=None):
        return [
            m
            for m in self._itens
            if (apenas_ativos is None or m.ativo is apenas_ativos)
            and (especialidade_id is None or m.especialidade_id == especialidade_id)
        ]

    def listar_agendaveis(self, especialidade_id=None):
        """RN16 + RN17 - espelha o JOIN do repositorio real."""
        return [
            m
            for m in self._itens
            if m.ativo
            and m.especialidade.ativo
            and (especialidade_id is None or m.especialidade_id == especialidade_id)
        ]


class FakeConsultaRepository:
    def __init__(self, consultas: list[Consulta] | None = None):
        self._itens = list(consultas or [])
        self.ids_travados: list[int] = []

    def buscar_por_id(self, id_):
        return next((c for c in self._itens if c.id == id_), None)

    def buscar_para_atualizar(self, id_):
        """Espelha o SELECT ... FOR UPDATE do repositorio real.

        O fake nao tem banco para travar, entao registra o id em `ids_travados`:
        e assim que o teste verifica que o caminho de escrita pediu a leitura travada.
        """
        self.ids_travados.append(id_)
        return self.buscar_por_id(id_)

    def existe_ativa_no_slot(self, horario_disponivel_id):
        return any(
            c.horario_disponivel_id == horario_disponivel_id and c.status in STATUS_QUE_OCUPAM_SLOT
            for c in self._itens
        )

    def listar_por_paciente(self, paciente_id, agora=None):  # noqa: ARG002
        return [c for c in self._itens if c.paciente_id == paciente_id]

    def salvar(self, entidade):
        if entidade not in self._itens:
            entidade.id = len(self._itens) + 1
            self._itens.append(entidade)
        return entidade


@pytest.fixture
def medico() -> Medico:
    return montar_medico()


@pytest.fixture
def slot_livre() -> HorarioDisponivel:
    slot = HorarioDisponivel(
        id=1, medico_id=1, data=date(2026, 8, 12), horario=time(14, 0), disponivel=True
    )
    # RN16 / RN17 - o service consulta `slot.medico` e a especialidade dele antes de reservar.
    slot.medico = montar_medico()
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
