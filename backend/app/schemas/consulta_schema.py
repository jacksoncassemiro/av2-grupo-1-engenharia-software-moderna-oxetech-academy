from datetime import date, datetime, time
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from app.exceptions.dominio import CancelamentoNaoPermitido
from app.models.enums import STATUS_QUE_OCUPAM_SLOT, StatusConsulta
from app.services.cancelamento_strategy import CancelamentoPorPaciente

if TYPE_CHECKING:
    from app.models.consulta import Consulta


class ConsultaSolicitar(BaseModel):
    """US-08 - paciente escolhe um slot livre."""

    horario_disponivel_id: int


class ConsultaAgendarPorAtendente(ConsultaSolicitar):
    """US-09 - atendente agenda para um paciente."""

    paciente_id: int


class ConsultaCancelar(BaseModel):
    motivo: str | None = Field(default=None, max_length=500)


class ConsultaMudarStatus(BaseModel):
    """US-13 - CONFIRMADA ou FINALIZADA."""

    status: StatusConsulta


def _pode_cancelar(consulta: "Consulta", agora: datetime, antecedencia_horas: int) -> bool:
    if consulta.status not in STATUS_QUE_OCUPAM_SLOT:
        return False
    try:
        CancelamentoPorPaciente(antecedencia_horas).validar(consulta, agora)
        return True
    except CancelamentoNaoPermitido:
        return False


class ConsultaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
    paciente_nome: str
    medico_id: int
    medico_nome: str
    especialidade_nome: str
    horario_disponivel_id: int
    data: date
    horario: time
    status: StatusConsulta
    data_agendamento: datetime
    motivo_cancelamento: str | None
    pode_cancelar: bool

    @classmethod
    def de_consulta(
        cls, consulta: "Consulta", agora: datetime, antecedencia_horas: int
    ) -> "ConsultaResposta":
        slot = consulta.horario
        medico = slot.medico
        return cls(
            id=consulta.id,
            paciente_id=consulta.paciente_id,
            paciente_nome=consulta.paciente.nome,
            medico_id=consulta.medico_id,
            medico_nome=medico.nome,
            especialidade_nome=medico.especialidade.nome,
            horario_disponivel_id=consulta.horario_disponivel_id,
            data=slot.data,
            horario=slot.horario,
            status=consulta.status,
            data_agendamento=consulta.data_agendamento,
            motivo_cancelamento=consulta.motivo_cancelamento,
            pode_cancelar=_pode_cancelar(consulta, agora, antecedencia_horas),
        )
